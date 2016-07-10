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
import os

import dtf.constants as constants


def get_long_description():

    """Generate long description"""

    here = os.path.abspath(os.path.dirname(__file__))

    with open(os.path.join(here, 'README.rst')) as readme_f:
        return readme_f.read()

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

    data_files=[
        ('/etc/bash_completion.d',
         ['data-files/dtf_bash_completion.sh']),
    ],

    entry_points={
        'console_scripts': [
            'dtf = dtf.launcher:main',
        ],
    },

    zip_safe=False,
    include_package_data=True,
)
