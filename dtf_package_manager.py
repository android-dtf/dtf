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
# DTF's package manager.

from argparse import ArgumentParser
from os import chmod, remove, makedirs, listdir
from pydtf import dtflog as log
from pydtf import dtfglobals
from shutil import copy, copytree, rmtree
from sys import argv
from tempfile import NamedTemporaryFile
from zipfile import ZipFile, is_zipfile
import os.path 
import sqlite3
import re

try:
    from lxml import etree
except ImportError:
    raise ImportError('DTF requires the python module "lxml" to use. Please install it!')
    exit(-5)

__VERSION__ = "1.0"

TAG = "dtf_package_installer"

DTF_DIR = dtfglobals.DTF_DIR
DTF_BINARIES_DIR =  DTF_DIR + "/bin/"
DTF_LIBRARIES_DIR =  DTF_DIR + "/lib/"
DTF_MODULES_DIR =  DTF_DIR + "/modules/"
DTF_PACKAGES_DIR = DTF_DIR + "/packages/"
DTF_DB = DTF_DIR + "/main.db"

MANIFEST_NAME = "manifest.xml"

VALID_TYPES = ['binary', 'module', 'library', 'package']
VALID_HEALTH_VALUES = ['stable', 'working', 'beta', 'deprecated', 'broken', None]

TYPE_MODULE = "module"
TYPE_LIBRARY= "library"
TYPE_BINARY = "binary"
TYPE_PACKAGE = "package"

force_mode = False

# No log to file.
log.LOG_LEVEL_FILE = 0

def usage():

    print "DTF Package Manager Version %s" % __VERSION__
    print ""
    print "Subcommands:"
    print "    delete      Delete an item from main database."
    print "    export      Export entire main database to DTF ZIP."
    print "    install     Install a DTF ZIP or single item."
    print ""


class Item(object):

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
        self.install_name = None
        self.local_name = None
        self.name = None
        self.type = None
        self.author = None
        self.about = None
        self.major_version = None
        self.minor_version = None
        self.health = None

    def makeVersion(self):

	if self.major_version == None and self.minor_version == None:
	   return None
	else:
	   if self.major_version == None: mjr = "0"
	   else: mjr = self.major_version

	   if self.minor_version == None: mnr = "0"
	   else: mnr = self.minor_version
     
	   return "%s.%s" % (mjr, mnr)      
    
    def __repr__(self):
        temp = "Name: %s (%s)\n" % (self.name, self.type)
        if self.type == TYPE_MODULE: temp += "  About: %s\n" % self.about
        temp += "  Installs as: %s\n" % self.install_name
        temp += "  Author: %s\n" % self.author
        temp += "  Version: %s\n" % self.makeVersion()
        temp += "  Health: %s" % self.health
        return temp

def loadItem(item):

    itm = Item()

    itm.name = item.name
    itm.type = item.type    

    itm.install_name = getItemAttribute(item, "install_name")
    itm.local_name = None
    itm.author = getItemAttribute(item, "author")
    itm.about = getItemAttribute(item, "about")
    itm.major_version = getItemAttribute(item, "major_version")
    itm.minor_version = getItemAttribute(item, "minor_version")
    itm.health = getItemAttribute(item, "health")

    return itm

def safeDictAccess(in_dict, key, default=None):

    try:
        return in_dict[key]
    except KeyError:
        return default

def splitVersion(in_val):

    try:
        (major, minor) = in_val.split('.')      
    except AttributeError:
        return None,None
    except ValueError:
        return None,None

    return (major, minor)

# XML Stuff
def getAttrib(element, attrib, default=None):

    try:
        return element.attrib[attrib]
    except KeyError:
        return default

# DB Stuff
def itemInstalled(item):

    type = item.type

    if type == TYPE_MODULE:
        table = "modules"
    elif type == TYPE_LIBRARY:
        table = "libraries"
    elif type == TYPE_BINARY:
        table = "binaries"
    elif type == TYPE_PACKAGE:
        table = "packages"
    else:
        raise KeyError

    dtf_db = sqlite3.connect(DTF_DB)

    c = dtf_db.cursor()

    sql = ("SELECT id "
           "FROM %s "
           "WHERE name='%s' "
           'LIMIT 1' % (table, item.name))

    c.execute(sql)

    if c.fetchone() is not None:
        return True
    else:
        return False

