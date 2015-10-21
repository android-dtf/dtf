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
"""Built-in module for listing local modules"""

import dtf.core.utils as utils

from dtf.module import Module

from os import listdir
from os.path import isfile, join


class local(Module):

    """Module class for listing local modules"""

    @classmethod
    def get_locals(cls):

        """List 'local_modules' directory"""

        local_path = "%s/local_modules" % utils.get_project_root()

        return [f for f in listdir(local_path) if isfile(join(local_path, f))]

    def execute(self, args):

        """Main module executor"""

        print "Local Modules:"

        for l_module in self.get_locals():

            print "   %s" % l_module

        return 0
