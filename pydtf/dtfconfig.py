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
# A class for using getprop, setprop, and delprop
import ConfigParser

def get_prop(section, prop):

    config = ConfigParser.ConfigParser()

    config.read(".dtfini")

    # Caller needs to check return if he/she cares what the issue was.
    try:
        rtn = config.get(section, prop)
    except ConfigParser.NoSectionError:
        exit(-2)
    except ConfigParser.NoOptionError:
        exit(-3)

    return rtn

def set_prop(section, prop, value):

    config = ConfigParser.ConfigParser()
    config.read(".dtfini")

    # Add section if it doesnt exist
    if not config.has_section(section):
        config.add_section(section)

    # Set the new parameter
    config.set(section, prop, value)

    f = open('.dtfini', 'w')
    config.write(f)
    f.close()

    return 0

def del_prop(section, prop):

    config = ConfigParser.ConfigParser()
    config.read(".dtfini")

    rtn = None

    # Remove the parameter
    try:
        rtn = config.remove_option(section, prop)
    except ConfigParser.NoSectionError:
        print "[WARN] Property not removed (the section did not exist)."
        exit(-2)

    if not rtn:
        print "[WARN] Property not removed (did not exist)."
        exit(-3)

    # Let's make sure we don't have an empty section now.
    if len(config.items(section)) == 0:
        config.remove_section(section)

    f = open('.dtfini', 'w')
    config.write(f)
    f.close()

    return 0
