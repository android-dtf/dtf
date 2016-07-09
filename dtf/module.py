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
"""dtf Module Template"""

import dtf.logging as log
import os

TAG = "dtf-module"


class Module(object):

    """
    Base class for creating a python module with dtf. Override the
    fields below, and implement an execute(self, args) method.
    """

    name = "MyModule"
    version = "1.0"
    license = "N/A"
    health = "beta"
    author = "N/A"
    about = "A basic dtf module."

    __self__ = ''

    def run(self, args):

        """
        Internal entry point for starting a module.  It basically executes
        the 'execute' method if it exists.
        """

        # Save module name
        self.__self__ = type(self).__name__

        # Determine if we have an execute() method.
        if hasattr(self, 'execute'):

            # Do python logging override
            try:
                log.LOG_LEVEL_STDOUT = int(os.environ['GLOG_LEVEL'])
            except KeyError:
                pass
            except ValueError:
                log.w(TAG, "Invalid GLOG_LEVEL value (0-5 is allowed)")

            result = getattr(self, 'execute')(args)

        else:

            log.e(TAG, "Module '%s' does not define a entry point!"
                  % self.__self__)
            result = None

        return result