def getItemAttribute(item, attribute):

    type = item.type

    if type == TYPE_MODULE:
        table = "modules"
    elif type == TYPE_LIBRARY:
        table = "libraries"
    elif type == TYPE_BINARY:
        table = "binaries"
    elif type == TYPE_PACKAGE:
        table = "packages"
    else:
        log.e(TAG, "Unknown type '%s' in getItem Attribute. Returning")
        return None

    dtf_db = sqlite3.connect(DTF_DB)

    c = dtf_db.cursor()

    sql = ("SELECT %s "
           "FROM %s "
           "WHERE name='%s' "
           'LIMIT 1' % (attribute, table, item.name))

    c.execute(sql)

    try:
        return c.fetchone()[0]
    except TypeError:
        return None

def deleteItem(item):

    if item.type == TYPE_BINARY:
        return deleteBinary(item)
    elif item.type == TYPE_LIBRARY:
        return deleteLibrary(item)
    elif item.type == TYPE_MODULE:
        return deleteModule(item)
    elif item.type == TYPE_PACKAGE:
        return deletePackage(item)
    else:
        log.e(TAG, "How is this even reachable?")
        return -99

def installSingleItem(item):

    if item.type == TYPE_BINARY:
        return installSingleBinary(item)
    elif item.type == TYPE_LIBRARY:
        return installSingleLibrary(item)
    elif item.type == TYPE_MODULE:
        return installSingleModule(item)
    elif item.type == TYPE_PACKAGE:
        return installSinglePackage(item)
    else:
        log.e(TAG, "How is this even reachable?")
        return -99

def installSingleBinary(item):

    name = item.name
    local_name = item.local_name
    install_name = item.install_name

    # First copy the new file.
    if copyFile(local_name, install_name, DTF_BINARIES_DIR) != 0:
        log.e(TAG, "Error copying binary '%s'" % (local_name))
        return -1

    # Update database
    if updateBinary(item) == 0:
        print "[ERROR] Failed to update binary '%s' details in database. Skipping." % (name)
        return -2

    log.i(TAG, "Binary '%s' installed successfully!" % name)

    return 0


def installZipBinary(zip_f, item):

    name = item.name
    local_name = item.local_name
    install_name = item.install_name

    # First copy the new file.
    if copyZipFile(zip_f, local_name, install_name, DTF_BINARIES_DIR) != 0:
        log.e(TAG, "Error copying binary '%s'" % (local_name))
        return -1

    # Update database
    if updateBinary(item) == 0:
        print "[ERROR] Failed to update binary '%s' details in database. Skipping." % (name)
        return -2

    return 0

def deleteBinary(item):

    file_path = DTF_BINARIES_DIR + item.install_name

    if deleteFile(file_path) != 0:
        log.e(TAG, "Error removing binary file! Continuing.")

    conn = sqlite3.connect(DTF_DB)
    c = conn.cursor()

    # Remove the line first.
    sql = ('DELETE FROM binaries '
           "WHERE name='%s'" % item.name)

    c.execute(sql)
    conn.commit()

    return c.rowcount

def installSingleLibrary(item):

    name = item.name
    local_name = item.local_name
    install_name = item.install_name

    # First copy the new file.
    if copyTree(local_name, install_name, DTF_LIBRARIES_DIR) != 0:
        log.e(TAG, "Error copying library '%s'" % (local_name))
        return -1

    # Update database
    if updateLibrary(item) == 0:
        print "[ERROR] Failed to update library '%s' details in database. Skipping." % (name)
        return -2

    log.i(TAG, "Library '%s' installed successfully!" % name)

    return 0

def installZipLibrary(zip_f, item):

    name = item.name
    local_name = item.local_name
    install_name = item.install_name

    # First copy the new file.
    if copyZipTree(zip_f, local_name, install_name, DTF_LIBRARIES_DIR) != 0:
        log.e(TAG, "Error copying library '%s'" % (local_name))
        return -1

    # Update database
    if updateLibrary(item) == 0:
        print "[ERROR] Failed to update library '%s' details in database. Skipping." % (name)
        return -2

    return 0

