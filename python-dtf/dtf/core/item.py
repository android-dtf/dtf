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

import semantic_version

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


def is_valid_version(version_string):

    """Check if version string is correct"""

    try:
        semantic_version.Version(version_string)
    except ValueError:
        return False

    return True


def item_is_newer(installed_item, item):

    """Determine if an item is newer"""

    return bool(semantic_version.Version(installed_item.version)
                < semantic_version.Version(item.version))


class Item(object):  # pylint: disable=too-few-public-methods

    """Class for working with content"""

    install_name = None
    local_name = None
    name = None
    type = type
    author = None
    about = None
    version = None
    health = None

    def __init__(self):

        """Initialize new object"""

        self.install_name = None
        self.local_name = None
        self.name = None
        self.type = None
        self.author = None
        self.about = None
        self.version = None
        self.health = None

    def __repr__(self):

        """Tostring for item"""

        temp = "Name: %s (%s)\n" % (self.name, self.type)
        if self.type == TYPE_MODULE:
            temp += "  About: %s\n" % self.about
        temp += "  Installs as: %s\n" % self.install_name
        temp += "  Author: %s\n" % self.author
        temp += "  Version: %s\n" % self.version
        temp += "  Health: %s" % self.health
        return temp
