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
""" dtf Checker script """
import os
import os.path
import shlex
import subprocess
import sys
from argparse import ArgumentParser

import dtf.core.utils as utils
import dtf.core.packagemanager as pm
import dtf.core.item
import dtf.logging as log
from dtf.globals import DTF_DB, DTF_LIBRARIES_DIR

TAG = "dtf_check"


def update_path():

    """Update path with dtf libraries"""

    if not os.path.isfile(DTF_DB):
        return 0

    for lib in pm.get_libraries(name_only=True):

        lib_path = "%s/%s" % (DTF_LIBRARIES_DIR, lib)

        sys.path.append(lib_path)

    return 0


def check_required():

    """Determine if all dependencies are accounted for"""

    # Check for pylint
    if utils.which("pylint") == "":
        log.e(TAG, "pylint is required!")
        return False

    # Check for flake8
    if utils.which("flake8") == "":
        log.e(TAG, "flake8 is required!")
        return False

    # Check for shellcheck
    if utils.which("shellcheck") == "":
        log.e(TAG, "shellcheck is required!")
        return False

    # Check for checkbashisms
    if utils.which("checkbashisms") == "":
        log.e(TAG, "checkbashisms is required!")
        return False

    return True


def do_checks(file_name, all_checks, strict_checks):

    """Perform checks"""

    # Update path to include libs
    update_path()

    if not os.path.isfile(file_name):
        log.e(TAG, "[FAIL] %s is not a file." % file_name)
        return -1

    base_name = os.path.basename(file_name)
    module_name = os.path.splitext(base_name)[0]

    log.d(TAG, "Full File: %s" % file_name)
    log.d(TAG, "Base name: %s" % base_name)
    log.d(TAG, "Module name: %s" % module_name)

    # First, is this python, or bash?
    if pm.is_python_module(file_name, module_name):
        log.i(TAG, "[PASS] Is python, doing python checks...")
        return do_python_checks(file_name, module_name,
                                all_checks, strict_checks)
    elif pm.is_bash_module(file_name):
        log.i(TAG, "[PASS] Is bash, doing bash checks...")
        return do_bash_checks(file_name, module_name,
                              all_checks, strict_checks)
    else:
        log.e(TAG, "[FAIL] This is not recognized as either python or bash!")
        return -2


def do_python_checks(file_name, module_name, all_checks, strict_checks):

    """Run all python checks"""

    # First attempt to auto parse
    item = pm.parse_python_module(file_name, module_name)

    if item is None:
        log.e(TAG, "[FAIL] Auto parse failed!")
        return -1

    if do_auto_checks(item, strict_checks) != 0:
        return -1

    if all_checks:
        log.d(TAG, "Running pylint...")
        if run_command("pylint \"%s\"" % file_name) != 0:
            log.e(TAG, "[FAIL] pylint failed.")
            return -1

        log.d(TAG, "Running flake8...")
        if run_command("flake8 \"%s\"" % file_name) != 0:
            log.e(TAG, "[FAIL] flake8 failed.")
            return -1

    log.i(TAG, "[PASS] All checks passed!")

    return 0


def do_bash_checks(file_name, module_name, all_checks, strict_checks):

    """Run app bash checks"""

    # First attempt to execute.
    if not utils.is_executable(file_name):
        log.e(TAG, "[FAIL] Module is not marked executable!")
        return -1

    # Next attempt to auto parse
    item = pm.parse_bash_module(file_name, module_name)

    if item is None:
        log.e(TAG, "[FAIL] Auto parse failed!")
        return -1

    if do_auto_checks(item, strict_checks) != 0:
        return -1

    if all_checks:
        log.d(TAG, "Running checkbashisms...")
        if run_command("checkbashisms -f \"%s\"" % file_name) != 0:
            log.e(TAG, "[FAIL] checkbashisms failed.")
            return -1

        log.d(TAG, "Running shellcheck...")
        if run_command("shellcheck \"%s\"" % file_name) != 0:
            log.e(TAG, "[FAIL] shellcheck failed.")
            return -1

    log.i(TAG, "[PASS] All checks passed!")

    return 0


def do_auto_checks(item, strict_checks):

    """Run the auto checks"""

    # Check Health
    if do_health_checks(item, strict_checks) != 0:
        return -1
    # Check Version
    elif do_version_checks(item, strict_checks) != 0:
        return -1
    # Check rest
    elif do_other_checks(item, strict_checks) != 0:
        return -1
    else:
        return 0


def do_health_checks(item, strict):

    """Run health checks"""

    health = item.health

    if health is None:
        log.w(TAG, "[WARN] Health is none, this should be set!")
        if strict:
            return -1
    elif health not in dtf.core.item.VALID_HEALTH_VALUES:
        log.e(TAG, "[FAIL] invalid health specified!")
        return -1
    elif health in ['broken', 'deprecated']:
        log.w(TAG, "[WARN] Broken or deprecated modules should be fixed!")
        if strict:
            return -1
    else:
        log.i(TAG, "[PASS] Valid health.")

    return 0


def do_version_checks(item, strict):

    """Run version checks"""

    if item.version is None:
        log.w(TAG, "[WARN] Version is none, this should be set!")
        if strict:
            return -1
    elif not dtf.core.item.is_valid_version(item.version):
        log.e(TAG, "[FAIL] invalid version (must be semvar)")
        return -1
    else:
        log.i(TAG, "[PASS] Valid version.")

    return 0


def do_other_checks(item, strict):

    """Run rest of the auto checkks"""

    if item.about is None:
        log.w(TAG, "[WARN] About string is none, this should be set!")
        if strict:
            return -1
    else:
        log.i(TAG, "[PASS] Valid about.")

    # Check Author
    if item.author is None:
        log.w(TAG, "[WARN] Author is none, this should be set!")
        if strict:
            return -1
    else:
        log.i(TAG, "[PASS] Valid author.")

    return 0


def run_command(cmd):

    """Run a command"""

    lexed = shlex.split(cmd)
    proc = subprocess.Popen(lexed)
    proc.communicate()

    return proc.returncode


def main():

    """Main loop"""

    parser = ArgumentParser(prog='dtf_checker',
                            description='Check module for syntax & style.')
    parser.add_argument('module_name', metavar="module_name", type=str,
                        nargs='+', default=None,
                        help='The module to check.')
    parser.add_argument('-a', '--all', dest='all_checks', action='store_const',
                        const=True, default=False,
                        help="Run more vigorous checks.")
    parser.add_argument('-s', '--strict', dest='strict', action='store_const',
                        const=True, default=False,
                        help="Treat warnins as errors.")

    parsed_args = parser.parse_args()

    all_checks = parsed_args.all_checks
    strict_checks = parsed_args.strict
    module_name = parsed_args.module_name[0]

    # First, lets make sure have stuff
    if not check_required():
        return -1

    # Do python logging override
    try:
        log.LOG_LEVEL_STDOUT = int(os.environ['GLOG_LEVEL'])
    except KeyError:
        pass
    except ValueError:
        log.w(TAG, "Invalid GLOG_LEVEL value (0-5 is allowed)")

    # Do checks
    return do_checks(module_name, all_checks, strict_checks)

if __name__ == "__main__":

    sys.exit(main())
