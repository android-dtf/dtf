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
import tempfile
import unittest
import zipfile
import ConfigParser

from subprocess import Popen, PIPE

import dtf.constants as constants
import dtf.core.utils as utils
import dtf.globals as gbls

DTF_CONFIG = utils.CONFIG_FILE_NAME
DTF_LOG_FILE = utils.LOG_FILE_NAME
LOCAL_MODULES_DIRECTORY = utils.LOCAL_MODULES_DIRECTORY
REPORTS_DIRECTORY = utils.REPORTS_DIRECTORY
DTF_DATA_DIR = gbls.DTF_DATA_DIR
DTF_BINARIES_DIR = gbls.DTF_BINARIES_DIR
DTF_LIBRARIES_DIR = gbls.DTF_LIBRARIES_DIR
DTF_MODULES_DIR = gbls.DTF_MODULES_DIR
DTF_PACKAGES_DIR = gbls.DTF_PACKAGES_DIR
DTF_DB = gbls.DTF_DB

TEST_TOP = os.getcwd()


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


class DataFile(object):  # pylint: disable=too-few-public-methods

    """Wrapper for opening using included files"""

    def __init__(self, file_name):

        """Attempt to open file"""

        full_file_name = "%s/tests/data-files/%s" % (TEST_TOP, file_name)
        if not os.path.isfile(full_file_name):
            raise OSError

        self.full_file_name = full_file_name
        self.file_handle = open(full_file_name, 'rb')

    def read(self):

        """Read from file handle"""

        return self.file_handle.read()

    def __str__(self):

        """Return full path"""

        return self.full_file_name


class DataZip(object):  # pylint: disable=too-few-public-methods

    """Wrapper for opening a zip file of content"""

    def __init__(self, file_name):

        """Open zip to temp dir"""

        full_zip_name = "%s/tests/data-files/%s" % (TEST_TOP, file_name)
        if not os.path.isfile(full_zip_name):
            raise OSError

        if not zipfile.is_zipfile(full_zip_name):
            raise OSError
        self.zip_f = zipfile.ZipFile(full_zip_name)

        self.temp_dir = tempfile.mkdtemp()

        for name in self.zip_f.namelist():
            self.zip_f.extract(name, self.temp_dir)

    def close(self):

        """Close the DataZip"""

        self.zip_f.close()
        utils.delete_tree(self.temp_dir)

    def __str__(self):

        """Return full path"""

        return self.temp_dir


class IntegrationTest(unittest.TestCase):

    """Class for performing dtf integration testing"""

    config = None

    def setUp(self):

        """Setup project with default config"""

        # Set up a default config, and store
        self.config = self.default_config()
        self.update_config(self.config)

        # Create directory structure if not there.
        if not os.path.isdir(DTF_DATA_DIR):
            os.mkdir(DTF_DATA_DIR)
            os.mkdir(DTF_BINARIES_DIR)
            os.mkdir(DTF_LIBRARIES_DIR)
            os.mkdir(DTF_MODULES_DIR)
            os.mkdir(DTF_PACKAGES_DIR)

        # Create the rest of the content.
        utils.touch(DTF_LOG_FILE)
        os.mkdir(LOCAL_MODULES_DIRECTORY)
        os.mkdir(REPORTS_DIRECTORY)

    def tearDown(self):

        """Remove mock project"""

        # Remove all content and main.db
        utils.delete_file(DTF_DB)

        utils.delete_file(DTF_CONFIG)
        utils.delete_file(DTF_LOG_FILE)
        utils.delete_tree(LOCAL_MODULES_DIRECTORY)
        utils.delete_tree(REPORTS_DIRECTORY)

    @classmethod
    def default_config(cls):

        """Placeholder for default config"""

        return None

    @classmethod
    def run_cmd(cls, cmd, input_data=None):

        """Run a dtf command"""

        rtn = dtf(cmd, input_data=input_data)

        print rtn.stdout, rtn.stderr

        return rtn

    @classmethod
    def update_config_raw(cls, contents):

        """Update config to contents supplied"""

        with open(DTF_CONFIG, 'w') as conf_f:
            conf_f.write(contents)

    @classmethod
    def update_config(cls, cfg):

        """Update config to Config object"""

        with open(DTF_CONFIG, 'w') as conf_f:
            cfg.write(conf_f)


class BasicIntegrationTest(IntegrationTest):

    """Default test for offline integration test"""

    @classmethod
    def default_config(cls):

        """Return basic config for offline"""

        config = ConfigParser.RawConfigParser()

        config.add_section('Info')
        config.set('Info', 'sdk', constants.API_MAX)

        return config


class BasicIntegrationDeviceTest(IntegrationTest):

    """Default test for online integration test"""

    @classmethod
    def default_config(cls):

        """Return basic config for online"""

        config = ConfigParser.RawConfigParser()

        config.add_section('Info')
        config.set('Info', 'sdk', constants.API_MAX)
        config.set('Info', 'serial', 'emulator-5554')

        return config


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

    env['GLOG_LEVEL'] = '5'

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

    os.mkdir(LOCAL_MODULES_DIRECTORY)


def deploy_config_raw(contents):

    """Deploy a project from a string"""

    with open(DTF_CONFIG, 'w') as conf_f:
        conf_f.write(contents)

    # Create a log file.
    open(DTF_LOG_FILE, 'w').close()

    os.mkdir(LOCAL_MODULES_DIRECTORY)


def deploy_config(cfg):

    """Deploy actual ConfigParser object"""

    with open(DTF_CONFIG, 'w') as conf_f:
        cfg.write(conf_f)

    # Create a log file.
    open(DTF_LOG_FILE, 'w').close()

    os.mkdir(LOCAL_MODULES_DIRECTORY)


def undeploy():

    """Delete the test project"""

    utils.delete_file(DTF_CONFIG)
    utils.delete_file(DTF_LOG_FILE)
    utils.delete_tree(LOCAL_MODULES_DIRECTORY)
