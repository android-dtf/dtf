#!/usr/bin/env bash
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

# Modules may source this file to use dtf's logging capabilities.

# Taken from: https://gist.github.com/bcap/5682077#file-terminal-control-sh
# Terminal output control (http://www.termsys.demon.co.uk/vtansi.htm)

TC='\e['

CLR_LINE_START="${TC}1K"
CLR_LINE_END="${TC}K"
CLR_LINE="${TC}2K"

# Hope no terminal is greater than 1k columns
RESET_LINE="${CLR_LINE}${TC}1000D"

# Colors and styles (based on https://github.com/demure/dotfiles/blob/master/subbash/prompt)

Bold="${TC}1m"    # Bold text only, keep colors
Undr="${TC}4m"    # Underline text only, keep colors
Inv="${TC}7m"     # Inverse: swap background and foreground colors
Reg="${TC}22;24m" # Regular text only, keep colors
RegF="${TC}39m"   # Regular foreground coloring
RegB="${TC}49m"   # Regular background coloring
Rst="${TC}0m"     # Reset all coloring and style
# ##########################


# Feel free to override these in your module.
LOG_FILE=.dtflog
LOG_LEVEL=4
LOG_TO_STDOUT=1
LOG_TO_FILE=1

# Don't override the global logging.
if [ -z $GLOG_LEVEL ]; then
    GLOG_LEVEL=$LOG_LEVEL
fi

#########################
# Format Notes:
#[2013-01-02T12:00:31] testmodule/E - This is an error!
# [], E, W, I, V, D
#  0, 1, 2, 3, 4, 5
#########################

COLOR_ERROR="${TC}38;5;160m" #d70000
COLOR_WARN="${TC}38;5;166m" #d75f00
COLOR_INFO="${TC}38;5;040m" #00d700
COLOR_VERB="${TC}38;5;045m" #00d7ff
COLOR_DEB="${TC}38;5;163m" #d700af

# Internal low-level logger
_log()
{
    date="["`date`"]"
    color=$1
    app=$2
    shift
    shift
    message=$@

    if [ "${LOG_TO_FILE}" -eq "1" ]; then
        echo "${date} ${app} - ${message}" >> ${LOG_FILE};
    fi

    if [ "${LOG_TO_STDOUT}" -eq "1" ]; then
        printf "${color}${date} ${app} - ${message}${Rst}\n";
    fi
}

# Print an error message
log_e()
{
    LOG_LEVEL=$GLOG_LEVEL
    if [ "${LOG_LEVEL}" -ge 1 ]; then
        caller=$(basename ${0})
        _log ${COLOR_ERROR} "${caller}/E" $@
    fi
}

# Print a warning message
log_w()
{
    LOG_LEVEL=$GLOG_LEVEL
    if [ "${LOG_LEVEL}" -ge 2 ]; then
        caller=$(basename ${0})
        _log ${COLOR_WARN} "${caller}/W" $@
    fi
}

# Print an informational message
log_i()
{
    LOG_LEVEL=$GLOG_LEVEL
    if [ "${LOG_LEVEL}" -ge 3 ]; then
        caller=$(basename ${0})
        _log ${COLOR_INFO} "${caller}/I" $@
    fi
}

# Print a verbose message
log_v()
{
    LOG_LEVEL=$GLOG_LEVEL
    if [ "${LOG_LEVEL}" -ge 4 ]; then
        caller=$(basename ${0})
        _log ${COLOR_VERB} "${caller}/V" $@
    fi
}

# Print a debugging message
log_d()
{
    LOG_LEVEL=$GLOG_LEVEL
    if [ "${LOG_LEVEL}" -ge 5 ]; then
        caller=$(basename ${0})
        _log ${COLOR_DEB} "${caller}/D" $@
    fi
}
