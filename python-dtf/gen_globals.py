#!/usr/bin/env python
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

"""Helper script to generate globals.ini"""

from __future__ import absolute_import
from __future__ import print_function
import fnmatch
import os
import sys
from configparser import ConfigParser

OUTPUT_FILE = "included/globals.ini"
INCLUDED_DIR = "~/.dtf/included"

# These are file mappings based on prefix
BINDINGS = [['dtf_aapt', 'aapt', 'aapt'],
            ['dtf_abe', 'abe', 'abe'],
            ['dtf_apktool', 'apktool', 'apktool'],
            ['dtf_axmlprinter2', 'axmlprinter2', 'axmlprinter2'],
            ['dtf_baksmali', 'smali', 'baksmali'],
            ['dtf_smali', 'smali', 'smali']]

# These are mappings to a directory
DIR_BINDINGS = [['dtf_dex2jar', 'dex2jar']]


def main():

    """Main loop"""

    parser = ConfigParser.SafeConfigParser()

    print('Doing globals.ini creation...')

    # Add dtfClient details
    if do_client_section(parser) != 0:
        return -1

    if do_bindings_section(parser) != 0:
        return -1

    if do_config_section(parser) != 0:
        return -1

    # Write it out
    with open(OUTPUT_FILE, 'wb') as configfile:
        parser.write(configfile)

    return 0


def bind_file_in_dir(local, prefix):

    """Find a file in directory matching prefix"""

    local_dir = "included/%s" % local
    binding_name = None

    for file_name in os.listdir(local_dir):
        if fnmatch.fnmatch(file_name, "%s*" % prefix):
            binding_name = file_name
            break

    if binding_name is None:
        return None

    full_out = "%s/%s/%s" % (INCLUDED_DIR, local, binding_name)

    return full_out


def do_config_section(parser):

    """Populate the config section"""

    parser.add_section('Config')

    # Color is enabled by default
    parser.set('Config', 'use_colors', '1')

    return 0

def do_client_section(parser):

    """Populate the client section"""

    apk_name = None

    for file_name in os.listdir('included/dtfClient/'):
        if fnmatch.fnmatch(file_name, '*.apk'):
            apk_name = file_name
            print("Found dtfClient APK: %s" % apk_name)
            break

    if apk_name is None:
        print('Unable to find dtfClient APK!')
        return -1

    full_apk_name = "%s/dtfClient/%s" % (INCLUDED_DIR, apk_name)

    parser.add_section('Client')
    parser.set("Client", "apk_file", full_apk_name)

    return 0


def do_bindings_section(parser):

    """Populate the bindings section"""

    parser.add_section('Bindings')

    for binding, local, prefix in BINDINGS:

        local_dir = "included/%s" % local
        out_name = bind_file_in_dir(local, prefix)

        if out_name is None:
            print("Error finding match: %s, %s" % (binding, local_dir))

        parser.set('Bindings', binding, out_name)

    for binding, local in DIR_BINDINGS:

        local_dir = "included/%s" % local

        if not os.path.isdir(local_dir):
            print("Unable to bind dir: %s, %s" % (binding, local_dir))
            return -1

        out_dir = "%s/%s/" % (INCLUDED_DIR, local)
        parser.set('Bindings', binding, out_dir)

    return 0

if __name__ == "__main__":
    sys.exit(main())
