# Android Device Testing Framework ("dtf")
# Copyright 2013-2017 Jake Valletta (@jake_valletta)
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
"""Autoconfiguration Utils"""

from __future__ import absolute_import
from __future__ import print_function
import fnmatch
import os.path
import tarfile
import configparser

import dtf.globals as dtfglobals
import dtf.logging as log
import dtf.core.compat as compat
import dtf.core.utils as utils

TAG = "autoconfig"

# These are file mappings based on prefix
BINDINGS = [['dtf_aapt', 'aapt', True],
            ['dtf_abe', 'abe', False],
            ['dtf_apktool', 'apktool', False],
            ['dtf_axmlprinter2', 'axmlprinter2', False],
            ['dtf_baksmali', 'baksmali', False],
            ['dtf_smali', 'smali', False]]


def __unpack_included(tar_path):

    """Unzip the included TAR"""

    log.d(TAG, "Doing unpack from local...")

    utils.mkdir_recursive(dtfglobals.DTF_INCLUDED_DIR)

    tar_path = "%s/included.tar" % utils.get_dtf_lib_dir()

    with tarfile.TarFile(tar_path, 'r') as included_tar:
        included_tar.extractall(dtfglobals.DTF_INCLUDED_DIR)

    return 0


def __find_apk(path):

    """Find APK in directory"""

    apk_name = None

    for file_name in os.listdir(path):
        if fnmatch.fnmatch(file_name, '*.apk'):
            apk_name = file_name
            break

    if apk_name is None:
        return None

    full_apk_name = "%s/%s" % (path, apk_name)
    return full_apk_name


def __parse_version():

    """Parse and return version string"""

    version_file_name = "%s/VERSION" % dtfglobals.DTF_INCLUDED_DIR

    if not os.path.isfile(version_file_name):
        return "Unknown"

    return open(version_file_name, 'r').readline(10)


def __bind_file_in_dir(prefix):

    """Find a file in directory matching prefix"""

    binding_name = None

    for file_name in os.listdir(dtfglobals.DTF_INCLUDED_DIR):
        if fnmatch.fnmatch(file_name, "%s*" % prefix):
            binding_name = file_name
            break

    if binding_name is None:
        return None

    full_out = "%s/%s" % (dtfglobals.DTF_INCLUDED_DIR, binding_name)

    return full_out


def __do_config_section(parser):

    """Populate the config section"""

    # Purge section before adding.
    parser.remove_section(dtfglobals.CONFIG_SECTION_CONFIG)

    parser.add_section(dtfglobals.CONFIG_SECTION_CONFIG)

    # Color is enabled by default
    parser.set(dtfglobals.CONFIG_SECTION_CONFIG, 'use_colors', '1')

    return 0


def __do_client_section(parser):

    """Populate the client section"""

    apk_name = None
    dtf_client_path = "%s/dtfClient" % utils.get_dtf_lib_dir()
    debug_apk_path = "%s/debug" % dtf_client_path
    release_apk_path = "%s/release" % dtf_client_path

    # Check 'debug' dir first.
    if os.path.isdir(debug_apk_path):
        apk_name = __find_apk(debug_apk_path)
    elif os.path.isdir(release_apk_path):
        apk_name = __find_apk(release_apk_path)

    if apk_name is None:
        log.e(TAG, "No dtfClient APK found!")
        return -1

    # Purge section before adding.
    parser.remove_section(dtfglobals.CONFIG_SECTION_CLIENT)

    parser.add_section(dtfglobals.CONFIG_SECTION_CLIENT)
    parser.set(dtfglobals.CONFIG_SECTION_CLIENT, "apk_file", apk_name)

    return 0


def __do_bindings_section(parser):

    """Populate the bindings section"""

    # Purge section before adding.

    parser.remove_section(dtfglobals.CONFIG_SECTION_BINDINGS)

    parser.add_section(dtfglobals.CONFIG_SECTION_BINDINGS)

    for binding, prefix, exact in BINDINGS:

        # First check if it's installed
        installed_path = utils.which(prefix)
        if installed_path is not None:
            out_name = __do_use_custom(prefix, exact=exact)

        # Auto use
        else:
            out_name = __bind_file_in_dir(prefix)

        if out_name is None:
            return -1

        parser.set(dtfglobals.CONFIG_SECTION_BINDINGS, binding, out_name)

    return 0


def __do_use_custom(prefix, exact=False):

    """Ask the user if built in should be used."""

    message = ("It looks likes you have '%s' installed already. dtf comes "
               'with an included\nversion of this tool, would you like to use '
               'your own version? [N/y] ' % prefix)

    resp = compat.raw_input(message)

    if resp.lower() == 'y':

        # Exact is easy. which() and return.
        if exact:
            return utils.which(prefix)
        else:
            print("Please enter the full path to the '%s' JAR file" % prefix)

            resp = os.path.expanduser(compat.raw_input("File path: "))

            if not os.path.isfile(resp):
                log.e(TAG, "File '%s' doesn't exist, skipping!" % resp)
                return __bind_file_in_dir(prefix)

            return resp

    else:
        return __bind_file_in_dir(prefix)


def __write_globals(parser):

    """Perform writing"""
    with open(dtfglobals.DTF_GLOBAL_CONFIG, 'w') as configfile:
        parser.write(configfile)

    return 0


# Public API is here down.
def initialize_from_local(is_full=False):

    """Initialize from the included TAR with framework"""

    tar_path = "%s/included.tar" % utils.get_dtf_lib_dir()

    return initialize_from_tar(tar_path, is_full=is_full)


def initialize_from_tar(tar_path, is_full=False, clean_up=False):

    """Initialize from a remote TAR"""

    # Step 1 is to unpack our TAR. Let's delete what was there first.
    utils.delete_tree(dtfglobals.DTF_INCLUDED_DIR)
    __unpack_included(tar_path)

    # Next, we do the the auto config. If its not clean, save the config
    if is_full:
        parser = configparser.SafeConfigParser()

        if __do_client_section(parser) != 0:
            log.e(TAG, "Error building client section of config!")
            return -1

        if __do_bindings_section(parser) != 0:
            log.e(TAG, "Error building bindings section of config!")
            return -1

        if __do_config_section(parser) != 0:
            log.e(TAG, "Error building global section of config!")
            return -1
    else:
        # Not clean means we don't want to disturb other content in the
        parser = dtfglobals.get_copy()

        if __do_bindings_section(parser) != 0:
            return -1

    # Next, we always want to set the version.
    version_string = __parse_version()
    parser.set(dtfglobals.CONFIG_SECTION_BINDINGS,
               'version', version_string)

    # Save out the new config.
    __write_globals(parser)

    if clean_up:
        utils.delete_file(tar_path)

    return 0
