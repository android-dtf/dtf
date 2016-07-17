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
"""Internal Package Manager"""

import dtf.globals
import dtf.logging as log

from os import chmod, remove, makedirs, mkdir
from shutil import copy, rmtree
from tempfile import NamedTemporaryFile
from zipfile import ZipFile

import imp
import os.path
import re
import sqlite3

from lxml import etree

# Eventually this will be changed
# pylint: disable=too-many-instance-attributes

TAG = "dtf_package_manager"

MANIFEST_NAME = "manifest.xml"

VALID_TYPES = ['binary', 'module', 'library', 'package']
VALID_HEALTH_VALUES = ['stable',
                       'working',
                       'beta',
                       'deprecated',
                       'broken',
                       None]

TYPE_MODULE = "module"
TYPE_LIBRARY = "library"
TYPE_BINARY = "binary"
TYPE_PACKAGE = "package"

DTF_DATA_DIR = dtf.globals.DTF_DATA_DIR
DTF_BINARIES_DIR = dtf.globals.DTF_BINARIES_DIR
DTF_LIBRARIES_DIR = dtf.globals.DTF_LIBRARIES_DIR
DTF_MODULES_DIR = dtf.globals.DTF_MODULES_DIR
DTF_PACKAGES_DIR = dtf.globals.DTF_PACKAGES_DIR
DTF_DB = dtf.globals.DTF_DB


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


# Helpers ###################################################
def file_in_zip(zip_f, file_name):

    """Determine if a file exists in a ZIP"""

    try:
        zip_f.read(file_name)
        return True
    except KeyError:
        return False


def directory_in_zip(zip_f, directory_name):

    """Determine if a directory exists in a ZIP"""

    return any(x.startswith("%s/" % directory_name.rstrip("/"))
               for x in zip_f.namelist())


def copy_zip_file(zip_f, local_name, install_name, install_dir):

    """Copy file in ZIP to directory"""

    install_path = install_dir + install_name

    log.d(TAG, "Copying '%s' to '%s'..." % (local_name, install_path))
    temp_f = NamedTemporaryFile(mode='w', delete=False)

    temp_f.write(zip_f.read(local_name))
    temp_f.flush()

    copy(temp_f.name, install_path)

    chmod(install_path, 0755)

    temp_f.close()

    remove(temp_f.name)

    log.d(TAG, "Copy complete!")

    return 0


def copy_zip_tree(zip_f, local_name, install_name, install_dir):

    """Copy directory in ZIP to directory"""

    install_path = install_dir + install_name + '/'

    # We need to remove the first one
    rmtree(install_path, ignore_errors=True)

    # Make the new directory.
    makedirs(install_path)

    for file_f in zip_f.namelist():
        # Do everything in the [local_name] dir, but not the root.
        if file_f.startswith(local_name) and file_f != local_name+'/':

            # First, we need to remove the first element.
            new_f = file_f.replace(local_name+'/', '', 1)

            # If it's a directory, make it.
            if file_f.endswith('/'):
                log.d(TAG, "Making dir %s" % install_path + new_f)
                makedirs(install_path + new_f)

            # Otherwise, we need to unzip to that new path.
            else:
                head, tail = os.path.split(new_f)
                log.d(TAG, "extracting %s to %s"
                      % (file_f, install_path + head))
                copy_zip_file(zip_f, file_f, tail, install_path + head + '/')

    log.d(TAG, "Copy complete!")

    return 0


def copy_file(local_name, install_name, install_dir):

    """Copy a file"""

    install_path = install_dir + install_name

    log.d(TAG, "Copying '%s' to '%s'..." % (local_name, install_path))
    copy(local_name, install_path)

    chmod(install_path, 0755)

    log.d(TAG, "Copy complete!")

    return 0


def copy_tree(local_name, install_name, install_dir):

    """Copy a directory recursively"""

    install_path = install_dir + install_name + '/'

    # We need to remove the first one
    rmtree(install_path, ignore_errors=True)

    # Make the new directory.
    makedirs(install_path)

    for root, dirs, files in os.walk(local_name):

        # Create new directories.
        if len(dirs) != 0:
            for local_dir in [os.path.join(root, name) for name in dirs]:
                new_dir = local_dir.replace(local_name+'/', '', 1)
                log.d(TAG, "Making dir  %s" % (install_path + new_dir))
                makedirs(install_path + new_dir)
        if len(files) != 0:
            for local_file in [os.path.join(root, name) for name in files]:
                new_file = local_file.replace(local_name+'/', '', 1)
                log.d(TAG, "Copying file '%s' to '%s'"
                      % (local_file, install_path + new_file))
                copy(local_file, install_path + new_file)

    return 0


def delete_file(file_path):

    """Delete a file"""

    try:
        remove(file_path)
        return 0
    except OSError:
        log.w(TAG, "There was an OSError when removing the file '%s'"
              % file_path)
        return 0


def delete_tree(directory_path):

    """Delete a directory recursively"""

    try:
        rmtree(directory_path)
        return 0
    except OSError:
        log.w(TAG, "OSError when removing the tree at '%s'" % directory_path)
        return 0


def get_xml_attrib(element, attrib, default=None):

    """Attempt to retrieve XML attribute"""

    try:
        return element.attrib[attrib]
    except KeyError:
        return default


def get_dict_attrib(in_dict, key, default=None):

    """Attempt to retrieve attribute from dictionary"""

    try:
        return in_dict[key]
    except KeyError:
        return default


