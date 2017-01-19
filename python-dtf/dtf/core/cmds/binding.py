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
"""Built-in module for getting a binding path"""

from __future__ import absolute_import
from __future__ import print_function
from dtf.globals import get_all_bindings, get_binding, GlobalPropertyError
from dtf.module import Module
import dtf.logging as log

TAG = "binding"


class binding(Module):  # pylint: disable=invalid-name

    """Module class for listing local modules"""

    @classmethod
    def do_print_all(cls):

        """Print all bindings"""

        try:
            for bind_key, value in get_all_bindings():
                print("%s : %s" % (bind_key, value))
        except GlobalPropertyError:
            log.e(TAG, "Unable to list bindings!")
            return -1

        return 0

    @classmethod
    def do_print_binding(cls, bind_key):

        """Print a single binding"""

        try:
            print(get_binding(bind_key))
        except GlobalPropertyError:
            log.e(TAG, "Unable to find binding: %s" % bind_key)
            return -1

        return 0

    def execute(self, args):

        """Main module executor"""

        if len(args) == 0:
            return self.do_print_all()
        else:
            return self.do_print_binding(args[0])
