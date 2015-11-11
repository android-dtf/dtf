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

import dtf.adb as DtfAdb
import dtf.logging as log
import dtf.properties as prop
import dtf.core.utils as utils

from dtf.constants import DTF_CLIENT
from argparse import ArgumentParser
from os.path import isfile

DTF_CLIENT_PATH = ("%s/included/dtfClient/com.dtf.client-1.1.apk" %
                                                utils.get_pydtf_dir())

DEFAULT_PATH = '/mnt/sdcard'

class client(Module):

    """Module class for dtf client"""

    adb = DtfAdb.DtfAdb()

    @classmethod
    def usage(cls):

        """Display module usage"""

        print "dtf Client Manager"
        print "Subcommands:"
        print "    install    Install the dtf client on device."
        print "    status     Print the install status of the client."
        print "    remove     Uninstall the dtf client."
        print "    upload     Upload file to dtf client directory."
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
                        description='Upload file to device.')
        parser.add_argument('--path', metavar="val", dest='upload_path',
                        default=DEFAULT_PATH, help="Specify a upload point.")
        parser.add_argument('file_name', type=str,
                         help='The file to upload.')

        args = parser.parse_args(args)

        file_name = args.file_name
        upload_path = args.upload_path

        if not isfile(file_name):
            log.e(self.name, "File does not exist: %s" % file_name)
            return -1

        log.i(self.name, "Waiting for device to be connected...")
        self.adb.wait_for_device()

        # Is client installed?
        if not self.adb.is_installed(DTF_CLIENT):
            log.e(self.name, "dtf Client is not installed!")
            return -1

        self.adb.push(file_name, upload_path)

        upload_file_name = "%s/%s" % (upload_path, file_name)
        dtf_upload_path = "/data/data/%s/" % DTF_CLIENT

        cmd = ("run-as %s cp %s %s" %
                (DTF_CLIENT, upload_file_name, dtf_upload_path))

        self.adb.shell_command(cmd)

        return 0

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

        else:
            print "Sub-command '%s' not found!" % sub_cmd
            rtn = self.usage()

        return rtn
