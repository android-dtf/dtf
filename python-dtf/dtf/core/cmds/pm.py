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
""" dtf's package manager """

import os
import os.path
import zipfile
from argparse import ArgumentParser

from dtf.module import Module
import dtf.globals
import dtf.logging as log
import dtf.core.item
import dtf.core.manifestparser as mp
import dtf.core.packagemanager as packagemanager

TAG = "pm"

DTF_DATA_DIR = dtf.globals.DTF_DATA_DIR
DTF_BINARIES_DIR = dtf.globals.DTF_BINARIES_DIR
DTF_LIBRARIES_DIR = dtf.globals.DTF_LIBRARIES_DIR
DTF_MODULES_DIR = dtf.globals.DTF_MODULES_DIR
DTF_PACKAGES_DIR = dtf.globals.DTF_PACKAGES_DIR
DTF_DB = dtf.globals.DTF_DB

TYPE_BINARY = dtf.core.item.TYPE_BINARY
TYPE_LIBRARY = dtf.core.item.TYPE_LIBRARY
TYPE_MODULE = dtf.core.item.TYPE_MODULE
TYPE_PACKAGE = dtf.core.item.TYPE_PACKAGE

# No log to file.
log.LOG_LEVEL_FILE = 0

LIST_QUIET = 0
LIST_DEFAULT = 1
LIST_VERBOSE = 2


