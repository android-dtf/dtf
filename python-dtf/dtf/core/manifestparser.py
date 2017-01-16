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
"""Helpers for interacting with manifest.xml + packages"""

import os
import tempfile
import zipfile
from shutil import copy, rmtree

from lxml import etree

import dtf.globals
import dtf.logging as log
import dtf.core.item
import dtf.core.utils as utils

TAG = "dtf-manifestparser"
MANIFEST_NAME = "manifest.xml"


def __get_xml_attrib(element, attrib, default=None):

    """Attempt to retrieve XML attribute"""

    try:
        return element.attrib[attrib]
    except KeyError:
        return default


def __item_from_xml(item, relative_root="./"):

    """create Item object from XML"""

    item_type = __get_xml_attrib(item, "type")
    if item_type is None:
        log.e(TAG, "Found tag with no 'type' attribute, skipping!")
        return None

    if item_type not in dtf.core.item.VALID_TYPES:
        log.e(TAG, "Illegal 'type' attribute found, skipping!")
        return None

    name = __get_xml_attrib(item, "name")
    if name is None:
        log.e(TAG, "Found NULL named moduled, skipping!")
        return None

    # Ok, lets start.  We can generically parse.
    local_item = dtf.core.item.Item()

    local_item.type = item_type
    local_item.major_version = __get_xml_attrib(item, "majorVersion")
    local_item.minor_version = __get_xml_attrib(item, "minorVersion")
    local_item.health = __get_xml_attrib(item, "health")
    local_item.author = __get_xml_attrib(item, "author")
    local_item.about = __get_xml_attrib(item, "about")

    install_name = __get_xml_attrib(item, "installName")
    local_name = __get_xml_attrib(item, "localName")

    if install_name is None:
        log.d(TAG, "install_name is null, using name...")
        install_name = name

    if local_name is None:
        log.d(TAG, "local_name is null, using name...")
        local_name = name
    else:
        local_name = os.path.normpath("%s/%s" % (relative_root, local_name))

    local_item.name = name
    local_item.install_name = install_name
    local_item.local_name = local_name

    return local_item


def parse_manifest(manifest_data, relative_root="./"):

    """Parse a blob of manifest data"""

    manifest = None
    manifest_root = None
    item_list = list()

    # Read Manifest
    try:
        manifest_root = etree.XML(manifest_data)
    except etree.XMLSyntaxError:
        log.e(TAG, "Error parsing XML file! Exiting.")
        return -4

    # Processing Stuff
    items = manifest_root.xpath("/Items/Item")

    for item in items:
        item_list.append(__item_from_xml(item, relative_root=relative_root))

    manifest = Manifest()
    manifest.items = item_list
    manifest.root_dir = relative_root

    return manifest


def parse_manifest_file(manifest_file_name):

    """Parse a standalone manifest.xml"""

    manifest_data = open(manifest_file_name).read()
    root_dir = os.path.dirname(manifest_file_name)

    return parse_manifest(manifest_data, relative_root=root_dir)


