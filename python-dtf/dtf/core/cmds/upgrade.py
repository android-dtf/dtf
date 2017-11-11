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
"""Built-in module for archiving a project"""

from __future__ import absolute_import
from __future__ import print_function

import tempfile
from argparse import ArgumentParser

import requests

import dtf.core.autoconfig as autoconfig
import dtf.module as module
import dtf.logging as log

BRANCH_DEFAULT = 'master'
UPGRADE_SCRIPT_TEMPLATE = ("https://raw.githubusercontent.com/android-dtf/"
                           "dtf/%s/installscript/install.sh")

UPGRADE_TAR_TEMPLATE = ("https://raw.githubusercontent.com/android-dtf/"
                        "dtf/%s/dtf-included/build/included.tar")


class upgrade(module.Module):  # pylint: disable=invalid-name

    """Module class for performing updates"""

    @classmethod
    def usage(cls):

        """Display module usage"""

        print('dtf Client Manager')
        print('Subcommands:')
        print('    core       Update dtf framework.')
        print('    included   Update just the bundled TAR.')
        print('')

        return 0

    def __download_file(self, url, file_name):

        """Download a file from URL to tempfile"""

        try:
            req = requests.get(url, verify=True, stream=True,
                               allow_redirects=True)

        except requests.exceptions.RequestException as excpt:

            log.e(self.name, "Error pulling update script!")
            print(excpt)
            return None

        if not req.ok:
            return None

        temp_file_name = "%s/%s" % (tempfile.gettempdir(), file_name)

        temp_f = open(temp_file_name, "wb")

        for chunk in req.iter_content(chunk_size=1024):
            if chunk:
                temp_f.write(chunk)

        # Reset the seek
        temp_f.close()

        return temp_file_name

    def do_core_upgrade(self, args):

        """Perform upgrade of dtf"""

        parser = ArgumentParser(prog='upgrade core',
                                description='Update dtf framework.')
        parser.add_argument('--reconfigure', action='store_true',
                            help="Just reconfig (post upgrade).")
        parser.add_argument('--branch', dest='branch',
                            default=BRANCH_DEFAULT,
                            help="Specify the branch to pull from.")
        parsed_args = parser.parse_args(args)

        # First, is this just a reconfig?
        if parsed_args.reconfigure:
            log.i(self.name, "Performing reconfiguration...")
            return autoconfig.initialize_from_local(is_full=True)

        log.i(self.name, "Downloading update script...")

        upgrade_script_url = UPGRADE_SCRIPT_TEMPLATE % parsed_args.branch

        upgrade_script_name = self.__download_file(upgrade_script_url,
                                                   'dtf_upgrade.sh')
        if upgrade_script_name is None:
            log.e(self.name, "Unable to download: %s" % upgrade_script_url)
            return -1

        log.i(self.name, "Update script downloaded. To complete install run:")
        log.i(self.name, "  chmod u+x %s" % upgrade_script_name)
        log.i(self.name, "  %s" % upgrade_script_name)

        return 0

    def do_included_upgrade(self, args):

        """Perform upgrade of only included"""

        parser = ArgumentParser(prog='upgrade included',
                                description='Update the bundled TAR.')
        parser.add_argument('--branch', dest='branch',
                            default=BRANCH_DEFAULT,
                            help="Specify the branch to pull from.")

        parsed_args = parser.parse_args(args)

        log.i(self.name, "Performing included upgrade...")

        upgrade_tar_url = UPGRADE_TAR_TEMPLATE % parsed_args.branch

        # First pull
        tar_name = self.__download_file(upgrade_tar_url, 'dtf_included.tar')
        if tar_name is None:
            log.e(self.name, "Unable to download: %s" % upgrade_tar_url)
            return -1

        # Now we perform the reconfiguration
        return autoconfig.initialize_from_tar(tar_name, is_full=False,
                                              clean_up=True)

    def execute(self, args):

        """Main module executor"""

        self.name = self.__self__

        rtn = 0

        if len(args) < 1:
            return self.usage()

        sub_cmd = args.pop(0)

        if sub_cmd == 'core':
            rtn = self.do_core_upgrade(args)

        elif sub_cmd == 'included':
            rtn = self.do_included_upgrade(args)

        else:
            print("Sub-command '%s' not found!" % sub_cmd)
            rtn = self.usage()

        return rtn
