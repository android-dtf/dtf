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
"""Built-in module for handling project properties"""

import ConfigParser

from dtf.module import Module
import dtf.logging as log
import dtf.core.utils as utils

from dtf.properties import (get_prop, set_prop, del_prop,
                            test_prop, PropertyError)


class prop(Module):  # pylint: disable=invalid-name

    """Module class for property management"""

    @classmethod
    def usage(cls):

        """Display module usage"""

        print "dtf Property Manager"
        print "Subcommands:"
        print "    get [sec] [prop]        Get a property."
        print "    set [sec] [prop] [val]  Set a property."
        print "    del [sec] [prop]        Delete a property."
        print "    dump                    Dump current properties."
        print "    test [sec] [prop]       Test if a value is set."
        print ""

        return 0

    def do_get(self, args):

        """Get a property"""

        rtn = 0
        value = ""

        if len(args) != 2:
            log.e(self.name, "A section and property must be specified.")
            rtn = self.usage()

        else:
            section = args[0]
            prop_name = args[1]

            try:
                value = get_prop(section, prop_name)

            except PropertyError:
                rtn = -1

            print value

        return rtn

    def do_set(self, args):

        """Set a property"""

        rtn = 0

        if len(args) < 3:
            log.e(self.name, "A section, prop, and value must be specified.")
            rtn = self.usage()

        else:
            section = args[0]
            prop_name = args[1]
            value = " ".join(args[2:])

            rtn = set_prop(section, prop_name, value)

        return rtn

    def do_del(self, args):

        """Delete a property"""

        rtn = 0

        if len(args) != 2:
            log.e(self.name, "A section and property must be specified.")
            rtn = self.usage()

        else:
            section = args[0]
            prop_name = args[1]

            rtn = del_prop(section, prop_name)

        return rtn

    @classmethod
    def do_dump(cls):

        """Dump entire configuration"""

        config = ConfigParser.ConfigParser()
        config.read(utils.CONFIG_FILE_NAME)

        for section in config.sections():
            print "[%s]" % section
            for name, value in config.items(section):
                print "%s = %s" % (name, value)

            print ""

        return 0

    def do_test(self, args):

        """Test if a value is set or not"""

        rtn = 0

        if len(args) != 2:
            log.e(self.name, "A section and property must be specified.")
            rtn = self.usage()

        else:
            section = args[0]
            prop_name = args[1]

            rtn = test_prop(section, prop_name)

        return rtn

    def execute(self, args):

        """Main module executor"""

        self.name = self.__self__

        rtn = 0

        if len(args) < 1:
            return self.usage()

        sub_cmd = args.pop(0)

        if sub_cmd == 'get':
            rtn = self.do_get(args)

        elif sub_cmd == 'set':
            rtn = self.do_set(args)

        elif sub_cmd == 'del':
            rtn = self.do_del(args)

        elif sub_cmd == 'dump':
            rtn = self.do_dump()

        elif sub_cmd == 'test':
            rtn = self.do_test(args)

        else:
            print "Sub-command '%s' not found!" % sub_cmd
            rtn = self.usage()

        return rtn
