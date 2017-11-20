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
""" dtf Main Launcher """

from __future__ import absolute_import
from __future__ import print_function
import sys
import subprocess
import os
import os.path

# Coverage is used for tests.
try:
    import coverage
except ImportError:
    pass
else:
    coverage.process_startup()

import dtf.constants as constants
import dtf.core.autoconfig as autoconfig
import dtf.core.utils as utils
import dtf.core.packagemanager as packagemanager
import dtf.packages as pkg
import dtf.logging as log
import dtf.globals as dtfglobals

# Check for version before anything
if sys.version_info < (2, 6, 0):
    sys.stderr.write("dtf requires python version 2.6 or higher!")
    sys.exit(1)

TAG = "dtf"

BUILT_IN_LIST = ['archive', 'client', 'local', 'prop', 'reset',
                 'status']


def usage():

    """Print dtf usage brief"""

    print("Android Device Testing Framework (dtf) v%s"
          % constants.VERSION)
    print('Usage: dtf [module|command] <arguments>')
    print('')
    print("Run with '-h' or 'help' for additional information.")

    return -1


def usage_full():

    """Print full dtf usage"""

    print("Android Device Testing Framework (dtf) v%s"
          % constants.VERSION)
    print('Usage: dtf [module|command] <arguments>')
    print('   Built-in Commands:')
    print('    archive     Archive your dtf project files.')
    print('    binding     Print dtf helper bindings.')
    print('    client      Install/remove the dtf client.')
    print('    help        Prints this help screen.')
    print('    init        Initializes a project.')
    print('    local       Display all local modules.')
    print('    pm          The dtf package manager.')
    print('    prop        The dtf property manager.')
    print('    reset       Removes the dtf config from current directory.')
    print('    status      Determine if project device is attached.')
    print('    upgrade     Perform dtf upgrades.')
    print('    version     Print version number (--full for verbose).')

    return 0


def is_first_run():

    """Determine if this is first run"""

    if os.path.isdir(dtfglobals.DTF_INCLUDED_DIR):
        return False
    else:
        return True


def find_built_in_module(cmd):

    """Determine if the command is a built in module"""

    return bool(cmd in BUILT_IN_LIST)


def check_dependencies():

    """Determine if all dependencies are accounted for"""

    # Check for adb
    if utils.which("adb") == "":
        log.e(TAG, "dtf requires `adb` (part of Android SDK)!")
        return -5

    # Check for Java
    if utils.which("java") != "":

        out = subprocess.check_output(["java", "-version"],
                                      stderr=subprocess.STDOUT)

        java_ver = out.split('\n')[0]

        if java_ver.find("1.7") == -1 and java_ver.find("1.8") == -1:
            log.e(TAG, "dtf requires Java 1.7 or 1.8!")
            return -5
    else:
        log.e(TAG, "dtf requires Java 1.7!")
        return -5

    return 0


def print_version(args):

    """Print the version (short or long)"""

    # Long version
    if len(args) > 0 and args[0] == '--full':
        apk_version = dtfglobals.get_generic_global(
            dtfglobals.CONFIG_SECTION_CLIENT, 'apk_version')
        bundle_version = dtfglobals.get_generic_global(
            dtfglobals.CONFIG_SECTION_BINDINGS, 'version')
        python_version = constants.VERSION

        print("Python Version: %s" % python_version)
        print("dtfClient Version: %s" % apk_version)
        print("Bindings Version Date: %s" % bundle_version)
    else:
        print(constants.VERSION)

    return 0


def main():

    """Main loop"""

    rtn = 0

    # First, lets make sure dtf has the dependencies we want.
    if check_dependencies() != 0:
        return -2

    # If this is first run, we need to do a couple of things.
    # Note: I exit here; doesn't matter what you tried to run.
    if is_first_run():
        sys.exit(do_first_run_process())

    # Next, check args.
    if len(sys.argv) < 2:
        sys.exit(usage())

    # Remove the execute path
    sys.argv.pop(0)
    # Remove and store cmd_name
    command_name = sys.argv.pop(0)

    # Help menu
    if command_name in ['-h', '--help', 'help']:
        sys.exit(usage_full())
    # Version information
    elif command_name in ['-v', '--version', 'version']:
        sys.exit(print_version(sys.argv))

    # Almost all commands with dtf require you to be in a project directory,
    # but some don't. Check for those next.
    elif command_name == 'pm':
        return pkg.launch_builtin_module('pm', sys.argv, chdir=False,
                                         skip_checks=True)

    elif command_name in ['init', 'binding', 'upgrade']:
        return pkg.launch_builtin_module(command_name, sys.argv,
                                         skip_checks=True)

    # Ok, now we need to get to the top of the project directory.
    project_root = utils.get_project_root()

    if project_root is None:
        log.e(TAG, "Unable to find a project root! Is this a dtf project?")
        return -3

    # Next, we check the following:
    # 1. Is it a built-in command?
    # 2. Is it a local module?
    # 3. Is it a module we know about?
    if find_built_in_module(command_name):
        rtn = pkg.launch_builtin_module(command_name, sys.argv)

    elif pkg.find_local_module(project_root, command_name):
        rtn = pkg.launch_local_module(project_root, command_name, sys.argv)

    elif pkg.is_module_installed(command_name):
        rtn = pkg.launch_module(command_name, sys.argv)

    else:
        log.e(TAG, "Module or command '%s' not found!" % command_name)
        rtn = -4

    return rtn


def do_first_run_process():

    """Perform the file time run install"""

    log.i(TAG, "First time launch of dtf detected...")

    # Set things up if they haven't been already
    if packagemanager.create_data_dirs() != 0:
        log.e(TAG, "Unable to setup dtf data directories!")
        return -4

    if not os.path.isfile(dtfglobals.DTF_DB):
        if packagemanager.initialize_db() != 0:
            log.e(TAG, "Error creating and populating dtf db!!")
            return -7

    if autoconfig.initialize_from_local(is_full=True) != 0:
        log.e(TAG, "Unable to initialize global settings!")
        return -5

    log.i(TAG, "Initial auto setup is completed!")
    return 0


if __name__ == "__main__":

    sys.exit(main())
