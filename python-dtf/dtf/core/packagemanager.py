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

import imp
import os
import os.path
import re
import sqlite3
from shutil import copy, rmtree

import dtf.globals
import dtf.logging as log
import dtf.core.item
import dtf.core.manifestparser as mp
import dtf.core.utils as utils

TAG = "dtf_package_manager"

MANIFEST_NAME = "manifest.xml"

DTF_DATA_DIR = dtf.globals.DTF_DATA_DIR
DTF_BINARIES_DIR = dtf.globals.DTF_BINARIES_DIR
DTF_LIBRARIES_DIR = dtf.globals.DTF_LIBRARIES_DIR
DTF_MODULES_DIR = dtf.globals.DTF_MODULES_DIR
DTF_PACKAGES_DIR = dtf.globals.DTF_PACKAGES_DIR
DTF_DB = dtf.globals.DTF_DB


# Helpers ###################################################
def copy_file(local_name, install_name, install_dir):

    """Copy a file"""

    install_path = install_dir + install_name

    log.d(TAG, "Copying '%s' to '%s'..." % (local_name, install_path))
    copy(local_name, install_path)

    os.chmod(install_path, 0755)

    log.d(TAG, "Copy complete!")

    return 0


def copy_tree(local_name, install_name, install_dir):

    """Copy a directory recursively"""

    install_path = install_dir + install_name + '/'

    # We need to remove the first one
    rmtree(install_path, ignore_errors=True)

    # Make the new directory.
    os.makedirs(install_path)

    for root, dirs, files in os.walk(local_name):

        # Create new directories.
        if len(dirs) != 0:
            for local_dir in [os.path.join(root, name) for name in dirs]:
                new_dir = local_dir.replace(local_name+'/', '', 1)
                log.d(TAG, "Making dir  %s" % (install_path + new_dir))
                os.makedirs(install_path + new_dir)
        if len(files) != 0:
            for local_file in [os.path.join(root, name) for name in files]:
                new_file = local_file.replace(local_name+'/', '', 1)
                log.d(TAG, "Copying file '%s' to '%s'"
                      % (local_file, install_path + new_file))
                copy(local_file, install_path + new_file)

    return 0


def get_dict_attrib(in_dict, key, default=None):

    """Attempt to retrieve attribute from dictionary"""

    try:
        return in_dict[key]
    except KeyError:
        return default


def get_item_attrib(item, attrib):

    """Load attribute of item from DB"""

    item_type = item.type

    if item_type == dtf.core.item.TYPE_MODULE:
        table = "modules"
    elif item_type == dtf.core.item.TYPE_LIBRARY:
        table = "libraries"
    elif item_type == dtf.core.item.TYPE_BINARY:
        table = "binaries"
    elif item_type == dtf.core.item.TYPE_PACKAGE:
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

        if re.match("^#!/.*sh$", shebang):
            return 1
        else:
            return 0


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

    item = dtf.core.item.Item()
    item.type = dtf.core.item.TYPE_MODULE
    item.name = name
    item.local_name = module_path
    item.install_name = name
    item.author = mod_inst.author
    item.about = mod_inst.about

    health = mod_inst.health
    if health not in dtf.core.item.VALID_HEALTH_VALUES:
        log.e(TAG, "Invalid health specified. Exiting.")
        return None

    item.health = health

    version = mod_inst.version
    if version is not None:
        if dtf.core.item.is_valid_version(version):
            item.version = version
        else:
            log.e(TAG, "Invalid version specified. Exiting.")
            return None
    else:
        item.version = None

    # Remove the compiled file name
    compiled_python_file = "%sc" % module_path
    if os.path.isfile(compiled_python_file):
        os.remove(compiled_python_file)

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

    item = dtf.core.item.Item()
    item.type = dtf.core.item.TYPE_MODULE
    item.name = name
    item.local_name = module_path
    item.install_name = name
    item.author = get_dict_attrib(attributes, "Author")
    item.about = get_dict_attrib(attributes, "About")

    health = get_dict_attrib(attributes, "Health")
    if health not in dtf.core.item.VALID_HEALTH_VALUES:
        log.e(TAG, "Invalid health specified. Exiting.")
        return None

    item.health = health

    version = get_dict_attrib(attributes, "Version")
    if version is not None:
        if dtf.core.item.is_valid_version(version):
            item.version = version
        else:
            log.e(TAG, "Invalid version specified. Exiting.")
            return None
    else:
        item.version = None

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

        sql = ('SELECT name, version, '
               'about, author, health '
               'FROM binaries '
               'ORDER BY name')

        cur.execute(sql)

        while True:

            item = dtf.core.item.Item()
            line = cur.fetchone()
            if line is None:
                break

            item.type = dtf.core.item.TYPE_BINARY
            item.name = line[0]
            item.version = line[1]
            item.about = line[2]
            item.author = line[3]
            item.health = line[4]

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

        sql = ('SELECT name, version, '
               'about, author, health '
               'FROM libraries '
               'ORDER BY name')

        cur.execute(sql)

        while True:

            item = dtf.core.item.Item()
            line = cur.fetchone()
            if line is None:
                break

            item.type = dtf.core.item.TYPE_LIBRARY
            item.name = line[0]
            item.version = line[1]
            item.about = line[2]
            item.author = line[3]
            item.health = line[4]

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

        sql = ('SELECT name, version, '
               'about, author, health '
               'FROM modules '
               'ORDER BY name')

        cur.execute(sql)

        while True:

            item = dtf.core.item.Item()
            line = cur.fetchone()
            if line is None:
                break

            item.type = dtf.core.item.TYPE_MODULE
            item.name = line[0]
            item.version = line[1]
            item.about = line[2]
            item.author = line[3]
            item.health = line[4]

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

        sql = ('SELECT name, version, '
               'about, author, health '
               'FROM packages '
               'ORDER BY name')

        cur.execute(sql)

        while True:

            item = dtf.core.item.Item()
            line = cur.fetchone()
            if line is None:
                break

            item.type = dtf.core.item.TYPE_PACKAGE
            item.name = line[0]
            item.version = line[1]
            item.about = line[2]
            item.author = line[3]
            item.health = line[4]

            packages.append(item)

    return packages


