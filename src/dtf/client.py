# Android Device Testing Framework ("dtf")
# Copyright 2013-2016 Jake Valletta (@jake_valletta)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
"""API for interacting with dtfClient application"""

from dtf.adb import DtfAdb
import dtf.logging as log

import struct
import socket
import os


CMD_DOWNLOAD = 'd'
CMD_UPLOAD = 'u'
CMD_EXECUTE = 'e'

RESP_OK = chr(0)
RESP_ERROR = chr(1)
RESP_NO_EXIST = chr(-1 % 256)
RESP_NO_READ = chr(-2 % 256)
RESP_EXISTS = chr(-3 % 256)
RESP_NO_WRITE = chr(-4 % 256)

SIZE_LONG = 8
SIZE_INTEGER = 4

SIZE_FILENAME = 256
SIZE_CMD = 512
SIZE_TRANSFER = 1024

TAG = "dtfClient"

DTF_SOCKET = "\0dtf_socket"

FORWARD_SOCKET = "localabstract:dtf_socket"

def bytes_to_int(byte_stream):

    """Convert bytes to integer"""

    return struct.unpack(">L", byte_stream)[0]

def bytes_to_long(byte_stream):

    """Convert bytes to long"""

    return struct.unpack(">Q", byte_stream)[0]

def long_to_bytes(long_in):

    """Convert a long into byte stream"""

    return struct.pack(">Q", long_in)

class DtfClient(object):

    """Python class for dtfClient"""

    serial = ''
    stdout = None
    stderr = None
    adb = None


    def __init__(self):

        """Object initialization"""

        self.adb = DtfAdb()

    def __enable_forward(self):

        """Setup forwarding for talking to dtfClient"""

        self.adb.add_forward(FORWARD_SOCKET, FORWARD_SOCKET)

    def __disable_forward(self):

        """Remove forwarding rule"""

        self.adb.remove_forward(FORWARD_SOCKET)

    @classmethod
    def __do_download(cls, remote_file_name, local_file_name):

        """Download a file using the dtfClient"""

        # Create an unbound and not-connected socket.
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

        log.d(TAG, "Connecting to socket...")
        sock.connect(DTF_SOCKET)
        log.d(TAG, "Connected!")

        sock.send(CMD_DOWNLOAD)

        resp_code = sock.recv(1)
        if resp_code != RESP_OK:
            log.e(TAG, "Server rejected download request!")
            return resp_code

        padded_file_name = remote_file_name.ljust(SIZE_FILENAME, '\0')

        log.d(TAG, "Sending filename to server")
        sock.send(padded_file_name)
        log.d(TAG, "Filename sent.")

        binary_file_size = sock.recv(SIZE_LONG)

        # This is an error
        if len(binary_file_size) == 1:
            return binary_file_size

        long_file_size = bytes_to_long(binary_file_size)

        log.d(TAG, "File size from server: %d" % long_file_size)

        sock.send(RESP_OK)

        local_f = file(local_file_name, 'wb')

        bytes_left = long_file_size

        while True:

            if bytes_left <= SIZE_TRANSFER:
                local_buf = sock.recv(bytes_left)

                local_f.write(local_buf)
                local_f.close()
                break
            else:
                local_buf = sock.recv(SIZE_TRANSFER)
                local_f.write(local_buf)

                bytes_left -= SIZE_TRANSFER

        sock.send(RESP_OK)
        log.d(TAG, "Transfer complete!")

        return 0

    @classmethod
    def __do_upload(cls, local_file_name, remote_file_name):

        """Do file upload"""

        # Create an unbound and not-connected socket.
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

        statinfo = os.stat(local_file_name)
        file_size = statinfo.st_size

        local_f = open(local_file_name, 'rb')

        log.d(TAG, "Connecting to socket...")
        sock.connect(DTF_SOCKET)
        log.d(TAG, "Connected!")

        sock.send(CMD_UPLOAD)

        resp_code = sock.recv(1)
        if resp_code != RESP_OK:
            log.e(TAG, "Server rejected upload request!")
            return resp_code

        log.d(TAG, "Sending filesize to server")
        sock.send(long_to_bytes(file_size))

        resp = sock.recv(1)
        if resp != RESP_OK:
            log.e(TAG, "Error submitting filesize!")
            return resp

        padded_file_name = remote_file_name.ljust(SIZE_FILENAME, '\0')

        log.d(TAG, "Sending the filename...")
        sock.send(padded_file_name)

        resp = sock.recv(1)

        if resp != RESP_OK:
            log.e(TAG, "Error with filename!")
            return resp

        bytes_left = file_size
        while True:

            if bytes_left <= SIZE_TRANSFER:
                sock.send(local_f.read(bytes_left))
                local_f.close()
                break
            else:
                sock.send(local_f.read(SIZE_TRANSFER))
                bytes_left -= SIZE_TRANSFER

        resp = sock.recv(1)

        if resp != RESP_OK:
            log.e(TAG, "Error uploading file!")
            return resp

        return RESP_OK

    @classmethod
    def __do_execute(cls, command_string):

        """Do file execute"""

        response = None

        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

        log.d(TAG, "Connecting to socket...")
        sock.connect(DTF_SOCKET)
        log.d(TAG, "Connected!")

        sock.send(CMD_EXECUTE)

        resp_code = sock.recv(1)
        if resp_code != RESP_OK:
            log.e(TAG, "Server rejected execute request!")
            return (response, resp_code)

        full_command = command_string.ljust(SIZE_CMD, '\0')

        log.d(TAG, "Sending execute string to server")
        sock.send(full_command)
        log.d(TAG, "Command sent.")

        binary_cmd_size = sock.recv(SIZE_INTEGER)

        # This is an error.
        if len(binary_cmd_size) == 1:
            return (response, binary_cmd_size)

        int_cmd_size = bytes_to_int(binary_cmd_size)

        sock.send(RESP_OK)

        if int_cmd_size == 0:
            log.d(TAG, "Response is empty string!")
            return ("", RESP_OK)

        bytes_left = int_cmd_size
        response = ""

        while True:
            if bytes_left <= SIZE_TRANSFER:
                local_buf = sock.recv(bytes_left)

                response += local_buf
                break
            else:
                local_buf = sock.recv(SIZE_TRANSFER)
                response += local_buf

                bytes_left -= SIZE_TRANSFER

        sock.send(RESP_OK)
        log.d(TAG, "Command complete!")

        return (response, RESP_OK)

    # Public API Starts here
    def upload_file(self, local_file_name, remote_file):

        """Upload a file using the dtfClient"""

        self.__enable_forward()
        resp_code = self.__do_upload(local_file_name, remote_file)
        self.__disable_forward()

        return resp_code

    def download_file(self, remote_file_name, local_file):

        """Download a file using the dtfClient"""

        self.__enable_forward()
        resp_code = self.__do_download(remote_file_name, local_file)
        self.__disable_forward()

        return resp_code

    def execute_command(self, cmd_string):

        """Execute command using dtfClient"""

        if cmd_string == "":
            return None

        self.__enable_forward()
        output, resp_code = self.__do_execute(cmd_string)
        self.__disable_forward()

        return output, resp_code
    # End public API
