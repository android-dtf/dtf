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

import dtf.properties as prop
import dtf.logging as log

from dtf.module import Module

import os
from subprocess import Popen


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

    @classmethod
    def make_zip(cls, zip_name):

        """Make a ZIP file"""

        null_f = open(os.devnull, 'w')
        cmd = ['zip', '-r', zip_name, '.']

        proc = Popen(cmd, stdout=null_f, stderr=null_f, shell=False)

        proc.wait()
        null_f.close()

        return proc.returncode

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
