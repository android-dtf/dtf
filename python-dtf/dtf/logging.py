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
"""dtf logging framework"""

from __future__ import absolute_import
from sys import stdout
from time import localtime, strftime

from colored import attr

import dtf.core.utils as utils
import dtf.colors as colors


# Can override just like the shell
LOG_LEVEL_FILE = 4    # By default, log E-V
LOG_LEVEL_STDOUT = 4  # By default, log E-V

# Internals ###########################################################
LOG_FILE = None

# Open file on module import
TOP = utils.get_project_root()
if TOP is not None:
    LOG_FILE = open(utils.LOG_FILE_NAME, 'a')


def __get_date():

    """Format current date"""

    return strftime("%a %b %d %H:%M:%S %Z %Y", localtime())


def __log(buf, entry):

    """Low level print function"""

    buf.write(entry)


# Low level stdout print
def __log_to_stdout(color, date, tag, message):

    """Write entry to stdout"""

    entry = "%s[%s] %s - %s %s\n" % (color, date, tag, message, attr(0))
    __log(stdout, entry)


# Low level file print
def __log_to_file(date, tag, message):

    """Write entry to stderr"""

    if LOG_FILE is None:
        return

    entry = "[%s] %s - %s\n" % (date, tag, message)
    __log(LOG_FILE, entry)

# ######################################################################


# Public Calls #########################################################
def e(tag, message):  # pylint: disable=invalid-name

    """Print an error message"""

    date = __get_date()
    if LOG_LEVEL_STDOUT >= 1:
        __log_to_stdout(colors.COLOR_ERR, date, tag+"/E", message)
    if LOG_LEVEL_FILE >= 1:
        __log_to_file(date, tag+"/E", message)


def w(tag, message):  # pylint: disable=invalid-name

    """Print a warning message"""

    date = __get_date()
    if LOG_LEVEL_STDOUT >= 2:
        __log_to_stdout(colors.COLOR_WARN, date, tag+"/W", message)
    if LOG_LEVEL_FILE >= 2:
        __log_to_file(date, tag+"/W", message)


def i(tag, message):  # pylint: disable=invalid-name

    """Print an informational message (non-debug)"""

    date = __get_date()
    if LOG_LEVEL_STDOUT >= 3:
        __log_to_stdout(colors.COLOR_INFO, date, tag+"/I", message)
    if LOG_LEVEL_FILE >= 3:
        __log_to_file(date, tag+"/I", message)


def v(tag, message):  # pylint: disable=invalid-name

    """Print a verbose message (non-debug)"""

    date = __get_date()
    if LOG_LEVEL_STDOUT >= 4:
        __log_to_stdout(colors.COLOR_VERB, date, tag+"/V", message)
    if LOG_LEVEL_FILE >= 4:
        __log_to_file(date, tag+"/V", message)


def d(tag, message):  # pylint: disable=invalid-name

    """Print a debugging message"""

    date = __get_date()
    if LOG_LEVEL_STDOUT >= 5:
        __log_to_stdout(colors.COLOR_DEB, date, tag+"/D", message)
    if LOG_LEVEL_FILE >= 5:
        __log_to_file(date, tag+"/D", message)


# Multi-line Logging
def e_ml(tag, messages):

    """Print a multi-line error message"""

    if not isinstance(messages, list):
        raise TypeError

    for message in messages:
        if message == "":
            continue

        e(tag, message)


def w_ml(tag, messages):

    """Print a multi-lne warning message"""

    if not isinstance(messages, list):
        raise TypeError

    for message in messages:
        if message == "":
            continue

        w(tag, message)


def i_ml(tag, messages):

    """Print a multi-line informational message"""

    if not isinstance(messages, list):
        raise TypeError

    for message in messages:
        if message == "":
            continue

        i(tag, message)


def v_ml(tag, messages):

    """Print a multi-line verbose message"""

    if not isinstance(messages, list):
        raise TypeError

    for message in messages:
        if message == "":
            continue

        v(tag, message)


def d_ml(tag, messages):

    """Print a multi-line debugging message"""

    if not isinstance(messages, list):
        raise TypeError

    for message in messages:
        if message == "":
            continue

        d(tag, message)
#########################################################################
