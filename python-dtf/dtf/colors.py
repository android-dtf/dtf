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
"""Wrapper API for using colors in dtf modules"""

from colored import fg, attr

import dtf.globals as glbl

COLOR_ERR = fg(1)
COLOR_WARN = fg(3)
COLOR_INFO = fg(2)
COLOR_VERB = fg(6)
COLOR_DEB = fg(5)


def __use_colors():

    """Check if colors should be used"""

    return bool(glbl.get_generic_global('Config', 'use_colors') == '1')


def error(message):

    """Color format a message for errors"""

    if __use_colors():
        return "%s%s%s" % (COLOR_ERR, message, attr(0))
    else:
        return message


def warning(message):

    """Color format a message for warnings"""

    if __use_colors():
        return "%s%s%s" % (COLOR_WARN, message, attr(0))
    else:
        return message


def info(message):

    """Color format a message for informational messages"""

    if __use_colors():
        return "%s%s%s" % (COLOR_INFO, message, attr(0))
    else:
        return message


def verbose(message):

    """Color format a message for verbose messages"""

    if __use_colors():
        return "%s%s%s" % (COLOR_VERB, message, attr(0))
    else:
        return message


def debug(message):

    """Color format a message for debugging"""

    if __use_colors():
        return "%s%s%s" % (COLOR_DEB, message, attr(0))
    else:
        return message


def bold(message):

    """Format a bold message"""

    if __use_colors():
        return "%s%s%s" % (attr('bold'), message, attr(0))
    else:
        return message
