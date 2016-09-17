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
"""Common helpers for running pytests"""

import os
import shutil

DTF_CONFIG = '.dtfini'
DTF_LOG_FILE = '.dtflog'


def deploy_config(file_name):

    """Deploy project config from file"""

    config_name = "tests/data-files/%s" % file_name

    shutil.copy(config_name, DTF_CONFIG)

    # Create a log file.
    open(DTF_LOG_FILE, 'w').close()


def deploy_config_raw(contents):

    """Deply a project from a string"""

    with open(DTF_CONFIG, 'w') as conf_f:
        conf_f.write(contents)

    # Create a log file.
    open(DTF_LOG_FILE, 'w').close()

def undeploy():

    """Delete the test config"""

    os.remove(DTF_CONFIG)
    os.remove(DTF_LOG_FILE)