def is_binary_installed(name):

    """Determine if a binary is installed"""

    return __item_installed(name, dtf.core.item.TYPE_BINARY)


def is_library_installed(name):

    """Determine if a library is installed"""

    return __item_installed(name, dtf.core.item.TYPE_LIBRARY)


def is_module_installed(name):

    """Determine if a module is installed"""

    return __item_installed(name, dtf.core.item.TYPE_MODULE)


def is_package_installed(name):

    """Determine if a package is installed"""

    return __item_installed(name, dtf.core.item.TYPE_PACKAGE)


def find_local_module(root, name):

    """Determine if a local module exists"""

    local_module_path = "%s/%s/%s" % (root,
                                      utils.LOCAL_MODULES_DIRECTORY, name)

    if os.path.isfile(local_module_path):
        return 1
    else:
        return 0


# Repo management
def add_repo(repo_name, url):

    """Add a repo to the DB"""

    # First, validate the URL
    if not utils.is_valid_url(url):
        log.e(TAG, "Invalid URL provided (missing http/s)")
        return -2

    # Next, make sure this repo doesnt exist
    if __has_repo(repo_name):
        log.e(TAG, "Repo name '%s' already exists!" % repo_name)
        return -3

    return __add_repo(repo_name, url)


def remove_repo(repo_name):

    """Remove a repo"""

    if not __has_repo(repo_name):
        log.e(TAG, "Repo name '%s' doesn't exist!" % repo_name)
        return -3

    return __do_repo_delete(repo_name)


def get_repos():

    """Get listing of repos"""

    return __do_get_repos()


# INTERNAL ONLY #######################################################
def __prompt_install(local_item, installed_item):

    """Prompt user for item installation"""

    print "Installed Item Details:"
    print str(installed_item)

    print ""

    print "New Item Details:"
    print str(local_item)

    print ""
    print "Do you want to install this %s? [y/N]" % (installed_item.type),
    resp = raw_input()

    return bool(resp.lower() == "y")


def __prompt_delete(installed_item):

    """Prompt user to item deletion"""

    print "Installed Item Details:"
    print str(installed_item)

    print ""
    print "Are you sure you want to delete this item (NO UNDO)? [y/N]",
    resp = raw_input()

    return bool(resp.lower() == "y")


def __load_item(item):

    """Create new fully-loaded Item"""

    itm = dtf.core.item.Item()

    itm.name = item.name
    itm.type = item.type

    itm.install_name = get_item_attrib(item, "install_name")
    itm.local_name = None
    itm.author = get_item_attrib(item, "author")
    itm.about = get_item_attrib(item, "about")
    itm.version = get_item_attrib(item, "version")
    itm.health = get_item_attrib(item, "health")

    return itm


def __item_installed(name, item_type):

    """Generic test for installed content"""

    if item_type == dtf.core.item.TYPE_MODULE:
        table = "modules"
    elif item_type == dtf.core.item.TYPE_LIBRARY:
        table = "libraries"
    elif item_type == dtf.core.item.TYPE_BINARY:
        table = "binaries"
    elif item_type == dtf.core.item.TYPE_PACKAGE:
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

    return bool(cur.fetchone() is not None)


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