def get_item_attrib(item, attrib):

    """Load attribute of item from DB"""

    item_type = item.type

    if item_type == TYPE_MODULE:
        table = "modules"
    elif item_type == TYPE_LIBRARY:
        table = "libraries"
    elif item_type == TYPE_BINARY:
        table = "binaries"
    elif item_type == TYPE_PACKAGE:
        table = "packages"
    else:
        log.e(TAG, "Unknown type '%s' in getItem Attribute. Returning"
              % item_type)
        return None

    dtf_db = sqlite3.connect(DTF_DB)

    cur = dtf_db.cursor()

    sql = ("SELECT %s "
           "FROM %s "
           "WHERE name='%s' "
           'LIMIT 1' % (attrib, table, item.name))

    cur.execute(sql)

    try:
        return cur.fetchone()[0]
    except TypeError:
        return None

# End helpers ###############################################


def is_bash_module(module_path):

    """Check shebang to determine bash"""

    with open(module_path, 'r') as file_f:

        shebang = file_f.readline().rstrip('\n')

        if shebang.find('bash') == -1:
            return 0
        else:
            return 1


def is_python_module(module_path, name):

    """Try to load as a Python module"""

    try:
        imp.load_source(name, module_path)
    except (NameError, SyntaxError):
        return False
    except ImportError:
        log.w(TAG, "This is a python module, but has non-existent imports!")
        return False

    return True


def parse_python_module(module_path, name):

    """Parse as a Python module"""

    module = imp.load_source(name, module_path)

    if module is None:
        log.e(TAG, "Error launching module '%s'." % name)
        return None

    try:
        mod_class = getattr(module, name)
        mod_inst = mod_class()

    except AttributeError:
        log.e(TAG, "Unable to find class '%s' in module!" % name)
        return None

    item = Item()
    item.type = TYPE_MODULE
    item.name = name
    item.local_name = module_path
    item.install_name = name
    item.author = mod_inst.author
    item.about = mod_inst.about

    health = mod_inst.health
    if health not in VALID_HEALTH_VALUES:
        log.e(TAG, "Invalid health specified. Exiting.")
        return None

    item.health = health

    version = mod_inst.version
    if version is not None:
        try:
            (item.major_version, item.minor_version) = version.split('.')
        except ValueError:
            log.e(TAG, "Version string is not valid. Exiting.")
            return None
    else:
        item.major_version = None
        item.minor_version = None

    # Remove the compiled file name
    compiled_python_file = "%sc" % module_path
    if os.path.isfile(compiled_python_file):
        remove(compiled_python_file)

    return item


def parse_bash_module(module_path, name):

    """Parse as a bash module"""

    attributes = dict()

    # Parse file for "#@", strings, store in dictionary.
    for line in open(module_path).read().split("\n"):
        match = re.match("#@[a-zA-Z ]+:.*", line)
        if match is None:
            continue

        try:
            attribute, value = match.group(0).replace("#@", "").split(":")
            value = value.lstrip(" ")
        except ValueError:
            log.w(TAG, "Unable to parse the module version, not including.")
            continue

        attributes[attribute] = value

    item = Item()
    item.type = TYPE_MODULE
    item.name = name
    item.local_name = module_path
    item.install_name = name
    item.author = get_dict_attrib(attributes, "Author")
    item.about = get_dict_attrib(attributes, "About")

    health = get_dict_attrib(attributes, "Health")
    if health not in VALID_HEALTH_VALUES:
        log.e(TAG, "Invalid health specified. Exiting.")
        return None

    item.health = health

    version = get_dict_attrib(attributes, "Version")
    if version is not None:
        try:
            (item.major_version, item.minor_version) = version.split('.')
        except ValueError:
            log.e(TAG, "Version string is not valid. Exiting.")
            return None
    else:
        item.major_version = None
        item.minor_version = None

    # Return our item.
    return item


# Getting Installed Data
def get_binaries(name_only=False):

    """Return a list of binaries"""

    bins = list()

    dtf_db = sqlite3.connect(DTF_DB)
    cur = dtf_db.cursor()

    # This just returns the name
    if name_only:

        sql = ('SELECT name '
               'FROM binaries ')

        for binary in cur.execute(sql):
            bins.append(binary[0])

    # This returns a list of items
    else:

        sql = ('SELECT name, major_version, minor_version, '
               'about, author, health '
               'FROM binaries '
               'ORDER BY name')

        cur.execute(sql)

        while True:

            item = Item()
            line = cur.fetchone()
            if line is None:
                break

            item.type = TYPE_BINARY
            item.name = line[0]
            item.major_version = line[1]
            item.minor_version = line[2]
            item.about = line[3]
            item.author = line[4]
            item.health = line[5]

            bins.append(item)

    return bins


def get_libraries(name_only=False):

    """Return a list of libraries"""

    libs = list()

    dtf_db = sqlite3.connect(DTF_DB)
    cur = dtf_db.cursor()

    # This just returns the name
    if name_only:

        sql = ('SELECT name '
               'FROM libraries ')

        for lib in cur.execute(sql):
            libs.append(lib[0])

    # This returns a list of items
    else:

        sql = ('SELECT name, major_version, minor_version, '
               'about, author, health '
               'FROM libraries '
               'ORDER BY name')

        cur.execute(sql)

        while True:

            item = Item()
            line = cur.fetchone()
            if line is None:
                break

            item.type = TYPE_LIBRARY
            item.name = line[0]
            item.major_version = line[1]
            item.minor_version = line[2]
            item.about = line[3]
            item.author = line[4]
            item.health = line[5]

            libs.append(item)

    return libs