def deleteLibrary(item):

    file_path = DTF_LIBRARIES_DIR + item.install_name

    print file_path

    if deleteTree(file_path) != 0:
        log.e(TAG, "Error removing tree! Continuing.")

    conn = sqlite3.connect(DTF_DB)
    c = conn.cursor()

    # Remove the line first.
    sql = ('DELETE FROM libraries '
           "WHERE name='%s'" % item.name)

    c.execute(sql)
    conn.commit()

    return c.rowcount


def installSingleModule(item):

    name = item.name
    local_name = item.local_name
    install_name = item.install_name

    # First copy the new file.
    if copyFile(local_name, install_name, DTF_MODULES_DIR) != 0:
        log.e(TAG, "Error copying module '%s'" % (local_name))
        return -1

    # Update database
    if updateModule(item) == 0:
        print "[ERROR] Failed to update module '%s' details in database. Skipping." % (name)
        return -2

    log.i(TAG, "Module '%s' installed successfully!" % name)

    return 0

def installZipModule(zip_f, item):

    name = item.name
    local_name = item.local_name
    install_name = item.install_name

    # First copy the new file.
    if copyZipFile(zip_f, local_name, install_name, DTF_MODULES_DIR) != 0:
	log.e(TAG, "Error copying module '%s'" % (local_name))
	return -1

    # Update database
    if updateModule(item) == 0:
	print "[ERROR] Failed to update module '%s' details in database. Skipping." % (name)
        return -2

    return 0

def deleteModule(item):

    file_path = DTF_MODULES_DIR + item.install_name

    if deleteFile(file_path) != 0:
        log.e(TAG, "Error removing module file! Continuing.")

    conn = sqlite3.connect(DTF_DB)
    c = conn.cursor()

    # Remove the line first.
    sql = ('DELETE FROM modules '
           "WHERE name='%s'" % item.name)

    c.execute(sql)
    conn.commit()

    return c.rowcount


def installSinglePackage(item):

    name = item.name
    local_name = item.local_name
    install_name = item.install_name

    # First copy the new file.
    if copyTree(local_name, install_name, DTF_PACKAGES_DIR) != 0:
        log.e(TAG, "Error copying package '%s'" % (local_name))
        return -1

    # Update database
    if updatePackage(item) == 0:
        print "[ERROR] Failed to update package '%s' details in database. Skipping." % (name)
        return -2

    log.i(TAG, "Package '%s' installed successfully!" % name)

    return 0

def installZipPackage(zip_f, item):

    name = item.name
    local_name = item.local_name
    install_name = item.install_name

    # First copy the new file.
    if copyZipTree(zip_f, local_name, install_name, DTF_PACKAGES_DIR) != 0:
        log.e(TAG, "Error copying package '%s'" % (local_name))
        return -1

    # Update database
    if updatePackage(item) == 0:
        print "[ERROR] Failed to update package '%s' details in database. Skipping." % (name)
        return -2

    return 0

def deletePackage(item):

    file_path = DTF_PACKAGES_DIR + item.install_name

    print file_path

    if deleteTree(file_path) != 0:
        log.e(TAG, "Error removing tree! Continuing.")

    conn = sqlite3.connect(DTF_DB)
    c = conn.cursor()

    # Remove the line first.
    sql = ('DELETE FROM packages '
           "WHERE name='%s'" % item.name)

    c.execute(sql)
    conn.commit()

    return c.rowcount


def updateBinary(item):

    conn = sqlite3.connect(DTF_DB)
    c = conn.cursor()

    # Remove the line first.
    sql = ('DELETE FROM binaries '
           "WHERE name='%s'" % item.name)

    c.execute(sql)

    entry = [(item.name, item.major_version, item.minor_version, item.author, 
              item.health, item.install_name)]

    # Update a Binary Entry
    sql = ('INSERT INTO binaries (name, major_version, minor_version, '
           'author, health, install_name)'
           'VALUES (?, ?, ?, ?, ?, ?)')

    c.executemany(sql, entry)
    conn.commit()

    return c.rowcount

