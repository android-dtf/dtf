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
"""Global dtf locations"""

from __future__ import absolute_import
import os.path

import configparser

import dtf.core.utils as utils

DTF_DATA_DIR = utils.get_dtf_data_dir()
DTF_BINARIES_DIR = DTF_DATA_DIR + "/binaries/"
DTF_LIBRARIES_DIR = DTF_DATA_DIR + "/libraries/"
DTF_MODULES_DIR = DTF_DATA_DIR + "/modules/"
DTF_PACKAGES_DIR = DTF_DATA_DIR + "/packages/"
DTF_DB = DTF_DATA_DIR + "/main.db"

DTF_INCLUDED_DIR = DTF_DATA_DIR + "/included"
DTF_GLOBAL_CONFIG = DTF_INCLUDED_DIR + "/globals.ini"


class GlobalPropertyError(Exception):

    """General exception for global properties"""
    pass


def get_binding(dtf_binding):

    """Read binding from global config"""

    return os.path.expanduser(get_generic_global("Bindings", dtf_binding))


def get_all_bindings():

    """Get all bindings"""

    return __get_section("Bindings")


def get_generic_global(section, prop):

    """Generic getter for getting a property"""

    if section is None:
        raise GlobalPropertyError("Section cannot be null!")
    elif prop is None:
        raise GlobalPropertyError("Property cannot be null!")

    global_conf = configparser.ConfigParser()
    global_conf.read(DTF_GLOBAL_CONFIG)

    try:
        return global_conf.get(section, prop)
    except configparser.NoSectionError:
        raise GlobalPropertyError("Section not found: %s" % section)
    except configparser.NoOptionError:
        raise GlobalPropertyError("Property not found: %s" % prop)


def __get_section(section):

    """Private helper to get all section values"""

    if section is None:
        raise GlobalPropertyError("Section cannot be null!")

    global_conf = configparser.ConfigParser()
    global_conf.read(DTF_GLOBAL_CONFIG)

    if not global_conf.has_section(section):
        raise GlobalPropertyError("Section not found: %s" % section)

    return global_conf.items(section)
