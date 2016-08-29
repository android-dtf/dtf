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


# Read in the version data.
def generate_version_string():

    """Generate version string based on VERSION"""

    values = open(os.path.join(
        os.path.dirname(__file__),
        "dtf/VERSION")).read().rstrip().split('-')

    if len(values) < 3:
        return "%s.%s" % (values[0], values[1])
    else:
        return "%s.%s.%s" % (values[0], values[1], values[2])

setup(
    name='dtf',
    version=generate_version_string(),
    description='Android Device Testing Framework (dtf)',
    long_description=open(
        os.path.join(os.path.dirname(__file__), "README.rst")).read(),

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
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],

    data_files=[
        ('/etc/bash_completion.d',
         ['data-files/dtf.bash']),
    ],

    entry_points={
        'console_scripts': [
            'dtf = dtf.launcher:main',
            'dtf_check = dtf.checker:main',
        ],
    },

    zip_safe=False,
    include_package_data=True,
)
