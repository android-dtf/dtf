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
"""Built-in module for archiving a project"""

import os
import zipfile

import dtf.properties as prop
import dtf.logging as log
from dtf.module import Module


class archive(Module):  # pylint: disable=invalid-name

    """Module class for archiving a project"""

    @classmethod
    def usage(cls):

        """Module usage"""

        print "dtf Archiver"
        print ""
        print "Subcommands:"
        print "    create    Archive the current project."
        print ""

        return 0

    def make_zip(self, zip_name):

        """Make a ZIP file"""

        zip_f = None

        try:
            zip_f = zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED)
        except RuntimeError:
            log.e(self.name, "ZIP_DEFLATE not available!")
            return -1

        # pylint: disable=unused-variable
        for root, dirs, files in os.walk(os.getcwd()):
            for file_to_add in files:
                zip_f.write(os.path.join(root, file_to_add))

        zip_f.close()

        return 0

    def do_create(self, args):

        """Create the archive"""

        zip_name = ""

        if len(args) == 0:
            zip_name = "%s.zip" % prop.get_prop('Info', 'version-string')

        else:
            zip_name = args.pop()

        log.i(self.name, "Archiving to '%s'..." % zip_name)

        rtn = self.make_zip(zip_name)

        if rtn != 0:
            log.e(self.name, "Unable to archive project!")

        return rtn

    def execute(self, args):

        """Main module executor"""

        self.name = self.__self__

        rtn = 0

        if len(args) < 1:
            return self.usage()

        sub_cmd = args.pop(0)

        if sub_cmd == 'create':
            rtn = self.do_create(args)

        else:
            print "Sub-command '%s' not found!" % sub_cmd
            rtn = self.usage()

        return rtn
