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
"""Built-in module for getting the status of a project"""

from dtf.module import Module
import dtf.properties as prop
import dtf.adb as DtfAdb

class status(Module):

    """Module class for getting the status of a device"""

    adb = DtfAdb.DtfAdb()

    def execute(self):

        """Main module executor"""

        found = False
        serial = prop.get_prop('Info', 'serial')

        devices = self.adb.get_devices()

        for device in devices:
            if device['serial'] == serial:
                found = True

            break

        print "Status:",

        if found:
            print "Connected"
        else:
            print "Not Connected"

        print "Serial Number: %s" % serial

        return 0