class Manifest(object):

    """Class wrapper for interacting with manifest.xml"""

    items = None
    root_dir = ""

    def __init__(self):

        """Initializer method"""
        self.items = list()

    @classmethod
    def item_to_xml_binaries(cls, etree_root, export_items):

        """Export all binaries"""

        # Add binaries
        bin_items = [item for item in export_items
                     if item.type == dtf.core.item.TYPE_BINARY]

        for item in bin_items:

            item_xml = etree.SubElement(etree_root, 'Item')
            item_xml.attrib['type'] = dtf.core.item.TYPE_BINARY
            item_xml.attrib['name'] = item.name

            if item.major_version is None or item.minor_version is None:
                log.w(TAG, "Skipping version for %s" % item.name)
            else:
                item_xml.attrib['majorVersion'] = item.major_version
                item_xml.attrib['minorVersion'] = item.minor_version

            if item.health is None:
                log.w(TAG, "Skipping health for %s" % item.name)
            else:
                item_xml.attrib['health'] = item.health

            if item.author is None:
                log.w(TAG, "Skipping author for %s" % item.name)
            else:
                item_xml.attrib['author'] = item.author

            item_xml.attrib['localName'] = "binaries/%s" % item.install_name

        return

    @classmethod
    def item_to_xml_libraries(cls, etree_root, export_items):

        """Export all libraries"""

        lib_items = [item for item in export_items
                     if item.type == dtf.core.item.TYPE_LIBRARY]

        for item in lib_items:

            item_xml = etree.SubElement(etree_root, 'Item')
            item_xml.attrib['type'] = dtf.core.item.TYPE_LIBRARY
            item_xml.attrib['name'] = item.name

            if item.major_version is None or item.minor_version is None:
                log.w(TAG, "Skipping version for %s" % item.name)
            else:
                item_xml.attrib['majorVersion'] = item.major_version
                item_xml.attrib['minorVersion'] = item.minor_version

            if item.health is None:
                log.w(TAG, "Skipping health for %s" % item.name)
            else:
                item_xml.attrib['health'] = item.health

            if item.author is None:
                log.w(TAG, "Skipping author for %s" % item.name)
            else:
                item_xml.attrib['author'] = item.author

            item_xml.attrib['localName'] = "libraries/%s" % item.install_name

        return

    @classmethod
    def item_to_xml_modules(cls, etree_root, export_items):

        """Export all modules"""

        mod_items = [item for item in export_items
                     if item.type == dtf.core.item.TYPE_MODULE]

        for item in mod_items:

            item_xml = etree.SubElement(etree_root, 'Item')
            item_xml.attrib['type'] = dtf.core.item.TYPE_MODULE
            item_xml.attrib['name'] = item.name

            if item.major_version is None or item.minor_version is None:
                log.w(TAG, "Skipping version for %s" % item.name)
            else:
                item_xml.attrib['majorVersion'] = item.major_version
                item_xml.attrib['minorVersion'] = item.minor_version

            if item.health is None:
                log.w(TAG, "Skipping health for %s" % item.name)
            else:
                item_xml.attrib['health'] = item.health

            if item.about is None:
                log.w(TAG, "Skipping about for %s" % item.name)
            else:
                item_xml.attrib['about'] = item.about

            if item.author is None:
                log.w(TAG, "Skipping author for %s" % item.name)
            else:
                item_xml.attrib['author'] = item.author

            item_xml.attrib['localName'] = "modules/%s" % item.install_name

        return

    @classmethod
    def item_to_xml_packages(cls, etree_root, export_items):

        """Export all packages"""

        pkg_items = [item for item in export_items
                     if item.type == dtf.core.item.TYPE_PACKAGE]

        for item in pkg_items:

            item_xml = etree.SubElement(etree_root, 'Item')
            item_xml.attrib['type'] = dtf.core.item.TYPE_PACKAGE
            item_xml.attrib['name'] = item.name

            if item.major_version is None or item.minor_version is None:
                log.w(TAG, "Skipping version for %s" % item.name)
            else:
                item_xml.attrib['majorVersion'] = item.major_version
                item_xml.attrib['minorVersion'] = item.minor_version

            if item.health is None:
                log.w(TAG, "Skipping health for %s" % item.name)
            else:
                item_xml.attrib['health'] = item.health

            if item.author is None:
                log.w(TAG, "Skipping author for %s" % item.name)
            else:
                item_xml.attrib['author'] = item.author

            item_xml.attrib['localName'] = "packages/%s" % item.install_name

        return

    def to_string(self):

        """Generate XML string list of items"""

        temp_manifest_f = tempfile.NamedTemporaryFile()

        root = etree.Element('Items')

        # Add binaries
        self.item_to_xml_binaries(root, self.items)

        # Add libraries
        self.item_to_xml_libraries(root, self.items)

        # Add modules
        self.item_to_xml_modules(root, self.items)

        # Add packages
        self.item_to_xml_packages(root, self.items)

        # Write it all out
        export_tree = etree.ElementTree(root)
        export_tree.write(temp_manifest_f, pretty_print=True)
        temp_manifest_f.flush()

        return temp_manifest_f