class pm(Module):  # pylint: disable=invalid-name,too-many-public-methods

    """Module class for dtf pm"""

    @classmethod
    def usage(cls):

        """Print Usage"""

        print "dtf Package Manager"
        print ""
        print "Subcommands:"
        print "    delete      Delete an item from main database."
        print "    export      Export entire main database to dtf ZIP."
        print "    install     Install a dtf ZIP or single item."
        print "    list        List all installed items."
        print "    purge       Purge all installed items, reset DB."
        print "    repo        Manage content repos."
        print ""

        return 0

    def do_install(self, args):

        """Attempt to install new content"""

        parser = ArgumentParser(
            prog='pm install',
            description='Install a item or DTF ZIP of items.')
        parser.add_argument('--zip', dest='zipfile', default=None,
                            help='Install a DTF ZIP file containing items.')
        parser.add_argument('--single', metavar="ITEM", dest='single_type',
                            default=None, help='Install a single item.')
        parser.add_argument('--name', metavar="val", dest='single_name',
                            default=None, help="Item name [SINGLE ONLY].")
        parser.add_argument('--local_name', metavar="val",
                            dest='single_local_name', default=None,
                            help="Item local name [SINGLE ONLY].")
        parser.add_argument('--install_name', metavar="val",
                            dest='single_install_name', default=None,
                            help="Item install name [SINGLE ONLY].")
        parser.add_argument('--version', metavar="val", dest='single_version',
                            default=None,
                            help="Item version (#.# format) [SINGLE ONLY].")
        parser.add_argument('--author', nargs='+', metavar="val",
                            dest='single_author', default=None,
                            help="Item author (email is fine). [SINGLE ONLY].")
        parser.add_argument('--about', nargs='+', metavar="val",
                            dest='single_about', default=None,
                            help="About string for a module. [SINGLE ONLY].")
        parser.add_argument('--health', metavar="val", dest='single_health',
                            default=None, help="Item health [SINGLE ONLY].")
        parser.add_argument('--auto', dest='single_auto', action='store_const',
                            const=True, default=False,
                            help="Automatically parse module [SINGLE ONLY].")
        parser.add_argument('--force', dest='force', action='store_const',
                            const=True, default=False,
                            help="Force installation of component(s).")

        parsed_args = parser.parse_args(args)

        zip_file_name = parsed_args.zipfile
        single_type = parsed_args.single_type
        force_mode = parsed_args.force

        if zip_file_name is not None and single_type is not None:
            log.e(TAG, "Cannot install both DTF ZIP and single item. Exiting.")
            return -1

        if zip_file_name is None and single_type is None:
            log.e(TAG, "ZIP mode or single item mode not detected. Exiting.")
            return -2

        # Install zip.
        if zip_file_name is not None:
            if zipfile.is_zipfile(zip_file_name):
                return packagemanager.install_zip(zip_file_name,
                                                  force=force_mode)

            else:
                log.e(TAG, "'%s' is not a valid ZIP file or does not exist."
                      % (zip_file_name))
                return -3

        # Install single.
        else:
            return self.install_single(parsed_args, single_type)

    @classmethod
    def do_delete(cls, args):

        """Attempt to remove content"""

        parser = ArgumentParser(
            prog='pm delete',
            description='Remove a item from disk and database.')
        parser.add_argument('--type', metavar="val", dest='item_type',
                            default=None, help='The type of the item')
        parser.add_argument('--name', metavar="val", dest='item_name',
                            default=None, help="Item to uninstall.")
        parser.add_argument('--force', dest='force', action='store_const',
                            const=True, default=False,
                            help="Force deletion of component.")

        parsed_args = parser.parse_args(args)

        force_mode = parsed_args.force

        name = parsed_args.item_name
        if name is None:
            log.e(TAG, "'--name' is required for delete mode. Exiting.")
            return -1

        item_type = parsed_args.item_type

        if item_type == TYPE_BINARY:
            rtn = packagemanager.delete_binary(name, force=force_mode)
        elif item_type == TYPE_LIBRARY:
            rtn = packagemanager.delete_library(name, force=force_mode)
        elif item_type == TYPE_MODULE:
            rtn = packagemanager.delete_module(name, force=force_mode)
        elif item_type == TYPE_PACKAGE:
            rtn = packagemanager.delete_package(name, force=force_mode)
        else:
            log.e(TAG, "Invalid type passed to delete. Exiting.")
            rtn = -2

        return rtn

    def do_export(self, args):

        """Perform an export"""

        rtn = 0

        parser = ArgumentParser(prog='pm export',
                                description='Export installed content.')
        parser.add_argument('output_name', type=str,
                            help='The output file name.')

        parsed_args = parser.parse_args(args)

        output_name = parsed_args.output_name

        if os.path.isfile(output_name):
            log.e(TAG, "Output file already exists!")
            return -1

        # Generate a list of populated items.
        export_items = self.generate_export_items()

        if len(export_items) == 0:
            log.e(TAG, "Nothing to export!")
            return -2

        export_zip = mp.ExportZip(output_name)

        for item in export_items:
            export_zip.add_item(item)

        export_zip.finalize()
        log.i(TAG, "Export completed!")

        return rtn

    def do_list(self, args):

        """List installed content"""

        rtn = 0

        parser = ArgumentParser(prog='pm list',
                                description='List installed components.')
        parser.add_argument('-v', dest='verbose', action='store_const',
                            const=True, default=False,
                            help="Show additional details about components.")
        parser.add_argument('-q', dest='quiet', action='store_const',
                            const=True, default=False,
                            help="Show only names of components.")
        parser.add_argument('type', type=str, nargs='?',
                            help='Show only requested type.')

        parsed_args = parser.parse_args(args)

        d_filter = parsed_args.type
        verbose = parsed_args.verbose
        quiet = parsed_args.quiet

        if verbose and quiet:
            log.e(TAG, "Unable to be verbose and quiet!")
            return -1

        if verbose:
            verbosity = LIST_VERBOSE
        elif quiet:
            verbosity = LIST_QUIET
        else:
            verbosity = LIST_DEFAULT

        if d_filter is not None:

            if d_filter == "binaries":
                self.print_installed_binaries(verbosity)
            elif d_filter == "libraries":
                self.print_installed_libraries(verbosity)
            elif d_filter == "modules":
                self.print_installed_modules(verbosity)
            elif d_filter == "packages":
                self.print_installed_packages(verbosity)
            else:
                log.e(TAG, "Unknown filter specified : %s" % d_filter)
                rtn = -3

        else:
            self.print_installed_binaries(verbosity)
            self.print_installed_libraries(verbosity)
            self.print_installed_modules(verbosity)
            self.print_installed_packages(verbosity)

        return rtn

    @classmethod
    def do_purge(cls):

        """Purge dtf DB"""

        print "!!!! WARNING !!!!"
        print ""
        print "This will delete all installed content and reset the database!!"
        print "Note: This will not delete any project data."
        print "Are you sure you want to do this? [N/y]",

        res = raw_input()

        if res.lower() == "y":
            return packagemanager.purge()
        else:
            return 0

    def do_repo(self, args):

        """Manage repos"""

        if len(args) < 1:
            print "Usage: dtf pm repo ACTION [args]"
            print ""
            print "  ACTIONs"
            print "    add [repo_name] [url]"
            print "    remove [repo_name]"
            print "    list"

            return 0

        cmd = args.pop(0)

        if cmd == 'add':
            return self.do_repo_add(args)
        elif cmd == 'remove':
            return self.do_repo_remove(args)
        elif cmd == 'list':
            return self.do_repo_list()
        else:
            log.e(TAG, "Invalid repo command: %s"
                  % cmd)
            return -1

    @classmethod
    def do_repo_add(cls, args):

        """Add a repo"""

        if len(args) != 2:
            log.e(TAG, "A repo name and URL is required!")
            return -1

        repo_name = args.pop(0)
        url = args.pop(0)

        return packagemanager.add_repo(repo_name, url)

    @classmethod
    def do_repo_remove(cls, args):

        """remove a repo"""

        if len(args) != 1:
            log.e(TAG, "Must specify a repo name!")
            return -1

        repo_name = args.pop()

        return packagemanager.remove_repo(repo_name)

    @classmethod
    def do_repo_list(cls):

        """List out repos"""

        print "Configured repos:"
        for repo, url in packagemanager.get_repos():
            print "  %s (%s)" % (repo, url)

        return 0

    @classmethod
    def format_version(cls, version_string):

        """Format version of item"""

        if version_string is None:
            return "No Version"

        else:
            return "v%s" % version_string

    @classmethod
    def generate_export_items(cls):

        """Create a list of items"""

        items = list()

        # Get all binaries
        for binary in packagemanager.get_binaries():

            binary.install_name = binary.name
            binary.local_name = "%s/%s" % (DTF_BINARIES_DIR, binary.name)
            items.append(binary)

        # Get all libraries
        for library in packagemanager.get_libraries():

            library.install_name = library.name
            library.local_name = "%s/%s" % (DTF_LIBRARIES_DIR, library.name)
            items.append(library)

        # Get all modules
        for module in packagemanager.get_modules():

            module.install_name = module.name
            module.local_name = "%s/%s" % (DTF_MODULES_DIR, module.name)
            items.append(module)

        # Get all packages
        for package in packagemanager.get_packages():

            package.install_name = package.name
            package.local_name = "%s/%s" % (DTF_PACKAGES_DIR, package.name)
            items.append(package)

        return items

    def print_installed_binaries(self, verbosity):

        """Print installed binaries"""

        binary_list = packagemanager.get_binaries()

        # If we are trying to be quiet, just print each item.
        if verbosity == LIST_QUIET:
            for binary in binary_list:
                print binary.name
            return

        # Otherwise, iterate over and print more
        print "Installed Binaries"

        for binary in binary_list:

            # Format version
            version = self.format_version(binary.version)

            print "\t%s (%s)" % (binary.name, version)
            if verbosity == LIST_VERBOSE:
                print "\t   About: %s" % binary.about
                print "\t   Author: %s" % binary.author
                print "\t   Health: %s" % binary.health

        return 0

    def print_installed_libraries(self, verbosity):

        """Print installed libraries"""
        library_list = packagemanager.get_libraries()

        # If we are trying to be quiet, just print each item.
        if verbosity == LIST_QUIET:
            for library in library_list:
                print library.name
            return

        # Otherwise, iterate over and print more
        print "Installed Libraries"

        for library in library_list:

            # Format version
            version = self.format_version(library.version)

            print "\t%s (%s)" % (library.name, version)
            if verbosity == LIST_VERBOSE:
                print "\t   About: %s" % library.about
                print "\t   Author: %s" % library.author
                print "\t   Health: %s" % library.health

        return 0

    def print_installed_modules(self, verbosity):

        """Print installed modules"""

        module_list = packagemanager.get_modules()

        # If we are trying to be quiet, just print each item.
        if verbosity == LIST_QUIET:
            for module in module_list:
                print module.name
            return

        # Otherwise, iterate over and print more
        print "Installed Modules"

        for module in module_list:

            # Format version
            version = self.format_version(module.version)

            print "\t%s (%s)" % (module.name, version)
            if verbosity == LIST_VERBOSE:
                print "\t   About: %s" % module.about
                print "\t   Author: %s" % module.author
                print "\t   Health: %s" % module.health

        return 0

    def print_installed_packages(self, verbosity):

        """Print installed packages"""

        package_list = packagemanager.get_packages()

        # If we are trying to be quiet, just print each item.
        if verbosity == LIST_QUIET:
            for package in package_list:
                print package.name
            return

        # Otherwise, iterate over and print more
        print "Installed Packages"

        for package in package_list:

            # Format version
            version = self.format_version(package.version)

            print "\t%s (%s)" % (package.name, version)
            if verbosity == LIST_VERBOSE:
                print "\t   About: %s" % package.about
                print "\t   Author: %s" % package.author
                print "\t   Health: %s" % package.health

        return 0

    @classmethod
    def auto_parse_module(cls, args):

        """Automatically parse module and return Item"""

        item = None
        name = args.single_name
        install_name = args.single_install_name
        local_name = args.single_local_name

        if install_name is None:
            log.d(TAG, "install_name is null, using name...")
            install_name = os.path.basename(name)
        if local_name is None:
            log.d(TAG, "local_name is null, using name...")
            local_name = name

        # Does the resource even exist?
        if not os.path.isfile(local_name):
            log.e(TAG, "Local module resource '%s' does not exist!"
                  % (local_name))
            return None

        if packagemanager.is_python_module(local_name, install_name):
            log.d(TAG, "Python mode selected")

            item = packagemanager.parse_python_module(local_name,
                                                      install_name)
            if item is None:
                log.e(TAG, "Error parsing Python module!")
                return None

        elif packagemanager.is_bash_module(local_name):
            log.d(TAG, "Bash mode selected")

            item = packagemanager.parse_bash_module(local_name,
                                                    install_name)
            if item is None:
                log.e(TAG, "Error parsing Bash module!")
                return None

        else:
            log.e(TAG, "Auto parse for Python and Bash failed!")
            return None

        return item

    def parse_single_item(self, args):  # pylint: disable=too-many-branches

        """Parse args, return Item"""

        item = dtf.core.item.Item()

        if args.single_name is None:
            log.e(TAG, "No '--name' specified in single item mode. Exiting.")
            return None

        item.name = args.single_name

        if args.single_type not in dtf.core.item.VALID_TYPES:
            log.e(TAG, "Invalid type passed to single. Exiting.")
            return None

        item.type = args.single_type

        if args.single_health not in dtf.core.item.VALID_HEALTH_VALUES:
            log.e(TAG, "Invalid health specified. Exiting.")
            return None

        item.health = args.single_health

        version = args.single_version
        if version is not None:
            if dtf.core.item.is_valid_version(version):
                item.version = version
            else:
                log.e(TAG, "Version string is not valid. Exiting.")
                return None
        else:
            item.version = None

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
            install_name = os.path.basename(args.single_name)
        if local_name is None:
            log.d(TAG, "local_name is null, using name...")
            local_name = args.single_name

        item.install_name = install_name
        item.local_name = local_name

        if self.check_local_exists(item):
            return item
        else:
            return None

    def install_single(self, args, single_type):

        """Parse and install single item"""

        force_mode = args.force
        rtn = 0

        # Check for auto-mode:
        if args.single_auto:
            # Only modules can be auto-parsed
            if single_type == TYPE_MODULE:
                log.i(TAG, "Attempting to auto parse...")

                item = self.auto_parse_module(args)
                if item is None:
                    log.e(TAG, "Error autoparsing module!")
                    return -9
            else:
                log.e(TAG, "Autoparse is only available for modules!")
                return -4
        # Not auto
        else:
            item = self.parse_single_item(args)
            if item is None:
                log.e(TAG, "Error parsing single item!")
                return -5

        # Now do the installation.
        if single_type == TYPE_BINARY:
            rtn = packagemanager.install_single_binary(item,
                                                       force=force_mode)
        elif single_type == TYPE_LIBRARY:
            rtn = packagemanager.install_single_library(item,
                                                        force=force_mode)
        elif single_type == TYPE_MODULE:
            rtn = packagemanager.install_single_module(item,
                                                       force=force_mode)
        elif single_type == TYPE_PACKAGE:
            rtn = packagemanager.install_single_package(item,
                                                        force=force_mode)
        return rtn

    @classmethod
    def check_local_exists(cls, item):

        """Check if local item exists and print error"""

        if item.type == TYPE_BINARY:
            if not os.path.isfile(item.local_name):
                log.e(TAG, "Local item '%s' does not exist. Exiting."
                      % (item.local_name))
                return None
        elif item.type == TYPE_LIBRARY:
            if not os.path.isdir(item.local_name):
                log.e(TAG, "Local directory '%s' does not exist. Exiting."
                      % (item.local_name))
                return None
        elif item.type == TYPE_MODULE:
            if not os.path.isfile(item.local_name):
                log.e(TAG, "Local item '%s' does not exist. Exiting."
                      % (item.local_name))
                return None
        elif item.type == TYPE_PACKAGE:
            if not os.path.isdir(item.local_name):
                log.e(TAG, "Local directory '%s' does not exist. Exiting."
                      % (item.local_name))
                return None

        return item

    def execute(self, args):

        """Main module executor"""

        self.name = self.__self__

        rtn = 0

        # Set things up if they haven't been already
        if packagemanager.create_data_dirs() != 0:
            log.e(TAG, "Unable to setup dtf data directories!")
            return -4

        if not os.path.isfile(DTF_DB):
            if packagemanager.initialize_db() != 0:
                log.e(TAG, "Error creating and populating dtf db!!")
                return -7

        if len(args) < 1:
            return self.usage()

        sub_cmd = args.pop(0)

        if sub_cmd == "install":
            rtn = self.do_install(args)
        elif sub_cmd == "delete":
            rtn = self.do_delete(args)
        elif sub_cmd == "export":
            rtn = self.do_export(args)
        elif sub_cmd == "list":
            rtn = self.do_list(args)
        elif sub_cmd == "purge":
            rtn = self.do_purge()
        elif sub_cmd == "repo":
            rtn = self.do_repo(args)
        else:
            log.e(TAG, "Sub-command '%s' not found!" % sub_cmd)
            rtn = self.usage()

        return rtn