def updateLibrary(item):

    conn = sqlite3.connect(DTF_DB)
    c = conn.cursor()

    # Remove the line first.
    sql = ('DELETE FROM libraries '
           "WHERE name='%s'" % item.name)

    c.execute(sql)

    entry = [(item.name, item.major_version, item.minor_version, item.author, 
              item.health, item.install_name)]

    # Update a Library Entry
    sql = ('INSERT INTO libraries (name, major_version, minor_version, '
           'author, health, install_name)'
           'VALUES (?, ?, ?, ?, ?, ?)')

    c.executemany(sql, entry)
    conn.commit()

    return c.rowcount


def updateModule(item):

    conn = sqlite3.connect(DTF_DB)
    c = conn.cursor()

    # Remove the line first.
    sql = ('DELETE FROM modules '
           "WHERE name='%s'" % item.name)

    c.execute(sql)

    entry = [(item.name, item.about, item.major_version, item.minor_version, item.author, 
              item.health, item.install_name)]
    
    # Update a Module Entry
    sql = ('INSERT INTO modules (name, about, major_version, minor_version, '
           'author, health, install_name)'
           'VALUES (?, ?, ?, ?, ?, ?, ?)')

    c.executemany(sql, entry)
    conn.commit()

    return c.rowcount

def updatePackage(item):

    conn = sqlite3.connect(DTF_DB)
    c = conn.cursor()

    # Remove the line first.
    sql = ('DELETE FROM packages '
           "WHERE name='%s'" % item.name)

    c.execute(sql)

    entry = [(item.name, item.major_version, item.minor_version, item.author, 
              item.health, item.install_name)]

    # Update a Package Entry
    sql = ('INSERT INTO packages (name, major_version, minor_version, '
           'author, health, install_name)'
           'VALUES (?, ?, ?, ?, ?, ?)')

    c.executemany(sql, entry)
    conn.commit()

    return c.rowcount

def localExists(local_name):
    return os.path.isfile(local_name)

def localDirExists(local_name):
    return os.path.isdir(local_name)

def localZipExists(zip_f, local_name):

    try:
        zip_f.read(local_name)
        return True
    except KeyError:
        return False

def localZipDirExists(zip_f, local_name):

    return any(x.startswith("%s/" % local_name.rstrip("/")) for x in zip_f.namelist())

def copyFile(local_name, install_name, install_dir):
    
    install_path = install_dir + install_name

    log.i(TAG, "Copying \"%s\" to \"%s\"..." % (local_name, install_path))
    copy(local_name, install_path)

    chmod(install_path, 0755)

    log.i(TAG, "Copy complete!")

    return 0


def copyZipFile(zip_f, local_name, install_name, install_dir):

    install_path = install_dir + install_name

    log.i(TAG, "Copying \"%s\" to \"%s\"..." % (local_name, install_path))
    temp_f = NamedTemporaryFile(mode='w', delete=False)

    temp_f.write(zip_f.read(local_name))
    temp_f.flush()

    copy(temp_f.name, install_path)

    chmod(install_path, 0755)

    temp_f.close()
   
    remove(temp_f.name)

    log.i(TAG, "Copy complete!")

    return 0

def deleteFile(install_path):

    try:
        remove(install_path)
        return 0
    except OSError:
        log.w(TAG, "There was an OSError when removing the file '%s'" % install_path)
        return 0

def copyTree(local_name, install_name, install_dir):

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
                log.i(TAG, "Making dir  %s" % (install_path + new_dir))
                makedirs(install_path + new_dir)
        if len(files) != 0:
            for local_file in [os.path.join(root, name) for name in files]:
                new_file = local_file.replace(local_name+'/', '', 1)
                log.i(TAG, "Copying file '%s' to '%s'" % (local_file, install_path + new_file))
                copy(local_file, install_path + new_file)

    return 0


def copyZipTree(zip_f, local_name, install_name, install_dir):

    install_path = install_dir + install_name + '/'

    # We need to remove the first one
    rmtree(install_path, ignore_errors=True)

    # Make the new directory.
    makedirs(install_path)

    for f in zip_f.namelist():
        # Do everything in the [local_name] dir, but not the root.
        if f.startswith(local_name) and f != local_name+'/': 

            # First, we need to remove the first element.
            new_f = f.replace(local_name+'/', '', 1)
            
            # If it's a directory, make it.
            if f.endswith('/'):
                log.i(TAG, "Making dir %s" % install_path + new_f)
                makedirs(install_path + new_f)

            # Otherwise, we need to unzip to that new path.
            else:
                head, tail = os.path.split(new_f)
                log.i(TAG, "extracting %s to %s" % (f, install_path+head))
                copyZipFile(zip_f, f, tail, install_path+head+'/')

    log.i(TAG, "Copy complete!")

    return 0

