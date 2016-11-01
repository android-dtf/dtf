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
"""pytest for using dtf logging"""

import dtf.testutils as testutils
import pytest

TAG = 'test_log'

# We actually need a log file to exist to populate TOP
testutils.deploy_config_raw("")

import dtf.logging as log

# We can undeploy imediately after
testutils.undeploy()

# General Tests
def test_no_config():

    """Try to log without a config"""

    tmp_log_file = log.LOG_FILE
    log.LOG_FILE = None

    log.e(TAG, "Will this work?")

    log.LOG_FILE = tmp_log_file


# Error Messages
def test_error():

    """Log an error message"""

    log.LOG_LEVEL_STDOUT = 5
    log.LOG_LEVEL_FILE = 5

    log.e(TAG, "This is an error!")


def test_error_suppress():

    """Log an error message with logging at 0"""

    log.LOG_LEVEL_STDOUT = 0
    log.LOG_LEVEL_FILE = 0

    log.e(TAG, "This is an error!")


def test_error_ml():

    """Attempt to log a multi-line error"""

    values = ["Error #1", "Another Error", "doh"]

    log.e_ml(TAG, values)


def test_error_ml_wrong_type():

    """Attempt to log a multi-line error with non-list"""

    values = None

    with pytest.raises(TypeError):
        log.e_ml(TAG, values)


def test_error_ml_empty():

    """Attempt to log a multi-line error with empty"""

    values = [""]

    log.e_ml(TAG, values)


# Warning Messages
def test_warning():

    """Log a warning message"""

    log.LOG_LEVEL_STDOUT = 5
    log.LOG_LEVEL_FILE = 5

    log.w(TAG, "This is a warning!")


def test_warning_suppress():

    """Log a warning message with logging at 1"""

    log.LOG_LEVEL_STDOUT = 1
    log.LOG_LEVEL_FILE = 1

    log.w(TAG, "This is a warning!")


def test_warning_ml():

    """Attempt to log a multi-line warning"""

    values = ["Warning #1", "Another Warning", "doh"]

    log.w_ml(TAG, values)


def test_warning_ml_wrong_type():

    """Attempt to log a multi-line warning with non-list"""

    values = None

    with pytest.raises(TypeError):
        log.w_ml(TAG, values)


def test_warning_ml_empty():

    """Attempt to log a multi-line warning with empty"""

    values = [""]

    log.w_ml(TAG, values)


# Informational Messages
def test_info():

    """Log an informational message"""

    log.LOG_LEVEL_STDOUT = 5
    log.LOG_LEVEL_FILE = 5

    log.i(TAG, "This is informational!")


def test_info_suppress():

    """Log an informational message with logging at 2"""

    log.LOG_LEVEL_STDOUT = 2
    log.LOG_LEVEL_FILE = 2

    log.i(TAG, "This is information!")


def test_info_ml():

    """Attempt to log a multi-line informational message"""

    values = ["Info #1", "Another Info", "doh"]

    log.i_ml(TAG, values)


def test_info_ml_wrong_type():

    """Attempt to log a multi-line informational with non-list"""

    values = None

    with pytest.raises(TypeError):
        log.i_ml(TAG, values)


def test_info_ml_empty():

    """Attempt to log a multi-line info with empty"""

    values = [""]

    log.i_ml(TAG, values)


# Verbose Messages
def test_verb():

    """Log a verbose message"""

    log.LOG_LEVEL_STDOUT = 5
    log.LOG_LEVEL_FILE = 5

    log.v(TAG, "This is a verbose message!")


def test_verb_suppress():

    """Log a verbose message with logging at 3"""

    log.LOG_LEVEL_STDOUT = 3
    log.LOG_LEVEL_FILE = 3

    log.v(TAG, "This is a verbose message!")


def test_verb_ml():

    """Attempt to log a multi-line verbose message"""

    values = ["Verbose #1", "Another Verbose", "doh"]

    log.v_ml(TAG, values)


def test_verb_ml_wrong_type():

    """Attempt to log a multi-line verbose message with non-list"""

    values = None

    with pytest.raises(TypeError):
        log.v_ml(TAG, values)

def test_verb_ml_empty():

    """Attempt to log a multi-line error with empty"""

    values = [""]

    log.v_ml(TAG, values)


# Debug Messages
def test_debug():

    """Log a debug message"""

    log.LOG_LEVEL_STDOUT = 5
    log.LOG_LEVEL_FILE = 5

    log.d(TAG, "This is an debug!")


def test_debug_suppress():

    """Log a debug message with logging at 4"""

    log.LOG_LEVEL_STDOUT = 4
    log.LOG_LEVEL_FILE = 4

    log.d(TAG, "This is a debug message!")


def test_debug_ml():

    """Attempt to log a multi-line debug"""

    values = ["Debug #1", "Another Debug", "doh"]

    log.d_ml(TAG, values)


def test_debug_ml_wrong_type():

    """Attempt to log a multi-line debug with non-list"""

    values = None

    with pytest.raises(TypeError):
        log.d_ml(TAG, values)


def test_debug_ml_empty():

    """Attempt to log a multi-line debug with empty"""

    values = [""]

    log.d_ml(TAG, values)
