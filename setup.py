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

from setuptools import setup
from os.path import isfile
from site import getsitepackages

import dtf.constants as constants
import dtf.core.utils as utils
import os

def is_root():

    """Determine if the calling user is root"""

    if os.geteuid() != 0:
        return False
    else:
        return True

def make_include_replace():

    """Make path replacement string for dtf_core.sh"""

    try:
        return ("%s/dtf-%s-*.egg/dtf/included"
                % (getsitepackages()[0], constants.VERSION))
    except IndexError:
        return None

def generate_include_files():

    """Generate list of includes dynamically"""

    #dest_inc_dir = "%s/" % utils.get_pydtf_dir()

    #return [(dest_inc_dir + d, [os.path.join(d, f) for f in files])
    return [('dtf/' + d, [os.path.join(d, f) for f in files])
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

    db_file_path = utils.get_dtf_data_dir() + "/main.db"
    completion_template = 'templates/completion_template.sh'
    completion_output = 'gen/dtf_bash_completion.sh'

    if isfile(completion_output):
        print "Completion output is already generated, skipping"
        return 0

    replacements = [('__REPLACE__', db_file_path)]

    if do_replace(completion_template, completion_output, replacements) != 0:

        print "Unable to perform updates to bash completion file!"
        return -1

    return 0

def create_dtf_core():

    """Generate a dtf_core.sh script based on current system"""

    replacements = list()

    core_template = 'templates/dtf_core_template.sh'
    core_output = 'included/dtf_core.sh'

    if isfile(core_output):
        print "dtf_core.sh output is already generated, skipping"
        return 0

    replacements.append(('__VERSION__', constants.VERSION))
    replacements.append(('__INCLUDED__', make_include_replace()))

    if do_replace(core_template, core_output, replacements) != 0:

        print "Unable to perform updates to dtf_core.sh file!"
        return -1

    return 0

def get_long_description():

    """Generate long description"""

    here = os.path.abspath(os.path.dirname(__file__))

    with open(os.path.join(here, 'README.rst')) as readme_f:
        return readme_f.read()

if not is_root():
    print "You must run this script as root!"
    exit(-1)

print "dtf installation started..."

# First, we need to populate the bash completion
try:
    os.mkdir('gen')
except OSError:
    pass

if create_bash_completion() != 0:
    print "Unable to generate bash completion file. Exiting!"
    exit(-3)

# Next, we also want to generate a dtf_core.sh
if create_dtf_core() != 0:
    print "Unable to generate dtf_core. Exiting!"

# Main Setup Execution
setup(
    name='dtf',
    version=constants.VERSION,
    description='Android Device Testing Framework (dtf)',
    long_description=get_long_description(),

    url='https://thecobraden.com/projects/dtf',
    download_url='https://github.com/jakev/dtf',

    author='Jake Valletta',
    author_email='javallet@gmail.com',
    license='ASL',

    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Information Technology',
        'Topic :: Security',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7'],

    keywords='android device security mobile reverse-engineering framework',

    packages=["dtf",
              "dtf.core",
              "dtf.core.cmds"],

    install_requires=['colored'],

    data_files=[('/etc/bash_completion.d',
                    ['gen/dtf_bash_completion.sh'])]
                            + generate_include_files(),

    entry_points={
        'console_scripts': [
            'dtf = dtf.launcher:main',
        ],
    },

    zip_safe=False,
    include_package_data=True,
)

print "dtf installation completed!"