def deleteTree(install_path):

    try:
        rmtree(install_path)
        return 0
    except OSError:
        log.w(TAG, "There was an OSError when removing the tree at '%s'" % install_path)
        return 0

def promptDelete(inst_item):

    global force_mode

    if force_mode:
        log.i(TAG, "Forcing component removal.")
        return True

    print "Installed Item Details:"
    print str(inst_item)

    print ""
    print "Are you sure you want to delete this item (CANNOT BE UNDONE)? [y/N]",
    resp = raw_input()
    if resp.lower() == "y":
        return True
    else:
        return False

def promptInstall(local_item, inst_item):

    global force_mode

    if force_mode:
        log.i(TAG, "Forcing component installation.")
        return True

    print "Installed Item Details:"
    print str(inst_item)

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


def createDtfDb():

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
           'health TEXT,'
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

def parseBinary(zip_f, item):

    rtn = 0

    # Does the resource even exist?
    if not localZipExists(zip_f, item.local_name):
        log.e(TAG, "Binary '%s' defined, but local resource '%s' does not exist! Skipping." % (item.name, item.local_name))
        return -1

    try:
        # First check if we know about this module.
        if itemInstalled(item):

            print "[WARNING] An item with this name is already installed. See details below."
            inst_item = loadItem(item)

            if promptInstall(item, inst_item):
                rtn = installZipBinary(zip_f, item)
            else:
                log.i(TAG, "Binary installed skipped.")
        else:
            log.i(TAG, "This is a new binary, installing.")
            rtn = installZipBinary(zip_f, item)

    except KeyError:
        log.e(TAG, "There was something wrong checking if the binary was installed. Skipping")
        rtn = -4

    return rtn

def parseLibrary(zip_f, item):

    rtn = 0

    # Does the resource even exist?
    if not localZipDirExists(zip_f, item.local_name):
        log.e(TAG, "Library '%s' defined, but directory '%s' does not exist! Skipping." % (item.name, item.local_name))
        return -1

    try:
        # First check if we know about this module.
        if itemInstalled(item):

            print "[WARNING] An item with this name is already installed. See details below."
            inst_item = loadItem(item)

            if promptInstall(item, inst_item):
                rtn = installZipLibrary(zip_f, item)
            else:
                log.i(TAG, "Library installed skipped.")
        else:
            log.i(TAG, "This is a new library, installing.")
            rtn = installZipLibrary(zip_f, item)

    except IOError:
        log.e(TAG, "There was something wrong checking if the library was installed. Skipping")
        rtn = -4

    return rtn

def autoParseModule(args):

    name = args.single_name
    install_name = args.single_install_name
    local_name = args.single_local_name

    if install_name is None:
        log.d(TAG, "install_name is null, using name...")
        install_name = name
    if local_name is None:
        log.d(TAG, "local_name is null, using name...")
        local_name = name

    # Does the resource even exist?
    if not localExists(local_name):
        log.e(TAG, "Local module resource '%s' does not exist! Skipping." % (local_name))
        return None

    attributes = dict()

    # Parse file for "#@", strings, store in dictionary.
    for line in open(local_name).read().split("\n"):
        m = re.match("#@[a-zA-Z\- ]+\:.*", line)
        if m == None: continue

        try:
            attribute, value = m.group(0).replace("#@","").split(":")
            value = value.lstrip(" ")
        except ValueError:
            log.w(TAG, "Unable to parse the module version, not including.")
            continue

        attributes[attribute] = value

    item = Item()
    item.type = TYPE_MODULE
    item.name = name
    item.local_name = local_name
    item.install_name = install_name
    item.author = safeDictAccess(attributes, "Author")
    item.about = safeDictAccess(attributes, "About")

    health = safeDictAccess(attributes, "Health")
    if health not in VALID_HEALTH_VALUES:
        print "[ERROR] Invalid health specified. Exiting."
        return None
    item.health = health

    version = safeDictAccess(attributes, "Version")
    if version is not None:
        try:
            (item.major_version, item.minor_version) = version.split('.')
        except ValueError:
            print "[ERROR] Version string is not valid. Exiting."
            return None
    else:
        item.major_version = None
        item.minor_version = None

    #Return our item.
    return item


