# Android Device Testing Framework ("dtf")
# Copyright 2013-2015 Jake Valletta (@jake_valletta)
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
"""Built-in module for client on device """

from dtf.module import Module

from dtf.adb import DtfAdb
from dtf.client import (DtfClient, RESP_OK, RESP_NO_READ, RESP_ERROR,
                        RESP_NO_WRITE, RESP_EXISTS, RESP_NO_EXIST,
                        ERR_SOCK)

import dtf.logging as log
import dtf.properties as prop
import dtf.core.utils as utils

from dtf.constants import DTF_CLIENT
from argparse import ArgumentParser

import os.path

DTF_CLIENT_PATH = ("%s/included/dtfClient/com.dtf.client-1.3-1.apk" %
                   utils.get_pydtf_dir())

DEFAULT_UPLOAD_PATH = '/data/data/com.dtf.client'

class client(Module):

    """Module class for dtf client"""

    adb = DtfAdb()
    client = DtfClient()

    @classmethod
    def usage(cls):

        """Display module usage"""

        print "dtf Client Manager"
        print "Subcommands:"
        print "    download   Download a file using dtfClient."
        print "    execute    Execute a command using dtfClient."
        print "    install    Install the dtf client on device."
        print "    status     Print the install status of the client."
        print "    remove     Uninstall the dtf client."
        print "    restart    Restart dtfClient's socket service."
        print "    upload     Upload file using dtfClient."
        print ""

        return 0

    def do_install(self):

        """Install the dtf client on device"""

        log.i(self.name, "Waiting for device to be connected...")
        self.adb.wait_for_device()

        log.i(self.name, "Removing old client if it exists...")
        self.adb.uninstall(DTF_CLIENT)

        log.i(self.name, "Installing dtf client...")

        self.adb.install(DTF_CLIENT_PATH)

        cmd = "am startservice -a com.dtf.action.name.INITIALIZE"
        self.adb.shell_command(cmd)

        busybox_path = "/data/data/%s/files/busybox" % DTF_CLIENT
        prop.set_prop('Info', 'busybox', busybox_path)

        log.i(self.name, "dtf client installed.")

        return 0

    def do_status(self):

        """Print the install status of the client"""

        if self.adb.is_installed(DTF_CLIENT):
            print "dtf Client Status: Installed"
            print ""

        else:
            print "dtf Client Status: Not Installed"
            print ""

    def do_remove(self):

        """Uninstall the dtf client"""

        log.i(self.name, "Waiting for device to be connected...")
        self.adb.wait_for_device()

        log.i(self.name, "Removing dtf client...")
        self.adb.uninstall(DTF_CLIENT)

        prop.del_prop('Info', 'busybox')

        log.i(self.name, "dtf client removed!")

        return 0

    def do_upload(self, args):

        """Upload file to dtf client directory"""

        parser = ArgumentParser(prog='client upload',
                                description='Upload file to device with dtfClient.')
        parser.add_argument('--path', dest='upload_path',
                            default=None, help="Specify a upload point.")
        parser.add_argument('file_name', type=str,
                            help='The file to upload.')

        args = parser.parse_args(args)

        file_name = args.file_name

        if args.upload_path is None:
            upload_file_name = os.path.basename(file_name)
            upload_path = "%s/%s" % (DEFAULT_UPLOAD_PATH, upload_file_name)
        else:
            upload_path = args.upload_path

        if not os.path.isfile(file_name):
            log.e(self.name, "File does not exist: %s" % file_name)
            return -1

        log.i(self.name, "Waiting for device to be connected...")
        self.adb.wait_for_device()
        log.i(self.name, "Device connected!")

        # Is client installed?
        if not self.adb.is_installed(DTF_CLIENT):
            log.e(self.name, "dtf Client is not installed!")
            return -1

        resp = self.client.upload_file(file_name, upload_path)

        if resp == RESP_OK:
            log.i(self.name, "File upload success!")
            return 0
        elif resp == RESP_ERROR:
            log.e(self.name, "General error!")
            return -1
        elif resp == RESP_EXISTS:
            log.e(self.name, "Remote file exist!")
            return -1
        elif resp == RESP_NO_WRITE:
            log.e(self.name, "No write permissions!")
            return -1
        elif resp == ERR_SOCK:
            log.e(self.name, "Socket error!")
            return -1
        else:
            log.e(self.name, "Unknown response, cannot proceed.")
            return -1

        return 0

    def do_download(self, args):

        """Download a file using the dtfClient API"""

        parser = ArgumentParser(prog='client download',
                                description='Download file from device with dtfClient.')
        parser.add_argument('--path', dest='download_path',
                            default=None, help="Specify local path.")
        parser.add_argument('file_name', type=str,
                            help='The file to download.')

        args = parser.parse_args(args)
        file_name = args.file_name

        if args.download_path is None:
            local_path = os.path.basename(file_name)
        else:
            local_path = args.download_path

        if os.path.isfile(local_path):
            log.e(self.name, "Local file '%s' already exists!" % local_path)
            return -1

        log.i(self.name, "Waiting for connected device...")
        self.adb.wait_for_device()
        log.i(self.name, "Device connected!")

        # Is client installed?
        if not self.adb.is_installed(DTF_CLIENT):
            log.e(self.name, "dtf Client is not installed!")
            return -1

        resp = self.client.download_file(file_name, local_path)

        if resp == RESP_OK:
            log.i(self.name, "File download success!")
            return 0
        elif resp == RESP_ERROR:
            log.e(self.name, "General error!")
            return -1
        elif resp == RESP_NO_EXIST:
            log.e(self.name, "Remote file doesnt exist!")
            return -1
        elif resp == RESP_NO_READ:
            log.e(self.name, "No read permissions!")
            return -1
        elif resp == ERR_SOCK:
            log.e(self.name, "Socket error!")
            return -1
        else:
            log.e(self.name, "Unknown response, cannot proceed.")
            return -1

    def do_restart(self):

        """Restart the socket service on the dtfClient"""

        log.i(self.name, "Waiting for device to be connected...")
        self.adb.wait_for_device()
        log.i(self.name, "Connected!")

        cmd = "am startservice -a com.dtf.action.name.RESTART_SOCKET"
        self.adb.shell_command(cmd)

        return 0

    def do_execute(self, args):

        """Execute a command using the dtfClient"""

        if len(args) != 1:
            print "Usage:"
            print "dtf client execute [command]"
            return -1

        command_string = args.pop()

        log.i(self.name, "Waiting for connected device...")
        self.adb.wait_for_device()
        log.i(self.name, "Device connected!")

        # Is client installed?
        if not self.adb.is_installed(DTF_CLIENT):
            log.e(self.name, "dtf Client is not installed!")
            return -1

        response, resp_code = self.client.execute_command(command_string)

        if resp_code == RESP_OK:
            print response
            return 0
        elif resp_code == ERR_SOCK:
            log.e(self.name, "Socket error!")
            return -1
        else:
            log.e(self.name, "Something went wrong with running the command: %s"
                  % resp_code)
            return -1

    def execute(self, args):

        """Main module executor"""

        self.name = self.__self__

        rtn = 0

        if len(args) < 1:
            return self.usage()

        sub_cmd = args.pop(0)

        if sub_cmd == 'install':
            rtn = self.do_install()

        elif sub_cmd == 'status':
            rtn = self.do_status()

        elif sub_cmd == 'remove':
            rtn = self.do_remove()

        elif sub_cmd == 'upload':
            rtn = self.do_upload(args)

        elif sub_cmd == 'download':
            rtn = self.do_download(args)

        elif sub_cmd == 'restart':
            rtn = self.do_restart()

        elif sub_cmd == 'execute':
            rtn = self.do_execute(args)

        else:
            print "Sub-command '%s' not found!" % sub_cmd
            rtn = self.usage()

        return rtn
