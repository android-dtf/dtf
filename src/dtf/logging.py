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
from colored import fg, attr
from time import localtime, strftime
from sys import stdout

import dtf.core.utils as utils

#pylint: disable-msg=C0103

# Can override just like the shell
LOG_LEVEL_FILE = 4   # By default, log E-V
LOG_LEVEL_STDOUT = 4 # By default, log E-V

# Internals ###########################################################
LOG_FILE_NAME = '.dtflog'
LOG_FILE = None

# Terminal Coloring
COLOR_ERR = fg('#d70000')
COLOR_WARN = fg('#d75f00')
COLOR_INFO = fg('#00d700')
COLOR_VERB = fg('#00d7ff')
COLOR_DEB = fg('#d700af')

# Open file on module import
TOP = utils.get_project_root()
if TOP is not None:
    LOG_FILE = open(LOG_FILE_NAME, 'a')

def __get_date():

    """Format current date"""

    return strftime("%a %b %d %H:%M:%S %Z %Y", localtime())

# Low level printing function
def __log(buf, entry):



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
def e(tag, message):

    """Print an error message"""

    date = __get_date()
    if LOG_LEVEL_STDOUT >= 1:
        __log_to_stdout(COLOR_ERR, date, tag+"/E", message)
    if LOG_LEVEL_FILE >= 1:
        __log_to_file(date, tag+"/E", message)

def w(tag, message):

    """Print a warning message"""

    date = __get_date()
    if LOG_LEVEL_STDOUT >= 2:
        __log_to_stdout(COLOR_WARN, date, tag+"/W", message)
    if LOG_LEVEL_FILE >= 2:
        __log_to_file(date, tag+"/W", message)

def i(tag, message):

    """Print an informational message (non-debug)"""

    date = __get_date()
    if LOG_LEVEL_STDOUT >= 3:
        __log_to_stdout(COLOR_INFO, date, tag+"/I", message)
    if LOG_LEVEL_FILE >= 3:
        __log_to_file(date, tag+"/I", message)

def v(tag, message):

    """Print a verbose message (non-debug)"""

    date = __get_date()
    if LOG_LEVEL_STDOUT >= 4:
        __log_to_stdout(COLOR_VERB, date, tag+"/V", message)
    if LOG_LEVEL_FILE >= 4:
        __log_to_file(date, tag+"/V", message)

def d(tag, message):

    """Print a debugging message"""

    date = __get_date()
    if LOG_LEVEL_STDOUT >= 5:
        __log_to_stdout(COLOR_DEB, date, tag+"/D", message)
    if LOG_LEVEL_FILE >= 5:
        __log_to_file(date, tag+"/D", message)

# Multi-line Logging
def e_ml(tag, messages):

    """Print a multi-line error message"""

    if type(messages) != type(list()):
        raise TypeError

    for message in messages:
        if message == "":
            continue

        e(tag, message)

def w_ml(tag, messages):

    """Print a multi-lne warning message"""

    if type(messages) != type(list()):
        raise TypeError

    for message in messages:
        if message == "":
            continue

        w(tag, message)

def i_ml(tag, messages):

    """Print a multi-line informational message"""

    if type(messages) != type(list()):
        raise TypeError

    for message in messages:
        if message == "":
            continue

        i(tag, message)

def v_ml(tag, messages):

    """Print a multi-line verbose message"""

    if type(messages) != type(list()):
        raise TypeError

    for message in messages:
        if message == "":
            continue

        v(tag, message)

def d_ml(tag, messages):

    """Print a multi-line debugging message"""

    if type(messages) != type(list()):
        raise TypeError

    for message in messages:
        if message == "":
            continue

        d(tag, message)
#########################################################################
