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
#
"""dtf Setup Script"""

from distutils.core import setup
from os.path import expanduser, isfile
from site import getsitepackages

import src.dtf.constants as constants
import src.dtf.logging as log

import os

TAG = "dtf-setup"

# No file logging yet please
log.LOG_LEVEL_FILE = 0

def get_pydtf_dir():

    """Return the location of the dtf dist-packages directory."""

    return getsitepackages()[0] + '/dtf'

def get_dtf_data_dir():

    """Return the location of the dtf data directory."""

    return expanduser('~') + '/.dtf'

def generate_include_files():

    """Generate list of includes dynamically"""
    dest_inc_dir = "%s/" % get_pydtf_dir()

    return [(dest_inc_dir + d, [os.path.join(d, f) for f in files])
                for d, folders, files in os.walk('included')]

def do_replace(in_f_name, out_f_name, replacement_list):

    """Do replacements in file"""

    out_f = open(out_f_name, 'w')

    with open(in_f_name, 'r') as in_f:

        out = in_f.read()

        for identifier, value in replacement_list:

            tmp_out = out.replace(identifier, value)

            out = tmp_out

        out_f.write(out)

    out_f.close()

    return 0


def create_bash_completion():

    """Generate a bash completion script based on current system"""

    db_file_path = get_dtf_data_dir() + "/main.db"
    completion_template = 'templates/completion_template.sh'
    completion_output = 'gen/dtf_bash_completion.sh'

    if isfile(completion_output):
        log.d(TAG, "Completion output is already generated.")
        return 0

    replacements = [('__REPLACE__', db_file_path)]

    if do_replace(completion_template, completion_output, replacements) != 0:

        log.e(TAG, "Unable to perform updates to bash completion file!")
        return -1

    return 0

def create_dtf_core():

    """Generate a dtf_core.sh script based on current system"""

    replacements = list()

    core_template = 'templates/dtf_core_template.sh'
    core_output = 'included/dtf_core.sh'

    if isfile(core_output):
        log.d(TAG, "dtf_core.sh output is already generated.")
        return 0

    replacements.append(('__VERSION__', constants.VERSION))
    replacements.append(('__INCLUDED__', get_pydtf_dir() + '/included'))

    if do_replace(core_template, core_output, replacements) != 0:

        log.e(TAG, "Unable to perform updates to dtf_core.sh file!")
        return -1

    return 0

log.i(TAG, "dtf installation started...")

# First, we need to populate the bash completion
try:
    os.mkdir('gen')
except OSError:
    pass

if create_bash_completion() != 0:
    log.e(TAG, "Unable to generate bash completion file. Exiting!")
    exit(-3)

# Next, we also want to generate a dtf_core.sh
if create_dtf_core() != 0:
    log.e(TAG, "Unable to generate dtf_core. Exiting!")

opts = {}

opts['name'] = 'dtf'
opts['version'] = constants.VERSION
opts['description'] = 'Android Device Testing Framework (dtf)'
opts['author'] = 'Jake Valletta'
opts['author_email'] = 'javallet@gmail.com'
opts['url'] = 'https://thecobraden.com/projects/dtf'
opts['license'] = 'ASL2.0'
opts['scripts'] = ["dtf"]
opts['package_dir'] = {'' : 'src'}
opts['packages'] = ["dtf",
                    "dtf.core",
                    "dtf.core.cmds"]

opts['data_files'] = [
        ('/etc/bash_completion.d',
        ['gen/dtf_bash_completion.sh'])] + generate_include_files()

distrib = setup(**opts)

log.i(TAG, "dtf installation completed!")