def get_modules(name_only=False):

    """Return a list of modules"""

    mods = list()

    dtf_db = sqlite3.connect(DTF_DB)
    cur = dtf_db.cursor()

    # This just returns the name
    if name_only:

        sql = ('SELECT name '
               'FROM modules ')

        for mod in cur.execute(sql):
            mods.append(mod[0])

    # This returns a list of items
    else:

        sql = ('SELECT name, major_version, minor_version, '
               'about, author, health '
               'FROM modules '
               'ORDER BY name')

        cur.execute(sql)

        while True:

            item = Item()
            line = cur.fetchone()
            if line is None:
                break

            item.type = TYPE_MODULE
            item.name = line[0]
            item.major_version = line[1]
            item.minor_version = line[2]
            item.about = line[3]
            item.author = line[4]
            item.health = line[5]

            mods.append(item)

    return mods


def get_packages(name_only=False):

    """Return a list of packages"""

    packages = list()

    dtf_db = sqlite3.connect(DTF_DB)
    cur = dtf_db.cursor()

    # This just returns the name
    if name_only:

        sql = ('SELECT name '
               'FROM packages ')

        for pack in cur.execute(sql):
            packages.append(pack[0])

    # This returns a list of items
    else:

        sql = ('SELECT name, major_version, minor_version, '
               'about, author, health '
               'FROM packages '
               'ORDER BY name')

        cur.execute(sql)

        while True:

            item = Item()
            line = cur.fetchone()
            if line is None:
                break

            item.type = TYPE_PACKAGE
            item.name = line[0]
            item.major_version = line[1]
            item.minor_version = line[2]
            item.about = line[3]
            item.author = line[4]
            item.health = line[5]

            packages.append(item)

    return packages


def is_binary_installed(name):

    """Determine if a binary is installed"""

    return __item_installed(name, TYPE_BINARY)


def is_library_installed(name):

    """Determine if a library is installed"""

    return __item_installed(name, TYPE_LIBRARY)


def is_module_installed(name):

    """Determine if a module is installed"""

    return __item_installed(name, TYPE_MODULE)


def is_package_installed(name):

    """Determine if a package is installed"""

    return __item_installed(name, TYPE_PACKAGE)


def find_local_module(root, name):

    """Determine if a local module exists"""

    local_module_path = "%s/local_modules/%s" % (root, name)

    if os.path.isfile(local_module_path):
        return 1
    else:
        return 0

# Installing content


# INTERNAL ONLY #######################################################
def __prompt_install(local_item, installed_item):

    """Prompt user for item installation"""

    print "Installed Item Details:"
    print str(installed_item)

    print ""

    print "New Item Details:"
    print str(local_item)

    print ""
    print "Do you want to install this module? [y/N]",
    resp = raw_input()

    if resp.lower() == "y":
        return True
    else:
        return False


def __prompt_delete(installed_item):

    """Prompt user to item deletion"""

    print "Installed Item Details:"
    print str(installed_item)

    print ""
    print "Are you sure you want to delete this item (NO UNDO)? [y/N]",
    resp = raw_input()
    if resp.lower() == "y":
        return True
    else:
        return False


def __load_item(item):

    """Create new fully-loaded Item"""

    itm = Item()

    itm.name = item.name
    itm.type = item.type

    itm.install_name = get_item_attrib(item, "install_name")
    itm.local_name = None
    itm.author = get_item_attrib(item, "author")
    itm.about = get_item_attrib(item, "about")
    itm.major_version = get_item_attrib(item, "major_version")
    itm.minor_version = get_item_attrib(item, "minor_version")
    itm.health = get_item_attrib(item, "health")

    return itm


def __item_installed(name, item_type):

    """Generic test for installed content"""

    if item_type == TYPE_MODULE:
        table = "modules"
    elif item_type == TYPE_LIBRARY:
        table = "libraries"
    elif item_type == TYPE_BINARY:
        table = "binaries"
    elif item_type == TYPE_PACKAGE:
        table = "packages"
    else:
        raise KeyError

    dtf_db = sqlite3.connect(DTF_DB)

    cur = dtf_db.cursor()

    sql = ("SELECT id "
           "FROM %s "
           "WHERE name='%s' "
           'LIMIT 1' % (table, name))

    cur.execute(sql)

    if cur.fetchone() is not None:
        return True
    else:
        return False


def __process_zip_items(zip_file, items, force):

    """Process items in a ZIP"""

    for item in items:

        item_type = get_xml_attrib(item, "type")
        if item_type is None or item_type not in VALID_TYPES:
            log.e(TAG, "Found tag with no 'type' attribute, skipping!")
            continue

        if item_type not in VALID_TYPES:
            log.e(TAG, "Illegal 'type' attribute found, skipping!")
            continue

        name = get_xml_attrib(item, "name")
        if name is None:
            log.e(TAG, "Found NULL named moduled, skipping!")
            continue

        # Ok, lets start.  We can generically parse.
        local_item = Item()

        local_item.type = item_type
        local_item.major_version = get_xml_attrib(item, "majorVersion")
        local_item.minor_version = get_xml_attrib(item, "minorVersion")
        local_item.health = get_xml_attrib(item, "health")
        local_item.author = get_xml_attrib(item, "author")
        local_item.about = get_xml_attrib(item, "about")

        install_name = get_xml_attrib(item, "installName")
        local_name = get_xml_attrib(item, "localName")

        if install_name is None:
            log.d(TAG, "install_name is null, using name...")
            install_name = name
        if local_name is None:
            log.d(TAG, "local_name is null, using name...")
            local_name = name

        local_item.name = name
        local_item.install_name = install_name
        local_item.local_name = local_name

        if item_type == TYPE_BINARY:
            rtn = __install_zip_binary(zip_file, local_item, force)
        elif item_type == TYPE_LIBRARY:
            rtn = __install_zip_library(zip_file, local_item, force)
        elif item_type == TYPE_MODULE:
            rtn = __install_zip_module(zip_file, local_item, force)
        elif item_type == TYPE_PACKAGE:
            rtn = __install_zip_package(zip_file, local_item, force)

    return rtn