def parseModule(zip_f, item):

    rtn = 0

    # Does the resource even exist?
    if not localZipExists(zip_f, item.local_name):
        log.e(TAG, "Module '%s' defined, but local resource '%s' does not exist! Skipping." % (item.name, item.local_name))
        return -1

    try:
        # First check if we know about this module.
        if itemInstalled(item):

	    print "[WARNING] An item with this name is already installed. See details below."
	    inst_item = loadItem(item)

	    if promptInstall(item, inst_item):
		rtn = installZipModule(zip_f, item)
	    else:
		log.i(TAG, "Module installed skipped.")
	else:
            log.i(TAG, "This is a new module, installing.")
            rtn = installZipModule(zip_f, item)

    except KeyError:
        log.e(TAG, "There was something wrong checking if the module was installed. Skipping")
        rtn = -4
 
    return rtn

def parsePackage(zip_f, item):

    rtn = 0

    # Does the resource even exist?
    if not localZipDirExists(zip_f, item.local_name):
        log.e(TAG, "Package '%s' defined, but directory '%s' does not exist! Skipping." % (item.name, item.local_name))
        return -1

    try:
        # First check if we know about this module.
        if itemInstalled(item):

            print "[WARNING] An item with this name is already installed. See details below."
            inst_item = loadItem(item)

            if promptInstall(item, inst_item):
                rtn = installZipPackage(zip_f, item)
            else:
                log.i(TAG, "Package installed skipped.")
        else:
            log.i(TAG, "This is a new package, installing.")
            rtn = installZipPackage(zip_f, item)

    except IOError:
        log.e(TAG, "There was something wrong checking if the package was installed. Skipping")
        rtn = -4

    return rtn

def parseSingleItem(args):

    item = Item()

    name = args.single_name
    if name == None:
        print "[ERROR] No '--name' specified in single item mode. Exiting."
        return None
    item.name = name    

    single_type = args.single_type
    if single_type not in VALID_TYPES:
        print "[ERROR] Invalid type passed to single. Exiting."
        return None
    item.type = single_type

    health = args.single_health
    if health not in VALID_HEALTH_VALUES:
        print "[ERROR] Invalid health specified. Exiting."
        return None
    item.health = health

    version = args.single_version
    if version is not None:
        try:
            (item.major_version, item.minor_version) = version.split('.')
        except ValueError:
            print "[ERROR] Version string is not valid. Exiting."
            return None
    else:
        item.major_version = None
        item.minor_version = None

    try:
       item.author = " ".join(args.single_author)
    except TypeError:
       item.author = None

    try:
        item.about = " ".join(args.single_about)
    except TypeError:
       item.about = None

    install_name = args.single_install_name
    local_name = args.single_local_name

    if install_name is None:
        log.d(TAG, "install_name is null, using name...")
        install_name = name
    if local_name is None:
        log.d(TAG, "local_name is null, using name...")
        local_name = name

    item.install_name = install_name
    item.local_name = local_name

    if item.type == TYPE_BINARY:
        if not localExists(item.local_name):
            print "[ERROR] Local item '%s' does not exist. Exiting." % (item.local_name)
            return None
    elif item.type == TYPE_LIBRARY:
        if not localDirExists(item.local_name):
            print "[ERROR] Local directory '%s' does not exist. Exiting." % (item.local_name)
            return None
    elif item.type == TYPE_MODULE:
        if not localExists(item.local_name):
            print "[ERROR] Local item '%s' does not exist. Exiting." % (item.local_name)
            return None
    elif item.type == TYPE_PACKAGE:
        if not localDirExists(item.local_name):
            print "[ERROR] Local directory '%s' does not exist. Exiting." % (item.local_name)
            return None

    return item

