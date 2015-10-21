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

import ConfigParser

import dtf.core.utils as utils
import dtf.logging as log

CONFIG_FILE_NAME = utils.CONFIG_FILE_NAME

TAG = "dtf-properties"

class PropertyError(Exception):

    """General exception for properties"""

    pass

def get_prop(section, prop):

    """Get a property value"""

    config = ConfigParser.ConfigParser()

    config.read(CONFIG_FILE_NAME)

    # Caller needs to check return if he/she cares what the issue was.
    try:
        rtn = config.get(section, prop)
    except ConfigParser.NoSectionError:
        raise PropertyError("Property section not found: %s" % section)
    except ConfigParser.NoOptionError:
        raise PropertyError("Property not found: %s\\%s" % (section, prop))

    return rtn

def set_prop(section, prop, value):

    """Set a property"""

    config = ConfigParser.ConfigParser()
    config.read(CONFIG_FILE_NAME)

    # Add section if it doesnt exist
    if not config.has_section(section):
        config.add_section(section)

    # Set the new parameter
    config.set(section, prop, value)

    prop_f = open(CONFIG_FILE_NAME, 'w')
    config.write(prop_f)
    prop_f.close()

    return 0

def del_prop(section, prop):

    """Delete a property"""

    config = ConfigParser.ConfigParser()
    config.read(CONFIG_FILE_NAME)

    rtn = None

    # Remove the parameter
    try:
        rtn = config.remove_option(section, prop)
    except ConfigParser.NoSectionError:
        log.w(TAG, "Property not removed (the section did not exist).")
        return -1

    if not rtn:
        log.w(TAG, "Property not removed (did not exist).")
        return -2

    # Let's make sure we don't have an empty section now.
    if len(config.items(section)) == 0:
        config.remove_section(section)

    prop_f = open(CONFIG_FILE_NAME, 'w')
    config.write(prop_f)
    prop_f.close()

    return 0

def test_prop(section, prop):

    """Test if a property is set or not"""

    config = ConfigParser.ConfigParser()
    config.read(CONFIG_FILE_NAME)

    try:
        config.get(section, prop)
        return 1
    except ConfigParser.NoSectionError:
        return 0
    except ConfigParser.NoOptionError:
        return 0

    # Some other error?
    return 0