def __do_single_binary_install(item):

    """Perform single binary installation"""

    name = item.name
    local_name = item.local_name
    install_name = item.install_name

    # First copy the new file.
    if copy_file(local_name, install_name, DTF_BINARIES_DIR) != 0:
        log.e(TAG, "Error copying binary '%s'" % (local_name))
        return -1

    # Update database
    if __update_binary(item) == 0:
        log.e(TAG, "Failed to update binary '%s' details in database."
              % (name))
        return -2

    log.i(TAG, "Binary '%s' installed successfully!" % name)
    return 0


def __do_single_library_install(item):

    """Perform single library installation"""

    name = item.name
    local_name = item.local_name
    install_name = item.install_name

    # First copy the new tree.
    if copy_tree(local_name, install_name, DTF_LIBRARIES_DIR) != 0:
        log.e(TAG, "Error copying library '%s'" % (local_name))
        return -1

    # Update database
    if __update_library(item) == 0:
        log.e(TAG, "Failed to update library '%s' details in database."
              % (name))
        return -2

    log.i(TAG, "Library '%s' installed successfully!" % name)
    return 0


def __do_single_module_install(item):

    """Perform single module installation"""

    name = item.name
    local_name = item.local_name
    install_name = item.install_name

    # First copy the new file.
    if copy_file(local_name, install_name, DTF_MODULES_DIR) != 0:
        log.e(TAG, "Error copying module '%s'" % (local_name))
        return -1

    # Update database
    if __update_module(item) == 0:
        log.e(TAG, "Failed to update module '%s' details in database."
              % (name))
        return -2

    log.i(TAG, "Module '%s' installed successfully!" % name)
    return 0


def __do_single_package_install(item):

    """Perform single package installation"""

    name = item.name
    local_name = item.local_name
    install_name = item.install_name

    # First copy the new tree.
    if copy_tree(local_name, install_name, DTF_PACKAGES_DIR) != 0:
        log.e(TAG, "Error copying package '%s'" % (local_name))
        return -1

    # Update database
    if __update_package(item) == 0:
        log.e(TAG, "Failed to update package '%s' details in database."
              % (name))
        return -2

    log.i(TAG, "Package '%s' installed successfully!" % name)
    return 0


def __do_zip_binary_install(zip_file, item):

    """Perform the ZIP binary installation"""

    name = item.name
    local_name = item.local_name
    install_name = item.install_name

    # First copy the new file.
    if copy_zip_file(zip_file, local_name,
                     install_name, DTF_BINARIES_DIR) != 0:
        log.e(TAG, "Error copying binary '%s'" % (local_name))
        return -1

    # Update database
    if __update_binary(item) == 0:
        log.e(TAG, "Failed to update binary '%s' details in database."
              % (name))
        return -2

    return 0


def __do_zip_library_install(zip_file, item):

    """Perform the ZIP library installation"""

    name = item.name
    local_name = item.local_name
    install_name = item.install_name

    # First copy the new file.
    if copy_zip_tree(zip_file, local_name,
                     install_name, DTF_LIBRARIES_DIR) != 0:
        log.e(TAG, "Error copying library '%s'" % (local_name))
        return -1

    # Update database
    if __update_library(item) == 0:
        log.e(TAG, "Failed to update library '%s' details in database."
              % (name))
        return -2

    return 0


def __do_zip_module_install(zip_file, item):

    """Perform the ZIP module installation"""

    name = item.name
    local_name = item.local_name
    install_name = item.install_name

    # First copy the new file.
    if copy_zip_file(zip_file, local_name,
                     install_name, DTF_MODULES_DIR) != 0:
        log.e(TAG, "Error copying module '%s'" % (local_name))
        return -1

    # Update database
    if __update_module(item) == 0:
        log.e(TAG, "Failed to update module '%s' details in database."
              % (name))
        return -2

    return 0


def __do_zip_package_install(zip_file, item):

    """Perform the ZIP package installation"""

    name = item.name
    local_name = item.local_name
    install_name = item.install_name

    # First copy the new file.
    if copy_zip_tree(zip_file, local_name,
                     install_name, DTF_PACKAGES_DIR) != 0:
        log.e(TAG, "Error copying package '%s'" % (local_name))
        return -1

    # Update database
    if __update_package(item) == 0:
        log.e(TAG, "Failed to update package '%s' details in database."
              % (name))
        return -2

    return 0