def __do_zip_binary_install(export_zip, item):

    """Perform the ZIP binary installation"""

    # First copy the new file.
    if export_zip.install_item_to(item, DTF_BINARIES_DIR) != 0:
        log.e(TAG, "Error copying binary '%s'" % item.local_name)
        return -1

    # Update database
    if __update_binary(item) == 0:
        log.e(TAG, "Failed to update binary '%s' details in database."
              % (item.name))
        return -2

    return 0


def __do_zip_library_install(export_zip, item):

    """Perform the ZIP library installation"""

    # First copy the new file.
    if export_zip.install_item_to(item, DTF_LIBRARIES_DIR) != 0:
        log.e(TAG, "Error copying library '%s'" % item.local_name)
        return -1

    # Update database
    if __update_library(item) == 0:
        log.e(TAG, "Failed to update library '%s' details in database."
              % (item.name))
        return -2

    return 0


def __do_zip_module_install(export_zip, item):

    """Perform the ZIP module installation"""

    # First copy the new file.
    if export_zip.install_item_to(item, DTF_MODULES_DIR) != 0:
        log.e(TAG, "Error copying module '%s'" % item.local_name)
        return -1

    # Update database
    if __update_module(item) == 0:
        log.e(TAG, "Failed to update module '%s' details in database."
              % (item.name))
        return -2

    return 0


def __do_zip_package_install(export_zip, item):

    """Perform the ZIP package installation"""

    # First copy the new file.
    if export_zip.install_item_to(item, DTF_PACKAGES_DIR) != 0:
        log.e(TAG, "Error copying package '%s'" % item.local_name)
        return -1

    # Update database
    if __update_package(item) == 0:
        log.e(TAG, "Failed to update package '%s' details in database."
              % (item.name))
        return -2

    return 0


def __update_binary(item):

    """Update a binary in the DB"""

    conn = sqlite3.connect(DTF_DB)
    cur = conn.cursor()

    # Remove the line first.
    sql = ('DELETE FROM binaries '
           "WHERE name='%s'" % item.name)

    cur.execute(sql)

    entry = [(item.name, item.version, item.author,
              item.health, item.install_name)]

    # Update a Binary Entry
    sql = ('INSERT INTO binaries (name, version, '
           'author, health, install_name)'
           'VALUES (?, ?, ?, ?, ?)')

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

    entry = [(item.name, item.version, item.author,
              item.health, item.install_name)]

    # Update a Library Entry
    sql = ('INSERT INTO libraries (name, version, '
           'author, health, install_name)'
           'VALUES (?, ?, ?, ?, ?)')

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

    entry = [(item.name, item.about, item.version,
              item.author, item.health, item.install_name)]

    # Update a Module Entry
    sql = ('INSERT INTO modules (name, about, version, '
           'author, health, install_name)'
           'VALUES (?, ?, ?, ?, ?, ?)')

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

    entry = [(item.name, item.version, item.author,
              item.health, item.install_name)]

    # Update a Package Entry
    sql = ('INSERT INTO packages (name, version, '
           'author, health, install_name)'
           'VALUES (?, ?, ?, ?, ?)')

    cur.executemany(sql, entry)
    conn.commit()

    return cur.rowcount


def __add_repo(repo_name, url):

    """Add a repo to DB"""

    conn = sqlite3.connect(DTF_DB)
    cur = conn.cursor()

    entry = [(repo_name, url)]

    sql = ('INSERT INTO repos (repo_name, url)'
           'VALUES (?, ?)')

    cur.executemany(sql, entry)
    conn.commit()

    return 0


def __has_repo(repo_name):

    """Check if a repo exists"""

    dtf_db = sqlite3.connect(DTF_DB)
    cur = dtf_db.cursor()

    sql = ('SELECT id '
           'FROM repos '
           "WHERE repo_name='%s' "
           'LIMIT 1' % repo_name)

    cur.execute(sql)

    return bool(cur.fetchone() is not None)


def __do_get_repos():

    """return list(repo, url)"""

    repo_list = list()

    dtf_db = sqlite3.connect(DTF_DB)
    cur = dtf_db.cursor()

    sql = ('SELECT repo_name, url '
           'FROM repos')

    for repo in cur.execute(sql):
        repo_list.append((repo[0], repo[1]))

    return repo_list


