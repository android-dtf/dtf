# Android Device Testing Framework ("dtf")
# Copyright 2013-2017 Jake Valletta (@jake_valletta)
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
"""Item class"""

# Eventually this will be changed
# pylint: disable=too-many-instance-attributes


VALID_HEALTH_VALUES = ['stable',
                       'working',
                       'beta',
                       'deprecated',
                       'broken',
                       None]

TYPE_MODULE = 'module'
TYPE_LIBRARY = 'library'
TYPE_BINARY = 'binary'
TYPE_PACKAGE = 'package'

VALID_TYPES = [TYPE_BINARY, TYPE_LIBRARY,
               TYPE_MODULE, TYPE_PACKAGE]


class Item(object):  # pylint: disable=too-few-public-methods

    """Class for working with content"""

    install_name = None
    local_name = None
    name = None
    type = type
    author = None
    about = None
    major_version = None
    minor_version = None
    health = None

    def __init__(self):

        """Initialize new object"""

        self.install_name = None
        self.local_name = None
        self.name = None
        self.type = None
        self.author = None
        self.about = None
        self.major_version = None
        self.minor_version = None
        self.health = None

    def make_version(self):

        """Create version string"""

        if self.major_version is None and self.minor_version is None:
            return None
        else:
            if self.major_version is None:
                mjr = "0"
            else:
                mjr = self.major_version

            if self.minor_version is None:
                mnr = "0"
            else:
                mnr = self.minor_version

            return "%s.%s" % (mjr, mnr)

    def __repr__(self):

        """Tostrig for item"""

        temp = "Name: %s (%s)\n" % (self.name, self.type)
        if self.type == TYPE_MODULE:
            temp += "  About: %s\n" % self.about
        temp += "  Installs as: %s\n" % self.install_name
        temp += "  Author: %s\n" % self.author
        temp += "  Version: %s\n" % self.make_version()
        temp += "  Health: %s" % self.health
        return temp
