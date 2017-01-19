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
"""dtf property support"""

from __future__ import absolute_import
from os.path import abspath, join, isfile
from os import getcwd, pardir

import configparser

import dtf.core.utils as utils
import dtf.logging as log

CONFIG_FILE_NAME = utils.CONFIG_FILE_NAME

TAG = "dtf-properties"


class PropertyError(Exception):

    """General exception for properties"""
    pass


def __upsearch(file_name, dir_name):

    """Search upward for file"""

    if isfile("%s/%s" % (dir_name, file_name)):
        return dir_name
    else:
        new_dir = abspath(join(dir_name, pardir))
        if dir_name == new_dir:
            return None
        return __upsearch(file_name, new_dir)

TOP = __upsearch(CONFIG_FILE_NAME, getcwd())


def __load_config():

    """Load the current project configuration"""

    config = configparser.ConfigParser()
    config.read(CONFIG_FILE_NAME)

    return config


def __update_config(config):

    """Update config file"""

    prop_f = open(CONFIG_FILE_NAME, 'w')
    config.write(prop_f)
    prop_f.close()


def get_prop(section, prop):

    """Get a property value"""

    config = __load_config()
    section = section.capitalize()

    # Caller needs to check return if he/she cares what the issue was.
    try:
        rtn = config.get(section, prop)
    except configparser.NoSectionError:
        err = "Property section not found: %s" % section
        raise PropertyError(err)
    except configparser.NoOptionError:
        err = r"Property not found: %s\%s" % (section, prop)
        raise PropertyError(err)

    return rtn


def set_prop(section, prop, value):

    """Set a property"""

    config = __load_config()
    section = section.capitalize()

    # Add section if it doesnt exist
    if not config.has_section(section):
        config.add_section(section)

    # Set the new parameter
    config.set(section, prop, value)

    __update_config(config)

    return 0


def del_prop(section, prop):

    """Delete a property"""

    config = __load_config()
    section = section.capitalize()

    rtn = None

    # Remove the parameter
    try:
        rtn = config.remove_option(section, prop)
    except configparser.NoSectionError:
        log.w(TAG, "Property not removed (the section did not exist).")
        return -1

    if not rtn:
        log.w(TAG, "Property not removed (did not exist).")
        return -2

    # Let's make sure we don't have an empty section now.
    if len(config.items(section)) == 0:
        config.remove_section(section)

    __update_config(config)

    return 0


def test_prop(section, prop):

    """Test if a property is set or not"""

    config = __load_config()
    section = section.capitalize()
    rtn = 0

    try:
        config.get(section, prop)
        rtn = 1
    except configparser.NoSectionError:
        rtn = 0
    except configparser.NoOptionError:
        rtn = 0

    return rtn