def __do_binary_delete(item):

    """Perform the binary removal"""

    file_path = DTF_BINARIES_DIR + item.install_name

    if utils.delete_file(file_path) != 0:
        log.e(TAG, "Error removing binary file! Continuing.")

    conn = sqlite3.connect(DTF_DB)
    cur = conn.cursor()

    # Remove the line first.
    sql = ('DELETE FROM binaries '
           "WHERE name='%s'" % item.name)

    cur.execute(sql)
    conn.commit()

    return 0


def __do_library_delete(item):

    """Perform the library removal"""

    file_path = DTF_LIBRARIES_DIR + item.install_name

    if utils.delete_tree(file_path) != 0:
        log.e(TAG, "Error removing tree! Continuing.")

    conn = sqlite3.connect(DTF_DB)
    cur = conn.cursor()

    # Remove the line first.
    sql = ('DELETE FROM libraries '
           "WHERE name='%s'" % item.name)

    cur.execute(sql)
    conn.commit()

    return 0


def __do_module_delete(item):

    """Perform the module removal"""

    file_path = DTF_MODULES_DIR + item.install_name

    if utils.delete_file(file_path) != 0:
        log.e(TAG, "Error removing module file! Continuing.")

    conn = sqlite3.connect(DTF_DB)
    cur = conn.cursor()

    # Remove the line first.
    sql = ('DELETE FROM modules '
           "WHERE name='%s'" % item.name)

    cur.execute(sql)
    conn.commit()

    return 0


def __do_package_delete(item):

    """Perform the package removal"""

    file_path = DTF_PACKAGES_DIR + item.install_name

    if utils.delete_tree(file_path) != 0:
        log.e(TAG, "Error removing tree! Continuing.")

    conn = sqlite3.connect(DTF_DB)
    cur = conn.cursor()

    # Remove the line first.
    sql = ('DELETE FROM packages '
           "WHERE name='%s'" % item.name)

    cur.execute(sql)
    conn.commit()

    return 0


def __do_repo_delete(repo_name):

    """Remove repo"""

    conn = sqlite3.connect(DTF_DB)
    cur = conn.cursor()

    sql = ('DELETE FROM repos '
           "WHERE repo_name='%s'" % repo_name)

    cur.execute(sql)
    conn.commit()

    return 0
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
           'version TEXT, '
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
           'version TEXT, '
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
           'version TEXT, '
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
           'version TEXT, '
           'author TEXT, '
           'health TEXT, '
           'install_name TEXT'
           ')')

    rtn = dtf_db.execute(sql)

    if not rtn:
        log.e(TAG, "Error creating packages table, exiting")
        return rtn

    # Create Repo Table
    sql = ('CREATE TABLE IF NOT EXISTS repos'
           '('
           'id INTEGER PRIMARY KEY AUTOINCREMENT, '
           'repo_name TEXT UNIQUE NOT NULL, '
           'url TEXT'
           ')')

    rtn = dtf_db.execute(sql)

    if not rtn:
        log.e(TAG, "Error creating repos table, exiting")
        return rtn

    dtf_db.commit()
    dtf_db.close()

    return 0


def create_data_dirs():

    """Create the .dtf/ directory structure"""

    # First create the main dir.
    if not os.path.isdir(DTF_DATA_DIR):

        try:
            os.mkdir(DTF_DATA_DIR)
        except OSError:
            log.e(TAG, "Unable to create dtf data directory!")
            return -6

    # Now the subdirectories. Be less strict about errors for these.
    try:
        os.mkdir(DTF_MODULES_DIR)
        os.mkdir(DTF_PACKAGES_DIR)
        os.mkdir(DTF_BINARIES_DIR)
        os.mkdir(DTF_LIBRARIES_DIR)
    except OSError:
        pass

    return 0
# End Initialization ###############################################


# Internal Package Installation ####################################
# pylint: disable=too-many-arguments,too-many-return-statements
def __generic_install(item, force_mode, new_only, check_function,
                      install_function, install_args):

    """Generic check and caller"""

    try:
        # First check if we know about this item
        if check_function(item.name):

            log.d(TAG, "Item exists, need to check")

            # If forced, don't even check.
            if force_mode:
                log.i(TAG, "Forcing component installation: %s (%s)"
                      % (item.name, item.type))
                return install_function(*install_args)

            installed_item = __load_item(item)

            # Ok, next, we check the versions.
            if dtf.core.item.item_is_newer(installed_item, item):
                log.i(TAG, "Upgrading %s from v%s to v%s"
                      % (item.name, installed_item.version, item.version))
                return install_function(*install_args)

            elif new_only:
                log.w(TAG, "Skipping due to older version: %s" % item.name)
                return 0

            # Otherwise we need to prompt
            else:
                print ("[WARNING] An item with this name is already installed."
                       " See details below.")

                if __prompt_install(item, installed_item):
                    log.d(TAG, "User would like to install")
                    return install_function(*install_args)
                else:
                    log.w(TAG, "Installation skipped.")
                    return 0
        else:
            log.i(TAG, "Installing new item: %s (%s)"
                  % (item.name, item.type))
            return install_function(*install_args)

    except KeyError:
        log.w(TAG, "Error checking if the item was installed. Skipping")
        return -4