def __install_zip_binary(zip_file, item, force_mode):

    """Install a binary from a ZIP"""

    rtn = 0

    # Does the resource even exist?
    if not file_in_zip(zip_file, item.local_name):
        log.w(TAG, "'%s' defined, but local file '%s' does not exist!"
              % (item.name, item.local_name))
        return -1

    try:
        # First check if we know about this binary
        if is_binary_installed(item.name):

            # Prompt for install.
            if not force_mode:
                print ("[WARNING] An item with this name is already installed."
                       " See details below.")

                installed_item = __load_item(item)

                if __prompt_install(item, installed_item):
                    log.d(TAG, "User would like to install")
                    rtn = __do_zip_binary_install(zip_file, item)
                else:
                    log.i(TAG, "Binary installation skipped.")
            # Force
            else:
                log.d(TAG, "Forcing component installation.")
                rtn = __do_zip_binary_install(zip_file, item)
        else:
            log.d(TAG, "This is a new binary, installing.")
            rtn = __do_zip_binary_install(zip_file, item)

    except KeyError:
        log.w(TAG, "Error checking if the binary was installed. Skipping")
        rtn = -4

    return rtn


def __install_zip_library(zip_file, item, force_mode):

    """Install a library from a ZIP"""

    rtn = 0

    # Does the resource even exist?
    if not directory_in_zip(zip_file, item.local_name):
        log.w(TAG, "'%s' defined, but directory '%s' does not exist!"
              % (item.name, item.local_name))
        return -1

    try:
        # First check if we know about this library
        if is_library_installed(item.name):

            # Prompt for install.
            if not force_mode:
                print ("[WARNING] An item with this name is already installed."
                       " See details below.")

                installed_item = __load_item(item)

                if __prompt_install(item, installed_item):
                    log.d(TAG, "User would like to install")
                    rtn = __do_zip_library_install(zip_file, item)
                else:
                    log.i(TAG, "Library installation skipped.")
            # Force
            else:
                log.d(TAG, "Forcing component installation.")
                rtn = __do_zip_library_install(zip_file, item)
        else:
            log.d(TAG, "This is a new library, installing.")
            rtn = __do_zip_library_install(zip_file, item)

    except KeyError:
        log.w(TAG, "Error checking if the library was installed. Skipping")
        rtn = -4

    return rtn


def __install_zip_module(zip_file, item, force_mode):

    """Install a module from a ZIP"""

    rtn = 0

    # Does the resource even exist?
    if not file_in_zip(zip_file, item.local_name):
        log.w(TAG, "'%s' defined, but local file '%s' does not exist!"
              % (item.name, item.local_name))
        return -1

    try:
        # First check if we know about this module
        if is_module_installed(item.name):

            # Prompt for install.
            if not force_mode:
                print ("[WARNING] An item with this name is already installed."
                       " See details below.")

                installed_item = __load_item(item)

                if __prompt_install(item, installed_item):
                    log.d(TAG, "User would like to install")
                    rtn = __do_zip_module_install(zip_file, item)
                else:
                    log.i(TAG, "Module installation skipped.")
            # Force
            else:
                log.d(TAG, "Forcing component installation.")
                rtn = __do_zip_module_install(zip_file, item)
        else:
            log.d(TAG, "This is a new module, installing.")
            rtn = __do_zip_module_install(zip_file, item)

    except KeyError:
        log.w(TAG, "Error checking if the module was installed. Skipping")
        rtn = -4

    return rtn


def __install_zip_package(zip_file, item, force_mode):

    """Install a package from a ZIP"""

    rtn = 0

    # Does the resource even exist?
    if not directory_in_zip(zip_file, item.local_name):
        log.w(TAG, "'%s' defined, but directory '%s' does not exist!"
              % (item.name, item.local_name))
        return -1

    try:
        # First check if we know about this package
        if is_package_installed(item.name):

            # Prompt for install.
            if not force_mode:
                print ("[WARNING] An item with this name is already installed."
                       " See details below.")

                installed_item = __load_item(item)

                if __prompt_install(item, installed_item):
                    log.d(TAG, "User would like to install")
                    rtn = __do_zip_package_install(zip_file, item)
                else:
                    log.i(TAG, "Package installation skipped.")
            # Force
            else:
                log.d(TAG, "Forcing component installation.")
                rtn = __do_zip_package_install(zip_file, item)
        else:
            log.d(TAG, "This is a new package, installing.")
            rtn = __do_zip_package_install(zip_file, item)

    except KeyError:
        log.w(TAG, "Error checking if the package was installed. Skipping")
        rtn = -4

    return rtn


def __update_binary(item):

    """Update a binary in the DB"""

    conn = sqlite3.connect(DTF_DB)
    cur = conn.cursor()

    # Remove the line first.
    sql = ('DELETE FROM binaries '
           "WHERE name='%s'" % item.name)

    cur.execute(sql)

    entry = [(item.name, item.major_version, item.minor_version, item.author,
              item.health, item.install_name)]

    # Update a Binary Entry
    sql = ('INSERT INTO binaries (name, major_version, minor_version, '
           'author, health, install_name)'
           'VALUES (?, ?, ?, ?, ?, ?)')

    cur.executemany(sql, entry)
    conn.commit()

    return cur.rowcount


def __update_library(item):

    """Update a library in the DB"""

    conn = sqlite3.connect(DTF_DB)
    cur = conn.cursor()

    # Remove the line first.
    sql = ('DELETE FROM libraries '
           "WHERE name='%s'" % item.name)

    cur.execute(sql)

    entry = [(item.name, item.major_version, item.minor_version, item.author,
              item.health, item.install_name)]

    # Update a Library Entry
    sql = ('INSERT INTO libraries (name, major_version, minor_version, '
           'author, health, install_name)'
           'VALUES (?, ?, ?, ?, ?, ?)')

    cur.executemany(sql, entry)
    conn.commit()

    return cur.rowcount


