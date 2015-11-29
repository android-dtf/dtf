package com.dtf.client;

import android.app.IntentService;
import android.content.Intent;
import android.util.Log;

import java.io.BufferedInputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;


public class HelperService extends IntentService {

    private static final String ACTION_COPY_TO_SDCARD = "com.dtf.action.name.COPY_TO_SDCARD";
    private static final String COPY_FILENAME = "filename";
    private static final String TAG = "DtfHelperService";

    public HelperService() {
        super("HelperService");
    }

    @Override
    protected void onHandleIntent(Intent intent) {
        if (intent != null) {
            final String action = intent.getAction();

            if (ACTION_COPY_TO_SDCARD.equals(action)) {
                final String file_name = intent.getStringExtra(COPY_FILENAME);
                handleActionCopyToSdCard(file_name);
            }
        }
    }

    private void handleActionCopyToSdCard(String file_name) {

        if (file_name == null) {
            Log.e(TAG, "File name cannot be null!");
            return;
        }

        Log.d(TAG, "Copying file '"+file_name+"' to SDCard...");
        copyToSdCard(file_name);
    }

    private void copyToSdCard(String file_name) {

        InputStream in = null;
        OutputStream out = null;
        try {
            in = new BufferedInputStream(new FileInputStream(
                    new File("/data/data/com.dtf.client/"+file_name)));

            File outFile = new File("/mnt/sdcard/"+file_name);
            out = new FileOutputStream(outFile);
            copyFile(in, out);
        } catch(IOException e) {
            Log.e(TAG, "Failed to copy file: " + file_name, e);
        }
        finally {
            if (in != null) {
                try {
                    in.close();
                } catch (IOException e) {
                }
            }
            if (out != null) {
                try {
                    out.close();
                } catch (IOException e) {
                }
            }
        }
    }

    private void copyFile(InputStream in, OutputStream out) throws IOException {
        byte[] buffer = new byte[1024];
        int read;
        while((read = in.read(buffer)) != -1){
            out.write(buffer, 0, read);
        }
    }
}
