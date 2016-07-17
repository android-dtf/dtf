package com.dtf.client;

import android.app.Service;
import android.content.Intent;
import android.net.Credentials;
import android.net.LocalServerSocket;
import android.net.LocalSocket;
import android.net.LocalSocketAddress;
import android.os.IBinder;
import android.util.Log;
import java.io.ByteArrayInputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.nio.ByteBuffer;

public class SocketService
        extends Service {

    public static boolean isRunning = false;
    private static final String SOCKET_ADDRESS = "dtf_socket";
    private static final String TAG = "SocketService";

    private static final int UID_ROOT = 0;
    private static final int UID_SHELL = 2000;
    private static final int GID_SHELL = 2000;

    private static final char CMD_DOWNLOAD = 'd';
    private static final char CMD_UPLOAD = 'u';
    private static final char CMD_EXECUTE = 'e';

    private static final int RESP_OK = 0;
    private static final int RESP_ERROR = 1;
    private static final int RESP_NO_EXIST = -1;
    private static final int RESP_NO_READ = -2;
    private static final int RESP_EXISTS = -3;
    private static final int RESP_NO_WRITE = -4;

    private static final int SIZE_LONG = Long.SIZE / Byte.SIZE;
    private static final int SIZE_INTEGER = Integer.SIZE / Byte.SIZE;

    private static final int READ_SIZE_FILENAME = 256;
    private static final int READ_SIZE_CMD = 512;
    private static final int READ_SIZE_TRANSFER = 1024;

    SocketListener socketListener;
    LocalServerSocket socket;

    public int onStartCommand(Intent intent, int flags, int startId) {

        Log.d(TAG, "Starting dtfClient socket");
        isRunning = true;

        this.socketListener = new SocketListener();
        this.socketListener.start();

        return 0;
    }

    public void onDestroy() {

        Log.d(TAG, "Stopping the dtfClient socket");
        isRunning = false;

        try {

            this.socket.close();
            /* This will cause the permission checks to fail, breaking us out of the loop */
            new LocalSocket().connect(new LocalSocketAddress(SOCKET_ADDRESS));

        } catch (IOException e) {
            e.printStackTrace();
        }

        super.onDestroy();
    }

    public IBinder onBind(Intent intent) {

        return null;
    }

    class SocketListener
            extends Thread {

        public SocketListener() {}

        public void run() {

            try {
                SocketService.this.socket = new LocalServerSocket(SOCKET_ADDRESS);

                while (SocketService.isRunning) {

                    LocalSocket receiver = SocketService.this.socket.accept();

                    if (receiver != null) {

                        InputStream input = receiver.getInputStream();
                        OutputStream output = receiver.getOutputStream();
                        Credentials peerCredentials = receiver.getPeerCredentials();

                        if (!checkPermissions(peerCredentials)) {

                            Log.w(TAG, "Unauthenticated attempt to access dtfClient socket!");
                            receiver.close();
                        }
                        else {

                            Log.i(TAG, "New dtfClient connection!");

                            int mode = input.read();
                            switch ((char)mode) {

                                case CMD_DOWNLOAD:
                                    Log.d(TAG, "Download invoked!");
                                    output.write(RESP_OK);

                                    doDownloadFile(input, output);
                                    break;
                                case CMD_UPLOAD:
                                    Log.d(TAG, "Upload invoked!");
                                    output.write(RESP_OK);

                                    doUploadFile(input, output);
                                    break;
                                case CMD_EXECUTE:
                                    Log.d(TAG, "Execute invoked!");
                                    output.write(RESP_OK);

                                    doExecuteCommand(input, output);
                                    break;
                                default:
                                    Log.e(TAG, "Unknown command!");
                                    output.write(RESP_ERROR);
                            }
                            Log.d(TAG, "Closing connection with client.");
                            receiver.close();
                        }
                    }
                }
            }
            catch (IOException e) {

                Log.e(TAG, "Unable to start UNIX socket: " + e.getMessage());
            }

            Log.d(TAG, "Socket thread is exiting");
        }

        private boolean checkPermissions(Credentials peerCredentials) {

            int uid = peerCredentials.getUid();
            int gid = peerCredentials.getGid();

            // Explicitly trust root
            if (uid == UID_ROOT) {
                return true;
            }
            // Shell user is trusted
            else if ((uid == UID_SHELL) && (gid == GID_SHELL)) {
                return true;
            }
            else {
                return false;
            }

        }

        private String readChunk(int chunk_size, InputStream input)
        {
            int i = 0;

            try {
                byte[] bytes = new byte[chunk_size];
                while (i < chunk_size)
                {
                    int readed = input.read();
                    bytes[i] = ((byte)readed);
                    i++;
                }
                return new String(bytes, 0, chunk_size);
            }
            catch (IOException e) {
                e.printStackTrace();
            }

            return null;
        }

        private byte[] readRawChunk(int chunk_size, InputStream input) {

            int i = 0;

            try {

                byte[] bytes = new byte[chunk_size];
                while (i < chunk_size) {
                    int readed = input.read();
                    bytes[i] = ((byte)readed);
                    i++;
                }

                return bytes;
            }

            catch (IOException e) {
                e.printStackTrace();
            }

            return null;
        }

        private long readLong(InputStream input) {

            int i = 0;

            try {

                byte[] bytes = new byte[SIZE_LONG];

                while (i < SIZE_LONG) {

                    int readed = input.read();
                    bytes[i] = ((byte)readed);
                    i++;
                }
                return SocketService.this.bytesToLong(bytes);
            }
            catch (IOException e) {
                e.printStackTrace();
            }

            return -1L;
        }

        private int sendFile(File file, long fileSize, OutputStream output) {

            long bytesLeft = fileSize;

            try {
                FileInputStream fis = new FileInputStream(file);
                while (true) {

                    if (bytesLeft <= READ_SIZE_TRANSFER) {

                        byte[] chunk = new byte[(int)bytesLeft];

                        fis.read(chunk);
                        output.write(chunk);

                        fis.close();
                        break;
                    }

                    byte[] chunk = new byte[READ_SIZE_TRANSFER];
                    fis.read(chunk);

                    output.write(chunk);
                    bytesLeft -= READ_SIZE_TRANSFER;
                }
            }
            catch (FileNotFoundException e) {
                Log.e(TAG, "FileNotFoundException reading file?");
                return RESP_NO_EXIST;
            }
            catch (IOException e) {

                Log.e(TAG, "IOException reading file?");
                return RESP_ERROR;
            }

            return RESP_OK;
        }

        private int receiveFile(File file, long fileSize, InputStream input) {

            long bytesLeft = fileSize;

            try {
                FileOutputStream fos = new FileOutputStream(file);

                while (true) {

                    if (bytesLeft <= READ_SIZE_TRANSFER) {

                        byte[] chunk = readRawChunk((int) bytesLeft, input);

                        fos.write(chunk);
                        fos.close();
                        break;
                    }

                    byte[] chunk = readRawChunk(READ_SIZE_TRANSFER, input);
                    fos.write(chunk);
                    bytesLeft -= READ_SIZE_TRANSFER;
                }
            }
            catch (FileNotFoundException e) {

                Log.e(TAG, "FileNotFoundException reading file?");
                return RESP_NO_EXIST;
            }
            catch (IOException e) {

                Log.e(TAG, "IOException reading file?");
                return RESP_ERROR;
            }

            return RESP_OK;
        }

        private int sendOutput(String response, int responseLength, OutputStream output) {

            int bytesLeft = responseLength;

            try {

                InputStream is = new ByteArrayInputStream(response.getBytes());
                while (true) {

                    if (bytesLeft <= READ_SIZE_TRANSFER)
                    {
                        byte[] chunk = new byte[bytesLeft];
                        is.read(chunk);

                        output.write(chunk);
                        break;
                    }
                    else {

                        byte[] chunk = new byte[READ_SIZE_TRANSFER];
                        is.read(chunk);

                        output.write(chunk);
                        bytesLeft -= READ_SIZE_TRANSFER;
                    }
                }
            }
            catch (IOException e) {

                Log.e(TAG, "IOException reading file?");
                return RESP_ERROR;
            }

            return RESP_OK;
        }

        private void doDownloadFile(InputStream input, OutputStream output) {

            try {

                String filenameRaw = readChunk(READ_SIZE_FILENAME, input);

                if (filenameRaw == null) {

                    Log.e(TAG, "Unable to read filename!");
                    output.write(RESP_ERROR);
                    return;
                }

                String filename = filenameRaw.replaceAll("\000", "");
                Log.d(TAG, "Request to download: " + filename);

                File file = new File(filename);

                if (!file.exists()) {

                    Log.e(TAG, "File doesn't exist!");
                    output.write(RESP_NO_EXIST);
                    return;
                }

                if (!file.canRead()) {

                    Log.e(TAG, "No read permissions!");
                    output.write(RESP_NO_READ);
                    return;
                }

                long fileSize = file.length();

                Log.d(TAG, "File Size: " + fileSize);

                output.write(SocketService.this.longToBytes(fileSize));

                int ready = input.read();
                if ((char)ready == RESP_OK) {

                    Log.d(TAG, "Client is ready to receive file!");
                    sendFile(file, fileSize, output);

                    int response = input.read();
                    if ((char)response == RESP_OK) {

                        Log.d(TAG, "Transfer completed successfully!");
                    } else {

                        Log.e(TAG, "Something was wrong transferring!");
                    }
                }
                else {
                    Log.e(TAG, "Client is not willing to receive file!");
                }
            }
            catch (IOException e) {
                Log.e(TAG, "IOException handling download file!!!");
            }
        }

        private void doUploadFile(InputStream input, OutputStream output) {

            try {

                long fileSize = readLong(input);

                if (fileSize < 0) {

                    Log.e(TAG, "Unable to read filesize!");
                    output.write(RESP_ERROR);
                    return;
                }

                Log.d(TAG, "File Size: " + fileSize);

                output.write(RESP_OK);

                String filenameRaw = readChunk(READ_SIZE_FILENAME, input);
                if (filenameRaw == null) {

                    Log.e(TAG, "Unable to read filename!");
                    output.write(RESP_ERROR);
                    return;
                }

                String filename = filenameRaw.replaceAll("\000", "");
                Log.d(TAG, "Request to upload: " + filename);

                File file = new File(filename);
                if (file.exists()) {

                    Log.e(TAG, "File already exist!");
                    output.write(RESP_EXISTS);
                    return;
                }

                if (!new File(file.getParent()).canWrite()) {

                    Log.e(TAG, "No write permissions!");
                    output.write(RESP_NO_WRITE);
                    return;
                }

                Log.d(TAG, "Ready to receive file!");
                output.write(RESP_OK);

                int response = receiveFile(file, fileSize, input);
                if (response != RESP_OK) {

                    Log.e(TAG, "Error receiving file!");
                    output.write(response);
                    return;
                }

                Log.d(TAG, "Successfully uploaded file!");
                output.write(response);
            }
            catch (IOException e) {

                Log.e(TAG, "IOException handling download file!!!");
            }
        }

        private void doExecuteCommand(InputStream input, OutputStream output) {

            try {

                String commandStringRaw = readChunk(READ_SIZE_CMD, input);
                if (commandStringRaw == null) {

                    Log.e(TAG, "Unable to read command!");
                    output.write(RESP_ERROR);
                    return;
                }

                String commandString = commandStringRaw.replaceAll("\000", "");
                Log.d(TAG, "Request execute: " + commandString);

                Log.d(TAG, "Ready Execute command.");

                ShellExecutor se = new ShellExecutor();
                String commandResponse = se.execute(commandString);

                int responseLength = commandResponse.length();
                Log.d(TAG, "Length of the output: " + responseLength);

                output.write(SocketService.this.intToBytes(responseLength));

                int readed = input.read();
                if ((char)readed != RESP_OK) {

                    Log.e(TAG, "Client doesn't want the output!");
                    return;
                }
                if (responseLength == 0) {

                    Log.d(TAG, "No response to send, returning!");
                    return;
                }
                sendOutput(commandResponse, responseLength, output);

                int response = input.read();
                if ((char)response == RESP_OK) {

                    Log.d(TAG, "Output sent successfully!");
                } else {

                    Log.e(TAG, "Something was wrong transferring!");
                }
            }
            catch (IOException e) {
                Log.e(TAG, "IOException executing command");
            }
        }
    }

    public byte[] longToBytes(long x) {

        ByteBuffer buffer = ByteBuffer.allocate(SIZE_LONG);
        buffer.putLong(x);
        return buffer.array();
    }

    public long bytesToLong(byte[] bytes) {

        ByteBuffer buffer = ByteBuffer.allocate(SIZE_LONG);
        buffer.put(bytes);
        buffer.flip();
        return buffer.getLong();
    }

    public byte[] intToBytes(int x) {

        ByteBuffer buffer = ByteBuffer.allocate(SIZE_INTEGER);
        buffer.putInt(x);
        return buffer.array();
    }
}