class ExportZip(object):

    """Class wrapper for interacting with ZIP exports"""

    zip_name = ""

    def __init__(self, zip_name):

        self.zip_name = zip_name
        self.manifest = Manifest()

        # If the file exists, we open and parse the manifest.
        if os.path.isfile(zip_name):
            self.zip_f = zipfile.ZipFile(zip_name, 'r',
                                         compression=zipfile.ZIP_DEFLATED)

            if not utils.file_in_zip(self.zip_f, MANIFEST_NAME):
                log.e(TAG, "Manifest doesnt exist in ZIP!")
                raise KeyError

            manifest_data = self.zip_f.read(MANIFEST_NAME)
            self.manifest = parse_manifest(manifest_data)

        # Otherwise, we just create a new one.
        else:
            self.zip_f = zipfile.ZipFile(zip_name, 'w',
                                         compression=zipfile.ZIP_DEFLATED)
            self.manifest = Manifest()

    def __add_file(self, subdir, item):

        """Add a file to the correct subdirectory"""

        install_to = "%s/%s" % (subdir, item.install_name)

        log.d(TAG, "Adding '%s' as '%s'"
              % (item.install_name, install_to))

        self.zip_f.write(item.local_name, install_to)

    def __add_tree(self, subdir, item):

        """Add entire tree to ZIP"""

        local_replace = os.path.dirname(item.local_name)

        for root, _, files in os.walk(item.local_name):
            for file_name in files:
                file_path = os.path.join(root, file_name)

                install_to = file_path.replace(local_replace, subdir, 1)

                log.d(TAG, "Adding dir '%s' as '%s'"
                      % (file_path, install_to))

                self.zip_f.write(file_path, install_to)

    def __copy_zip_file(self, local_name, install_name, install_dir):

        """Copy file in ZIP to directory"""

        install_path = install_dir + install_name

        log.d(TAG, "Copying '%s' to '%s'..." % (local_name, install_path))
        temp_f = tempfile.NamedTemporaryFile(mode='w', delete=False)

        temp_f.write(self.zip_f.read(local_name))
        temp_f.flush()

        copy(temp_f.name, install_path)

        os.chmod(install_path, 0755)

        temp_f.close()

        os.remove(temp_f.name)

        log.d(TAG, "Copy complete!")

        return 0

    def __copy_zip_tree(self, local_name, install_name, install_dir):

        """Copy directory in ZIP to directory"""

        install_path = install_dir + install_name + '/'

        # We need to remove the first one
        rmtree(install_path, ignore_errors=True)

        reduced_list = [file_f for file_f in self.zip_f.namelist()
                        if file_f.startswith(local_name)
                        and file_f != local_name+'/']

        self.zip_f.extractall(dtf.globals.DTF_DATA_DIR, reduced_list)

        log.d(TAG, "Copy complete!")
        return 0

    def __add_export_content(self):

        """Add content to our ZIP file"""

        for item in self.manifest.items:

            if item.type == dtf.core.item.TYPE_BINARY:
                self.__add_file("binaries/", item)
            elif item.type == dtf.core.item.TYPE_LIBRARY:
                self.__add_tree("libraries/", item)
            elif item.type == dtf.core.item.TYPE_MODULE:
                self.__add_file("modules/", item)
            elif item.type == dtf.core.item.TYPE_PACKAGE:
                self.__add_tree("packages/", item)

    def add_item(self, item):

        """Add an item to manifest list"""

        self.manifest.items.append(item)

    def assert_item(self, item):

        """Confirm item is backed for files"""

        if item.type in [dtf.core.item.TYPE_MODULE,
                         dtf.core.item.TYPE_BINARY]:
            if not utils.file_in_zip(self.zip_f, item.local_name):
                return False

        elif item.type in [dtf.core.item.TYPE_LIBRARY,
                           dtf.core.item.TYPE_PACKAGE]:
            if not utils.directory_in_zip(self.zip_f, item.local_name):
                return False

        return True

    def iter_items(self):

        """Return a iterable list of items"""

        return self.manifest.items

    def install_item_to(self, item, dest_dir):

        """Install item to a location"""

        if utils.file_in_zip(self.zip_f, item.local_name):
            return self.__copy_zip_file(item.local_name,
                                        item.install_name, dest_dir)
        elif utils.directory_in_zip(self.zip_f, item.local_name):
            return self.__copy_zip_tree(item.local_name,
                                        item.install_name, dest_dir)
        else:
            return -1

    def finalize(self):

        """Write out all data and add content"""

        # Add the manifest XML
        temp_manifest = self.manifest.to_string()
        self.zip_f.write(temp_manifest.name, MANIFEST_NAME)

        # Now, for each item in the manifest, add the actual content
        self.__add_export_content()

        # Close it all out
        self.zip_f.close()
