#!/usr/bin/env python
# Android Device Testing Framework ("dtf")
# Copyright 2013-2014 Jake Valletta (@jake_valletta)
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
# Python helper for DTF logging.

from time import localtime, strftime
from sys import stdout

# Can override just like the shell
LOG_LEVEL_FILE = 4   # By default, log E-V
LOG_LEVEL_STDOUT = 4 # By default, log E-V

# Internals ###########################################################
__log_file = None

def __getDate():
    return strftime("%a %b %d %H:%M:%S %Z %Y", localtime())

# Low level printing function
def __log(buf, entry):
    buf.write(entry)

# Low level stdout print
def __log_to_stdout(date, tag, message):

    entry = "[%s] %s - %s\n" % (date, tag, message)
    __log(stdout, entry)

# Low level file print
def __log_to_file(date, tag, message):


    # Lazy Load
    global __log_file

    if __log_file == None:
        __log_file = open(".dtflog", "a")
        
    entry = "[%s] %s - %s\n" % (date, tag, message)
    __log(__log_file, entry)
# ######################################################################

# Public Calls #########################################################

# Print a error message
def e(tag, message):

    date = __getDate()
    if LOG_LEVEL_STDOUT >= 1: __log_to_stdout(date, tag+"/E", message)
    if LOG_LEVEL_FILE >= 1: __log_to_file(date, tag+"/E", message)

# Print a warning message
def w(tag, message):

    date = __getDate()
    if LOG_LEVEL_STDOUT >= 2: __log_to_stdout(date, tag+"/W", message)
    if LOG_LEVEL_FILE >= 2: __log_to_file(date, tag+"/W", message)

# Print an informational message
def i(tag, message):

    date = __getDate()
    if LOG_LEVEL_STDOUT >= 3: __log_to_stdout(date, tag+"/I", message)
    if LOG_LEVEL_FILE >= 3: __log_to_file(date, tag+"/I", message)

# Print a verbose message
def v(tag, message):

    date = __getDate()
    if LOG_LEVEL_STDOUT >= 4: __log_to_stdout(date, tag+"/V", message)
    if LOG_LEVEL_FILE >= 4: __log_to_file(date, tag+"/V", message)


# Print a excessive debugging message
def d(tag, message):

    date = __getDate()
    if LOG_LEVEL_STDOUT >= 5: __log_to_stdout(date, tag+"/D", message)
    if LOG_LEVEL_FILE >= 5: __log_to_file(date, tag+"/D", message)
#########################################################################
