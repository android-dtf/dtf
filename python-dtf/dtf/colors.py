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

COLOR_ERR = fg(1)
COLOR_WARN = fg(3)
COLOR_INFO = fg(2)
COLOR_VERB = fg(6)
COLOR_DEB = fg(5)


def error(message):

    """Color format a message for errors"""

    return "%s%s%s" % (COLOR_ERR, message, attr(0))


def warning(message):

    """Color format a message for warnings"""

    return "%s%s%s" % (COLOR_WARN, message, attr(0))


def info(message):

    """Color format a message for informational messages"""

    return "%s%s%s" % (COLOR_INFO, message, attr(0))


def verbose(message):

    """Color format a message for verbose messages"""

    return "%s%s%s" % (COLOR_VERB, message, attr(0))


def debug(message):

    """Color format a message for debugging"""

    return "%s%s%s" % (COLOR_DEB, message, attr(0))
