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
"""Built-in module for creating dtf project"""

from __future__ import absolute_import
from __future__ import print_function
import os
import os.path
import re
import signal
import time

from dtf.module import Module
from dtf.properties import set_prop
import dtf.adb as adb
import dtf.core.compat as compat
import dtf.core.utils as utils
import dtf.logging as log
import dtf.packages as pkg

TAG = 'init'

TYPE_DALVIK = 'Dalvik'
TYPE_ART = 'ART'

SEANDROID_UNKNOWN = "Unknown"
SEANDROID_PERMISSIVE = "Permissive"
SEANDROID_ENFORCING = "Enforcing"
SEANDROID_OFF = "Off"


def rmfile(file_name):

    """Delete a file (that may or may not exist)"""

    try:
        os.remove(file_name)
    except OSError:
        pass


def mkdir(dir_name):

    """Create a directory (that may or may not exist)"""

    try:
        os.mkdir(dir_name)
    except OSError:
        pass


def get_set_value(set_data, match_key):

    """Extract value from SET output"""

    for val in set_data:

        try:
            key, value = val.split('=', 1)
        except ValueError:
            continue

        if key == match_key:
            return value

    return None


class init(Module):  # pylint: disable=invalid-name

    """Module class for creating a dtf project"""

    adb = None

    # pylint: disable=unused-argument
    @classmethod
    def do_shutdown(cls, signum, frame):

        """Handle a Ctrl+C"""

        log.w(TAG, "Exiting dtf initialization!")
        rmfile(utils.CONFIG_FILE_NAME)
        rmfile(utils.LOG_FILE_NAME)

        exit(-4)

    def getprop(self, value):

        """Call `getprop`"""

        self.adb.shell_command("getprop %s" % value)
        return self.adb.get_output()[0]

    def determine_cpu_bits(self):

        """Determine if it is 32 or 64 bit"""

        arch = self.getprop('ro.product.cpu.abi')
        if arch is None:
            log.e(TAG, "Unable to determine processor architecture!")
            return None

        if arch.find('armeabi') != -1:
            return '32'
        elif re.search("arm.*64", arch):
            return '64'
        else:
            log.e(TAG, "Unsupported CPU architecture: %s" % arch)
            return None

    def determine_vm_type(self, sdk, cpu_bits):

        """Determine if we are Dalvik/ART"""

        # ART was introduced in KitKat, so if we are less, its Dalvik.
        if int(sdk) < 20:
            log.d(TAG, "Using Dalvik based on SDK")
            return TYPE_DALVIK

        # Check for single persist.sys.dalvik.vm.lib
        lib = self.getprop('persist.sys.dalvik.vm.lib')
        lib2 = self.getprop('persist.sys.dalvik.vm.lib.2')

        # None set, error
        if lib == '' and lib2 == '':
            log.e(TAG, "Unable to determine VM type!")
            return None

        # Both are set.
        elif lib != '' and lib2 != '':

            if cpu_bits == '64':
                arm_dir = '/system/framework/arm64'
            else:
                arm_dir = '/system/framework/arm'

            if self.adb.is_dir(arm_dir):
                log.d(TAG, "Using ART based ARM directory.")
                return TYPE_ART
            else:
                log.d(TAG, "Using Dalvik based on ARM directory.")
                return TYPE_DALVIK

        # One or the other is set.
        else:
            so_type = max([lib, lib2])
            if so_type == 'libart.so':
                log.d(TAG, "Using ART based on prop.")
                return TYPE_ART
            else:
                log.d(TAG, "Using Dalvik based on prop.")
                return TYPE_DALVIK

    def determine_seandroid_state(self):

        """Determine if SEAndroid is used"""

        self.adb.shell_command("getenforce")

        response = self.adb.get_output()[0].lower()

        if response.find("not found") != -1:
            return SEANDROID_OFF
        elif response == "permissive":
            return SEANDROID_PERMISSIVE
        elif response == "enforcing":
            return SEANDROID_ENFORCING
        else:
            log.w(TAG, "Unable to determine SEAndroid state!")
            return SEANDROID_UNKNOWN

    def generate_version_string(self):

        """Generate the version string to use"""

        brand = self.getprop('ro.product.brand')
        name = self.getprop('ro.product.name')
        version = self.getprop('ro.build.id')
        version_string = "%s-%s_%s" % (brand, name, version)

        print('dtf would like to use the following version string:')
        print("\n%s\n" % version_string)
        print("The version string is only used to identify this project.\n")

        res = compat.raw_input("Would you like to change it? [N/y] ").lower()

        if res == 'y':
            return compat.raw_input("Please enter a custom version string: ")
        else:
            return version_string

    @classmethod
    def make_project_directories(cls):

        """Create all directories associated with a dtf project"""

        mkdir(utils.REPORTS_DIRECTORY)
        mkdir(utils.DBS_DIRECTORY)
        mkdir(utils.LOCAL_MODULES_DIRECTORY)

        return 0

    def determine_device(self):

        """Determine which device to use"""

        devices = self.adb.get_devices()

        if len(devices) == 0:
            log.e(TAG, "No devices found, exiting.")
            return None

        elif len(devices) == 1:

            init_device = devices[0]
            serial = init_device['serial']

            res = compat.raw_input("Got serial '%s', is this correct? [Y/n] "
                                   % serial)
            if res.lower() == 'n':
                log.e(TAG, "Initialization aborted.")
                return None
        else:
            print('Found many devices. Please select from the following list:')

            i = 1
            for device in devices:
                print("#%d. %s (%s)" % (i, device['serial'], device['status']))
                i += 1

            res = compat.raw_input("\nWhich device #? ")

            try:
                int_res = int(res)
                init_device = devices[int_res - 1]
            except (ValueError, IndexError):
                log.e(TAG, "Invalid input!")
                return None

        return init_device

    def initialize_device(self, init_device):

        """Perform the actual initialization"""

        device_serial = init_device['serial']

        log.d(TAG, "Preparing device: %s" % device_serial)

        utils.touch(utils.CONFIG_FILE_NAME)

        set_prop('Info', 'serial', device_serial)

        # Set the client section.
        set_prop('Client', 'mode', adb.MODE_USB)

        # Since we have a serial now, lets create a new DtfAdb instance
        self.adb = adb.DtfAdb()

        # Kernel
        self.adb.shell_command('cat /proc/version')
        kernel = self.adb.get_output()[0]
        log.d(TAG, "Kernel version: %s" % kernel)
        set_prop('Info', 'kernel', kernel)

        # SDK
        sdk = self.getprop('ro.build.version.sdk')
        log.d(TAG, "Using SDK API %s" % sdk)
        set_prop('Info', 'SDK', sdk)

        self.adb.shell_command('set')
        set_output = self.adb.get_output()

        # $PATH
        path = get_set_value(set_output, 'PATH')
        if path is None:
            log.e(TAG, "Unable to get $PATH variable!")
            self.do_shutdown(None, None)
        log.d(TAG, "PATH : %s" % path)
        set_prop('Info', 'path', path)

        # $BOOTCLASSPTH
        bootclasspath = get_set_value(set_output, 'BOOTCLASSPATH')
        if bootclasspath is None:
            log.e(TAG, "Unable to get $BOOTCLASSPATH variable!")
            self.do_shutdown(None, None)
        log.d(TAG, "BOOTCLASSPATH : %s" % bootclasspath)
        set_prop('Info', 'bootclasspath-jars', bootclasspath)

        # Version string
        version_string = self.generate_version_string()

        log.d(TAG, "Using version string: %s" % version_string)
        set_prop('Info', 'version-string', version_string)

        # Determine CPU bitness
        cpu_bits = self.determine_cpu_bits()
        if cpu_bits is None:
            self.do_shutdown(None, None)

        log.d(TAG, "Using %s-bit CPU" % cpu_bits)
        set_prop('Info', 'cpu-bits', cpu_bits)

        # Set the VM type (Dalvik|Art)
        vm_type = self.determine_vm_type(sdk, cpu_bits)
        if vm_type is None:
            self.do_shutdown(None, None)

        log.d(TAG, "Determined runtime: %s" % vm_type)
        set_prop('Info', 'vmtype', vm_type)

        # Determine SEAndroid
        se_state = self.determine_seandroid_state()

        log.d(TAG, "Determine SEAndroid state: %s" % se_state)
        set_prop('Info', 'seandroid-state', se_state)

        # Setup the directory structure
        self.make_project_directories()

        # Set directory related properties
        set_prop('Local', 'reports-dir', utils.REPORTS_DIRECTORY)
        set_prop('Local', 'db-dir', utils.DBS_DIRECTORY)

        # Invoke client installation
        rtn = pkg.launch_builtin_module('client', ['install'])
        if rtn != 0:
            log.w(TAG, "Unable to install dtf client. Try manually.")

        return 0

    def do_init(self):

        """Perform the initialization"""

        log.i(TAG, "Project initialization started.")

        signal.signal(signal.SIGINT, self.do_shutdown)

        if os.path.isfile(utils.CONFIG_FILE_NAME):
            log.e(TAG, "Configuration file already exists!")
            return -1

        compat.raw_input("\nPlease connect test device "
                         "(press Enter to continue) ")

        # This might get in the way.
        try:
            del os.environ['ANDROID_SERIAL']
        except KeyError:
            pass

        self.adb = adb.DtfAdb(no_serial=True)

        log.i(TAG, "Restarting adb...")
        self.adb.kill_server()
        self.adb.start_server()

        log.i(TAG, "Waiting for a device to be connected...")

        time.sleep(1)

        init_device = self.determine_device()
        if init_device is None:
            log.e(TAG, "Error determining device.")
            return -2

        # Is this device offline?
        if init_device['status'] != adb.STATUS_DEVICE:
            log.e(TAG, "Cannot initialize offline/bootloader device!")
            log.e(TAG, "Try either: ")
            log.e(TAG, "    1. Run: adb kill-server && dtf init")
            log.e(TAG, "    2. Reboot the device.")
            return -3

        # Initialize device
        if self.initialize_device(init_device) != 0:
            log.e(TAG, "Error initializing device!")
            return -4

        log.i(TAG, "Device initialization complete!")
        return 0

    def execute(self, args):  # pylint: disable=unused-argument

        """Main module executor"""

        return self.do_init()