def __update_module(item):

    """Update module in the DB"""

    conn = sqlite3.connect(DTF_DB)
    cur = conn.cursor()

    # Remove the line first.
    sql = ('DELETE FROM modules '
           "WHERE name='%s'" % item.name)

    cur.execute(sql)

    entry = [(item.name, item.about, item.major_version, item.minor_version,
              item.author, item.health, item.install_name)]

    # Update a Module Entry
    sql = ('INSERT INTO modules (name, about, major_version, minor_version, '
           'author, health, install_name)'
           'VALUES (?, ?, ?, ?, ?, ?, ?)')

    cur.executemany(sql, entry)
    conn.commit()

    return cur.rowcount


def __update_package(item):

    """Update package in the DB"""

    conn = sqlite3.connect(DTF_DB)
    cur = conn.cursor()

    # Remove the line first.
    sql = ('DELETE FROM packages '
           "WHERE name='%s'" % item.name)

    cur.execute(sql)

    entry = [(item.name, item.major_version, item.minor_version, item.author,
              item.health, item.install_name)]

    # Update a Package Entry
    sql = ('INSERT INTO packages (name, major_version, minor_version, '
           'author, health, install_name)'
           'VALUES (?, ?, ?, ?, ?, ?)')

    cur.executemany(sql, entry)
    conn.commit()

    return cur.rowcount


def __do_binary_delete(item):

    """Perform the binary removal"""

    file_path = DTF_BINARIES_DIR + item.install_name

    if delete_file(file_path) != 0:
        log.e(TAG, "Error removing binary file! Continuing.")

    conn = sqlite3.connect(DTF_DB)
    cur = conn.cursor()

    # Remove the line first.
    sql = ('DELETE FROM binaries '
           "WHERE name='%s'" % item.name)

    cur.execute(sql)
    conn.commit()

    return cur.rowcount


def __do_library_delete(item):

    """Perform the library removal"""

    file_path = DTF_LIBRARIES_DIR + item.install_name

    if delete_tree(file_path) != 0:
        log.e(TAG, "Error removing tree! Continuing.")

    conn = sqlite3.connect(DTF_DB)
    cur = conn.cursor()

    # Remove the line first.
    sql = ('DELETE FROM libraries '
           "WHERE name='%s'" % item.name)

    cur.execute(sql)
    conn.commit()

    return cur.rowcount


def __do_module_delete(item):

    """Perform the module removal"""

    file_path = DTF_MODULES_DIR + item.install_name

    if delete_file(file_path) != 0:
        log.e(TAG, "Error removing module file! Continuing.")

    conn = sqlite3.connect(DTF_DB)
    cur = conn.cursor()

    # Remove the line first.
    sql = ('DELETE FROM modules '
           "WHERE name='%s'" % item.name)

    cur.execute(sql)
    conn.commit()

    return cur.rowcount


def __do_package_delete(item):

    """Perform the package removal"""

    file_path = DTF_PACKAGES_DIR + item.install_name

    if delete_tree(file_path) != 0:
        log.e(TAG, "Error removing tree! Continuing.")

    conn = sqlite3.connect(DTF_DB)
    cur = conn.cursor()

    # Remove the line first.
    sql = ('DELETE FROM packages '
           "WHERE name='%s'" % item.name)

    cur.execute(sql)
    conn.commit()

    return cur.rowcount
# End INTERNAL #####################################################


# Database Initialization ##########################################
def initialize_db():

    """Initialize dtf main.db"""

    dtf_db = sqlite3.connect(DTF_DB)

    # Create Binaries Table
    sql = ('CREATE TABLE IF NOT EXISTS binaries'
           '('
           'id INTEGER PRIMARY KEY AUTOINCREMENT, '
           'name TEXT UNIQUE NOT NULL, '
           'about TEXT, '
           'major_version TEXT, '
           'minor_version TEXT, '
           'author TEXT, '
           'health TEXT,'
           'install_name TEXT'
           ')')

    rtn = dtf_db.execute(sql)

    if not rtn:
        log.e(TAG, "Error creating binaries table, exiting")
        return rtn

    # Create Libraries Table
    sql = ('CREATE TABLE IF NOT EXISTS libraries'
           '('
           'id INTEGER PRIMARY KEY AUTOINCREMENT, '
           'name TEXT UNIQUE NOT NULL, '
           'about TEXT, '
           'major_version TEXT, '
           'minor_version TEXT, '
           'author TEXT, '
           'health TEXT, '
           'install_name TEXT'
           ')')

    rtn = dtf_db.execute(sql)

    if not rtn:
        log.e(TAG, "Error creating libraries table, exiting")
        return rtn

    # Create Modules Table
    sql = ('CREATE TABLE IF NOT EXISTS modules'
           '('
           'id INTEGER PRIMARY KEY AUTOINCREMENT, '
           'name TEXT UNIQUE NOT NULL, '
           'about TEXT, '
           'major_version TEXT, '
           'minor_version TEXT, '
           'author TEXT, '
           'health TEXT, '
           'install_name TEXT'
           ')')

    rtn = dtf_db.execute(sql)

    if not rtn:
        log.e(TAG, "Error creating modules table, exiting")
        return rtn

    # Create Packages Table
    sql = ('CREATE TABLE IF NOT EXISTS packages'
           '('
           'id INTEGER PRIMARY KEY AUTOINCREMENT, '
           'name TEXT UNIQUE NOT NULL, '
           'about TEXT, '
           'major_version TEXT, '
           'minor_version TEXT, '
           'author TEXT, '
           'health TEXT, '
           'install_name TEXT'
           ')')

    rtn = dtf_db.execute(sql)

    if not rtn:
        log.e(TAG, "Error creating packages table, exiting")
        return rtn

    dtf_db.commit()
    dtf_db.close()

    return 0


