#!/usr/bin/env bash
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

# Modules may source this file to use DTF's logging capabilities.

# Feel free to override these in your module.
LOG_FILE=.dtflog
LOG_LEVEL=4
LOG_TO_STDOUT=1
LOG_TO_FILE=1

#########################
# Format Notes:
#[2013-01-02T12:00:31] testmodule/E - This is an error!
# [], E, W, I, V, D
#  0, 1, 2, 3, 4, 5
#########################

# Internal low-level logger
_log()
{
    date="["`date`"]"
    app=$1
    shift
    message=$@

    if [ "${LOG_TO_FILE}" -eq "1" ]; then echo "${date} ${app} - ${message}" >> ${LOG_FILE}; fi
    if [ "${LOG_TO_STDOUT}" -eq "1" ]; then echo "${date} ${app} - ${message}"; fi
}

# Print an error message
log_e()
{
    if [ "${LOG_LEVEL}" -ge "1" ]; then
        caller=$(basename ${BASH_SOURCE[1]})
        _log "${caller}/E" $@
    fi
}

# Print a warning message
log_w()
{
    if [ "${LOG_LEVEL}" -ge "2" ]; then
        caller=$(basename ${BASH_SOURCE[1]})
        _log "${caller}/W" $@
    fi
}

# Print an informational message
log_i()
{
    if [ "${LOG_LEVEL}" -ge "3" ]; then
        caller=$(basename ${BASH_SOURCE[1]})
        _log "${caller}/I" $@
    fi
}

# Print a verbose message
log_v()
{
    if [ "${LOG_LEVEL}" -ge "4" ]; then
        caller=$(basename ${BASH_SOURCE[1]})
        _log "${caller}/V" $@
    fi
}

# Print a debugging message
log_d()
{
    if [ "${LOG_LEVEL}" -ge "5" ]; then
        caller=$(basename ${BASH_SOURCE[1]})
        _log "${caller}/D" $@
    fi
}