def parseZip(zip_file_name):

    manifest_data = None
    manifest_root = None

    zip_f = ZipFile(zip_file_name, 'r')

    log.i(TAG, "Parsing manifest file...")

    # Get Manifest
    if not localZipExists(zip_f, MANIFEST_NAME):
        print "[ERROR] Error extracting '%s' from ZIP archive - does it exist?" % (MANIFEST_NAME)
    manifest_data = zip_f.read(MANIFEST_NAME)
    
    # Read Manifest
    try:
        manifest_root = etree.XML(manifest_data)
    except etree.XMLSyntaxError as e:
        print "[ERROR] Error parsing XML file '%s' : \"%s\" (%i). Exiting." % (MANIFEST_NAME, e.strerror, e.errno)
        return -4

    # Processing Stuff
    items = manifest_root.xpath("/Items/Item")

    for item in items:

        type = getAttrib(item, "type")
        if type is None or type not in VALID_TYPES:
            log.e(TAG, "Found tag with no 'type' attribute, skipping!")
            continue
         
        if type not in VALID_TYPES:
            log.e(TAG, "Illegal \'type\' attribute found, skipping!")
            continue

        name = getAttrib(item, "name")
        if name is None:
            log.e(TAG, "Found NULL named moduled, skipping!")
            continue

        # Ok, lets start.  We can generically parse.
        local_item = Item()

        local_item.type = type
        local_item.major_version = getAttrib(item, "majorVersion")
        local_item.minor_version = getAttrib(item, "minorVersion")
        local_item.health = getAttrib(item, "health")
        local_item.author = getAttrib(item, "author")
        local_item.about = getAttrib(item, "about")

        install_name = getAttrib(item, "installName")
        local_name = getAttrib(item, "localName")

        if install_name is None:
            log.d(TAG, "install_name is null, using name...")
            install_name = name
        if local_name is None:
            log.d(TAG, "local_name is null, using name...")
            local_name = name

        local_item.name = name
        local_item.install_name = install_name
        local_item.local_name = local_name

        if type == TYPE_BINARY:
            rtn = parseBinary(zip_f, local_item)
            log.d(TAG, "parseBinary() result : %d" % rtn)

        elif type == TYPE_LIBRARY:
            rtn = parseLibrary(zip_f, local_item)       
            log.d(TAG, "parseLibrary() result : %d" % rtn)

        elif type == TYPE_MODULE:
            rtn = parseModule(zip_f, local_item)       
            log.d(TAG, "parseModule() result : %d" % rtn)

        elif type == TYPE_PACKAGE:
            rtn = parsePackage(zip_f, local_item)       
            log.d(TAG, "parsePackage() result : %d" % rtn)


    return 0

