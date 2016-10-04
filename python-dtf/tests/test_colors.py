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
"""pytest for using dtf coloring"""

import common
import pytest

import dtf.colors as colors

TAG = 'test_colors'


def test_error():

    """Log an error message"""

    print "This message is an %s" % colors.error("error.")


def test_warning():

    """Log an warning message"""

    print "This message is a %s" % colors.warning("warning.")


def test_info():

    """Log an info message"""

    print "This message is a %s" % colors.info("info message.")


def test_verbose():

    """Log an verbose message"""

    print "This message is a %s" % colors.verbose("verbose message.")


def test_debug():

    """Log an debug message"""

    print "This message is a %s" % colors.debug("debug message.")

def test_bold():

    """Log a bolded message"""

    print "This message is %s" % colors.bold("important!")
