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
"""Test utilities for running dtf tests"""

import json
import os
import shutil
import sys
import ConfigParser

from subprocess import Popen, PIPE

import dtf.constants as constants

DTF_CONFIG = '.dtfini'
DTF_LOG_FILE = '.dtflog'


class Result(object):  # pylint: disable=too-few-public-methods

    """Wrapper for stdout/error and return code"""

    def __init__(self, return_code, stdout, stderr):

        """Initialize object"""

        self.return_code = return_code
        self.stdout = stdout
        self.stderr = stderr

    @property
    def json(self):

        """JSONify output"""

        return json.loads(self.stdout)


def get_default_config(api=constants.API_MAX):

    """Factory for creating a config"""

    config = ConfigParser.RawConfigParser()

    config.add_section('Info')
    config.set('Info', 'sdk', api)

    return config


# Taken from awscli/testutils.py
def get_stdout_encoding():

    """Determine encoding of stdout"""

    encoding = getattr(sys.__stdout__, 'encoding', None)
    if encoding is None:
        encoding = 'utf-8'

    return encoding


def dtf(command, input_data=None):

    """Run a dtf command"""

    env = os.environ.copy()

    full_command = "dtf %s" % (command)

    process = Popen(full_command, stdout=PIPE, stderr=PIPE, stdin=PIPE,
                    shell=True, env=env)

    stdout_encoding = get_stdout_encoding()

    kwargs = {}

    if input_data:
        kwargs = {'input': input_data}

    stdout, stderr = process.communicate(**kwargs)

    return Result(process.returncode,
                  stdout.decode(stdout_encoding),
                  stderr.decode(stdout_encoding))


def deploy_config_file(file_name):

    """Deploy project config from file"""

    config_name = "tests/data-files/%s" % file_name

    shutil.copy(config_name, DTF_CONFIG)

    # Create a log file.
    open(DTF_LOG_FILE, 'w').close()


def deploy_config_raw(contents):

    """Deploy a project from a string"""

    with open(DTF_CONFIG, 'w') as conf_f:
        conf_f.write(contents)

    # Create a log file.
    open(DTF_LOG_FILE, 'w').close()


def deploy_config(cfg):

    """Deploy actual ConfigParser object"""

    with open(DTF_CONFIG, 'w') as conf_f:
        cfg.write(conf_f)

    # Create a log file.
    open(DTF_LOG_FILE, 'w').close()


def undeploy():

    """Delete the test project"""

    try:
        os.remove(DTF_CONFIG)
    except OSError:
        pass

    try:
        os.remove(DTF_LOG_FILE)
    except OSError:
        pass