def installCmd(in_args):

    global force_mode

    # Pop off the "install" line.
    in_args.pop(0)

    parser = ArgumentParser(prog='pm install',
                            description='Install a item or DTF ZIP of items.')
    parser.add_argument('--zip', dest='zipfile', default=None,
                        help='Install a DTF ZIP file containing items.')
    parser.add_argument('--single', metavar="ITEM", dest='single_type',default=None,
                        help='Install a single item.')
    parser.add_argument('--name', metavar="val", dest='single_name', default=None,
                        help="Item name [SINGLE ONLY].")
    parser.add_argument('--local_name', metavar="val", dest='single_local_name', 
                        default=None, help="Item local name [SINGLE ONLY].")
    parser.add_argument('--install_name', metavar="val", dest='single_install_name',
                        default=None, help="Item install name [SINGLE ONLY].")
    parser.add_argument('--version', metavar="val", dest='single_version', default=None,
                        help="Item version (#.# format) [SINGLE ONLY].")
    parser.add_argument('--author', nargs='+', metavar="val", dest='single_author', default=None,
                        help="Item author (email is fine). [SINGLE ONLY].")
    parser.add_argument('--about', nargs='+', metavar="val", dest='single_about', default=None,
                        help="About string for a module. [SINGLE MODULE ONLY].")
    parser.add_argument('--health', metavar="val", dest='single_health', default=None,
                        help="Item health [SINGLE ONLY].")
    parser.add_argument('--auto', dest='single_auto', action='store_const',const=True,
                        default=False, help="Automatically parse module [SINGLE MODULE ONLY].")
    parser.add_argument('--force', dest='force', action='store_const',const=True,
                        default=False, help="Force installation of component(s).")

    args = parser.parse_args(in_args)

    zipfile = args.zipfile
    single_type = args.single_type
    force_mode = args.force

    if zipfile != None and single_type != None:
        print "[ERROR] Cannot install both DTF ZIP and single item. Exiting."
        return -1

    if zipfile == None and single_type == None:
        print "[ERROR] DTF ZIP mode or single item mode not detected. Exiting."
        return -2
 
    # Install zip.
    if zipfile != None:
        if is_zipfile(zipfile):
            return parseZip(zipfile)
        else:
            print "[ERROR] '%s' is not a valid ZIP file or does not exist. Exiting." % (zipfile)
            return -3

    # Install single.
    else:
        auto = args.single_auto
        if auto:
            if single_type == TYPE_MODULE:
                log.i(TAG, "Attempting to auto parse...")
                item = autoParseModule(args)
                if item == None:
                    log.e(TAG, "Error autoparsing module. Exiting.")
                    return -9
            else:
                print "[ERROR] Autoparse is only available for modules! Exiting."
                return -4
        else:
            item = parseSingleItem(args)
            if item == None:
                log.e(TAG, "Error parsing single item, exiting.")
                return -5

        try:
            # First check if we know about this item.
            if itemInstalled(item):

                print "[WARNING] An item with this name is already installed. See details below."
                inst_item = loadItem(item)

                if promptInstall(item, inst_item):
                    return installSingleItem(item)
                else:
                    log.i(TAG, "Module installed skipped.")
            else:
                log.i(TAG, "This is a new item, installing.")
                return installSingleItem(item)

        except KeyError:
            log.e(TAG, "There was something wrong checking if the item was installed. Skipping")
            return -10

    return 0

def deleteCmd(in_args):

    global force_mode

    # Pop off the "delete" line.
    in_args.pop(0)

    parser = ArgumentParser(prog='pm delete',
                            description='Remove a item from disk and database.')
    parser.add_argument('--zip', dest='zipfile', default=None,
                        help='Install a DTF ZIP file containing items.')
    parser.add_argument('--type', metavar="val", dest='single_type',default=None, 
                        help='The type of the item')
    parser.add_argument('--name', metavar="val", dest='single_name', default=None,
                        help="Item to uninstall.")
    parser.add_argument('--force', dest='force', action='store_const',const=True,
                        default=False, help="Force deletion of component.")

    args = parser.parse_args(in_args)

    force_mode = args.force

    # Just a place holder.
    item = Item()

    name = args.single_name
    if name == None:
        print "[ERROR] '--name' is required for delete mode. Exiting."
        return -1
    item.name = name

    single_type = args.single_type
    if single_type not in VALID_TYPES:
        print "[ERROR] Invalid type passed to delete. Exiting."
        return -2
    item.type = single_type

    try:
        # First check if we know about this module.
        if itemInstalled(item):
            inst_item = loadItem(item)

            if promptDelete(inst_item):
                if deleteItem(inst_item) != 1:
                    log.e(TAG, "Error removing item!")
                    return -5
                else:
                    log.i(TAG, "Item removed successfully.")
                    return 0
            else:
                log.i(TAG, "Item removal skipped.")
                return 0
        else:
            print "There is not a item installed with this name and type. Exiting"
            return -3

    except KeyError:
        log.e(TAG, "There was something wrong checking if the item was installed. Exiting")
        return -4

# TODO:  Implement
def exportCmd(args):

    print "Not implemented Yet. :("
    return 0

def main(argv):

    rtn = 0

    log.d(TAG, "Auto creating main.db...")
    if createDtfDb() != 0:
        print "[ERROR] Unable to create the DTF BD, exiting!"
        return -2

    # Pop the program name off forever
    argv.pop(0)
    sub_cmd = argv[0] 

    if sub_cmd == "install":
        rtn = installCmd(argv)
    elif sub_cmd == "delete":
        rtn = deleteCmd(argv)
        pass
    elif sub_cmd == "export":
        rtn = exportCmd(argv)
        pass
        
    return rtn

if __name__ == '__main__':

    rtn = 0

    if len(argv) >= 2:
        rtn = main(argv)
    else:
        usage()

    exit(rtn)