# Install Content ######################################################
def install_zip(zip_file_name, force=False, new_only=False):

    """Install a ZIP file"""

    rtn = 0
    export_zip = mp.ExportZip(zip_file_name)

    for item in export_zip.iter_items():

        if not export_zip.assert_item(item):
            log.w(TAG, "'%s' defined, but local file '%s' does not exist!"
                  % (item.name, item.local_name))
            continue

        item_type = item.type

        if item_type == dtf.core.item.TYPE_BINARY:
            rtn |= __generic_install(item, force, new_only,
                                     is_binary_installed,
                                     __do_zip_binary_install,
                                     (export_zip, item))

        elif item_type == dtf.core.item.TYPE_LIBRARY:
            rtn |= __generic_install(item, force, new_only,
                                     is_library_installed,
                                     __do_zip_library_install,
                                     (export_zip, item))

        elif item_type == dtf.core.item.TYPE_MODULE:
            rtn |= __generic_install(item, force, new_only,
                                     is_module_installed,
                                     __do_zip_module_install,
                                     (export_zip, item))

        elif item_type == dtf.core.item.TYPE_PACKAGE:
            rtn |= __generic_install(item, force, new_only,
                                     is_package_installed,
                                     __do_zip_package_install,
                                     (export_zip, item))

    return rtn


def install_single(item, force=False):

    """Install a single item"""

    item_type = item.type

    if item_type == dtf.core.item.TYPE_BINARY:
        return __generic_install(item, force, False, is_binary_installed,
                                 __do_single_binary_install, (item,))

    elif item_type == dtf.core.item.TYPE_LIBRARY:
        return __generic_install(item, force, False, is_library_installed,
                                 __do_single_library_install, (item,))

    elif item_type == dtf.core.item.TYPE_MODULE:
        return __generic_install(item, force, False, is_module_installed,
                                 __do_single_module_install, (item,))

    elif item_type == dtf.core.item.TYPE_PACKAGE:
        return __generic_install(item, force, False, is_package_installed,
                                 __do_single_package_install, (item,))
# End Package Installation ##############################################


# Removing Content ######################################################
def delete_binary(name, force=False):

    """Remove a binary"""

    rtn = 0

    # First check if we know about the binary
    if is_binary_installed(name):

        item = dtf.core.item.Item()
        item.name = name
        item.type = dtf.core.item.TYPE_BINARY

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

        item = dtf.core.item.Item()
        item.name = name
        item.type = dtf.core.item.TYPE_LIBRARY

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

        item = dtf.core.item.Item()
        item.name = name
        item.type = dtf.core.item.TYPE_MODULE

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

        item = dtf.core.item.Item()
        item.name = name
        item.type = dtf.core.item.TYPE_PACKAGE

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

        if utils.delete_file(full_path) != 0:
            log.e(TAG, "Error removing binary file! Continuing.")

    # Remove Libraries
    sql = ('SELECT name, install_name '
           'FROM libraries')

    for row in cur.execute(sql):

        library_name = row[0]
        install_name = row[1]
        full_path = DTF_LIBRARIES_DIR + install_name
        log.d(TAG, "Removing library '%s'" % library_name)

        if utils.delete_tree(full_path) != 0:
            log.e(TAG, "Error removing library! Continuing.")

    # Remove Modules
    sql = ('SELECT name, install_name '
           'FROM modules')

    for row in cur.execute(sql):

        module_name = row[0]
        install_name = row[1]
        full_path = DTF_MODULES_DIR + install_name
        log.d(TAG, "Removing module '%s'" % module_name)

        if utils.delete_file(full_path) != 0:
            log.e(TAG, "Error removing module file! Continuing.")

    # Remove Packages
    sql = ('SELECT name, install_name '
           'FROM packages')

    for row in cur.execute(sql):

        package_name = row[0]
        install_name = row[1]
        full_path = DTF_PACKAGES_DIR + install_name
        log.d(TAG, "Removing package '%s'" % package_name)

        if utils.delete_tree(full_path) != 0:
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
