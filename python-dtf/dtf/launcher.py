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
import sys
import subprocess
import os
import os.path
import tarfile

import dtf.constants as constants
import dtf.core.utils as utils
import dtf.packages as pkg
import dtf.logging as log
from dtf.globals import DTF_INCLUDED_DIR

# Check for version before anything
if sys.version_info < (2, 6, 0):
    sys.stderr.write("dtf requires python version 2.6 or higher!")
    sys.exit(1)

TAG = "dtf"

BUILT_IN_LIST = ['archive', 'client', 'local', 'prop', 'reset',
                 'source', 'status']


def usage():

    """Print dtf usage brief"""

    print ("Android Device Testing Framework (dtf) v%s"
           % constants.VERSION)
    print 'Usage: dtf [module|command] <arguments>'
    print ''
    print "Run with '-h' or 'help' for additional information."

    return -1


def usage_full():

    """Print full dtf usage"""

    print ("Android Device Testing Framework (dtf) v%s"
           % constants.VERSION)
    print 'Usage: dtf [module|command] <arguments>'
    print '   Built-in Commands:'
    print '    archive     Archive your dtf project files.'
    print '    binding     Print dtf helper bindings.'
    print '    client      Install/remove the dtf client.'
    print '    help        Prints this help screen.'
    print '    init        Initializes a project.'
    print '    local       Display all local modules.'
    print '    pm          The dtf package manager.'
    print '    prop        The dtf property manager.'
    print '    reset       Removes the dtf config from current directory.'
    print '    source      Used for sourcing additional commands.'
    print '    status      Determine if project device is attached.'
    print '    version     Print version number.'

    return -1


def is_first_run():

    """Determine if this is first run"""

    if os.path.isdir(DTF_INCLUDED_DIR):
        return False
    else:
        return True


def unpack_included():

    """Unzip the included TAR"""

    os.mkdir(DTF_INCLUDED_DIR)

    tar_path = "%s/included.tar" % (os.path.split(__file__)[0])

    with tarfile.TarFile(tar_path, 'r') as included_tar:
        included_tar.extractall(DTF_INCLUDED_DIR)

    return 0


def find_built_in_module(cmd):

    """Determine if the command is a built in module"""

    return bool(cmd in BUILT_IN_LIST)


def check_dependencies():

    """Determine if all dependencies are accounted for"""

    # Check for adb
    if utils.which("adb") == "":
        log.e(TAG, "dtf requires `adb` (part of Android SDK)!")
        return -5

    # Check for sqlite3
    if utils.which("sqlite3") == "":
        log.e(TAG, "dtf requires `sqlite3`!")
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


def main():

    """Main loop"""

    rtn = 0

    # First, lets make sure dtf has the dependencies we want.
    if check_dependencies() != 0:
        return -2

    # If this is first run, we need to extract the included files
    if is_first_run():
        unpack_included()

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
        print constants.VERSION
        sys.exit(0)

    # Almost all commands with dtf require you to be in a project directory,
    # but some don't. Check for those next.
    elif command_name == 'pm':
        return pkg.launch_builtin_module('pm', sys.argv, chdir=False)

    elif command_name in ['init', 'source', 'binding']:
        return pkg.launch_builtin_module(command_name, sys.argv)

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

if __name__ == "__main__":

    sys.exit(main())