def create_data_dirs():

    """Create the .dtf/ directory structure"""

    # First create the main dir.
    if not os.path.isdir(DTF_DATA_DIR):

        try:
            mkdir(DTF_DATA_DIR)
        except OSError:
            log.e(TAG, "Unable to create dtf data directory!")
            return -6

    # Now the subdirectories. Be less strict about errors for these.
    try:
        mkdir(DTF_MODULES_DIR)
        mkdir(DTF_PACKAGES_DIR)
        mkdir(DTF_BINARIES_DIR)
        mkdir(DTF_LIBRARIES_DIR)
    except OSError:
        pass

    return 0
# End Initialization ###############################################


# Package Installation #############################################
def install_single_binary(item, force=False):

    """Install a single binary"""

    rtn = 0

    try:
        # First check if we know about this binary
        if is_binary_installed(item.name):

            # Prompt for install.
            if not force:
                print ("[WARNING] An item with this name is already installed."
                       " See details below.")

                installed_item = __load_item(item)

                if __prompt_install(item, installed_item):
                    log.d(TAG, "User would like to install")
                    rtn = __do_single_binary_install(item)
                else:
                    log.i(TAG, "Binary installation skipped.")
            # Force
            else:
                log.d(TAG, "Forcing component installation.")
                rtn = __do_single_binary_install(item)
        else:
            log.d(TAG, "This is a new binary, installing.")
            rtn = __do_single_binary_install(item)

    except KeyError:
        log.w(TAG, "Error checking if the binary was installed. Skipping")
        rtn = -4

    return rtn


def install_single_library(item, force=False):

    """Install a single library"""

    rtn = 0

    try:
        # First check if we know about this libraary
        if is_library_installed(item.name):

            # Prompt for install.
            if not force:
                print ("[WARNING] An item with this name is already installed."
                       " See details below.")

                installed_item = __load_item(item)

                if __prompt_install(item, installed_item):
                    log.d(TAG, "User would like to install")
                    rtn = __do_single_library_install(item)
                else:
                    log.i(TAG, "Library installation skipped.")
            # Force
            else:
                log.d(TAG, "Forcing component installation.")
                rtn = __do_single_library_install(item)
        else:
            log.d(TAG, "This is a new library, installing.")
            rtn = __do_single_library_install(item)

    except KeyError:
        log.w(TAG, "Error checking if the library was installed. Skipping")
        rtn = -4

    return rtn


def install_single_module(item, force=False):

    """Install a single module"""

    rtn = 0

    try:
        # First check if we know about this module
        if is_module_installed(item.name):

            # Prompt for install.
            if not force:
                print ("[WARNING] An item with this name is already installed."
                       " See details below.")

                installed_item = __load_item(item)

                if __prompt_install(item, installed_item):
                    log.d(TAG, "User would like to install")
                    rtn = __do_single_module_install(item)
                else:
                    log.i(TAG, "Module installation skipped.")
            # Force
            else:
                log.d(TAG, "Forcing component installation.")
                rtn = __do_single_module_install(item)
        else:
            log.d(TAG, "This is a new module, installing.")
            rtn = __do_single_module_install(item)

    except KeyError:
        log.w(TAG, "Error checking if the module was installed. Skipping")
        rtn = -4

    return rtn


def install_single_package(item, force=False):

    """Install a single package"""

    rtn = 0

    try:
        # First check if we know about this package
        if is_binary_installed(item.name):

            # Prompt for install.
            if not force:
                print ("[WARNING] An item with this name is already installed."
                       " See details below.")

                installed_item = __load_item(item)

                if __prompt_install(item, installed_item):
                    log.d(TAG, "User would like to install")
                    rtn = __do_single_package_install(item)
                else:
                    log.i(TAG, "Package installation skipped.")
            # Force
            else:
                log.d(TAG, "Forcing component installation.")
                rtn = __do_single_package_install(item)
        else:
            log.d(TAG, "This is a new package, installing.")
            rtn = __do_single_package_install(item)

    except KeyError:
        log.w(TAG, "Error checking if the package was installed. Skipping")
        rtn = -4

    return rtn


def install_zip(zip_file_name, force=False):

    """Install a ZIP file"""

    rtn = 0
    manifest_data = None
    manifest_root = None

    zip_f = ZipFile(zip_file_name, 'r')

    log.d(TAG, "Parsing manifest file...")

    # Get Manifest
    if not file_in_zip(zip_f, MANIFEST_NAME):
        log.e(TAG, "Error extracting '%s' from ZIP archive - does it exist?"
              % (MANIFEST_NAME))
        return -3

    manifest_data = zip_f.read(MANIFEST_NAME)

    # Read Manifest
    try:
        manifest_root = etree.XML(manifest_data)
    except etree.XMLSyntaxError:
        log.e(TAG, "Error parsing XML file '%s'! Exiting."
              % MANIFEST_NAME)
        return -4

    # Processing Stuff
    items = manifest_root.xpath("/Items/Item")

    rtn = __process_zip_items(zip_f, items, force)

    if rtn == 0:
        log.i(TAG, "ZIP content '%s' installed successfully!"
              % zip_file_name)
    else:
        log.e(TAG, "Unable to install ZIP file: %d" % rtn)

    return rtn

# End Package Installation ##############################################


# Removing Content ######################################################
def delete_binary(name, force=False):

    """Remove a binary"""

    rtn = 0

    # First check if we know about the binary
    if is_binary_installed(name):

        item = Item()
        item.name = name
        item.type = TYPE_BINARY

        installed_item = __load_item(item)

        # Prompt for removal
        if not force:

            if __prompt_delete(installed_item):
                log.d(TAG, "User would like to remove")
                rtn = __do_binary_delete(installed_item)
            else:
                log.i(TAG, "Binary deletion skipped.")
        # Force
        else:
            log.d(TAG, "Forcing component removal.")
            rtn = __do_binary_delete(installed_item)
    else:
        log.e(TAG, "No binary installed with this name.")
        rtn = -1

    return rtn


def delete_library(name, force=False):

    """Remove a library"""

    rtn = 0

    # First check if we know about the library
    if is_library_installed(name):

        item = Item()
        item.name = name
        item.type = TYPE_LIBRARY

        installed_item = __load_item(item)

        # Prompt for removal
        if not force:

            if __prompt_delete(installed_item):
                log.d(TAG, "User would like to remove")
                rtn = __do_library_delete(installed_item)
            else:
                log.i(TAG, "Library deletion skipped.")
        # Force
        else:
            log.d(TAG, "Forcing component removal.")
            rtn = __do_library_delete(installed_item)
    else:
        log.e(TAG, "No library installed with this name.")
        rtn = -1

    return rtn


def delete_module(name, force=False):

    """Remove a module"""

    rtn = 0

    # First check if we know about the module
    if is_module_installed(name):

        item = Item()
        item.name = name
        item.type = TYPE_MODULE

        installed_item = __load_item(item)

        # Prompt for removal
        if not force:

            if __prompt_delete(installed_item):
                log.d(TAG, "User would like to remove")
                rtn = __do_module_delete(installed_item)
            else:
                log.i(TAG, "Module deletion skipped.")
        # Force
        else:
            log.d(TAG, "Forcing component removal.")
            rtn = __do_module_delete(installed_item)
    else:
        log.e(TAG, "No module installed with this name.")
        rtn = -1

    return rtn


def delete_package(name, force=False):

    """Remove a package"""

    rtn = 0

    # First check if we know about the package
    if is_package_installed(name):

        item = Item()
        item.name = name
        item.type = TYPE_PACKAGE

        installed_item = __load_item(item)

        # Prompt for removal
        if not force:

            if __prompt_delete(installed_item):
                log.d(TAG, "User would like to remove")
                rtn = __do_package_delete(installed_item)
            else:
                log.i(TAG, "Package deletion skipped.")
        # Force
        else:
            log.d(TAG, "Forcing component removal.")
            rtn = __do_package_delete(installed_item)
    else:
        log.e(TAG, "No package installed with this name.")
        rtn = -1

    return rtn


# Database Removal ######################################################
def purge():

    """Perform database purge"""

    log.i(TAG, "Starting purge....")

    dtf_db = sqlite3.connect(DTF_DB)
    cur = dtf_db.cursor()

    # Remove Binaries
    sql = ('SELECT name, install_name '
           'FROM binaries')

    for row in cur.execute(sql):

        binary_name = row[0]
        install_name = row[1]
        full_path = DTF_BINARIES_DIR + install_name
        log.d(TAG, "Removing binary '%s'" % binary_name)

        if delete_file(full_path) != 0:
            log.e(TAG, "Error removing binary file! Continuing.")

    # Remove Libraries
    sql = ('SELECT name, install_name '
           'FROM libraries')

    for row in cur.execute(sql):

        library_name = row[0]
        install_name = row[1]
        full_path = DTF_LIBRARIES_DIR + install_name
        log.d(TAG, "Removing library '%s'" % library_name)

        if delete_tree(full_path) != 0:
            log.e(TAG, "Error removing library! Continuing.")

    # Remove Modules
    sql = ('SELECT name, install_name '
           'FROM modules')

    for row in cur.execute(sql):

        module_name = row[0]
        install_name = row[1]
        full_path = DTF_MODULES_DIR + install_name
        log.d(TAG, "Removing module '%s'" % module_name)

        if delete_file(full_path) != 0:
            log.e(TAG, "Error removing module file! Continuing.")

    # Remove Packages
    sql = ('SELECT name, install_name '
           'FROM packages')

    for row in cur.execute(sql):

        package_name = row[0]
        install_name = row[1]
        full_path = DTF_PACKAGES_DIR + install_name
        log.d(TAG, "Removing package '%s'" % package_name)

        if delete_tree(full_path) != 0:
            log.e(TAG, "Error removing package! Continuing.")

    # Drop the DB.
    cur.execute("DROP TABLE IF EXISTS binaries")
    cur.execute("DROP TABLE IF EXISTS libraries")
    cur.execute("DROP TABLE IF EXISTS modules")
    cur.execute("DROP TABLE IF EXISTS packages")

    dtf_db.commit()

    # Rebuilding
    if initialize_db() != 0:
        log.e(TAG, "Unable to re-create dtf db!")
        return -1

    log.i(TAG, "Purge complete!")
    return 0

# End Database Removal ##################################################
