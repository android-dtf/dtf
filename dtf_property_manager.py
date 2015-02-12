#!/usr/bin/env python
# Android Device Testing Framework ("dtf")
# Copyright 2013-2014 Jake Valletta (@jake_valletta)
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
# dtf's property management layer.

# pylint: disable-msg=C0111
import ConfigParser
from sys import argv
from pydtf.dtfconfig import *

__VERSION__ = 1.0
DTF_CONFIG_FILE = ".dtfini"

def usage():

    print "DTF Property Manager Version %s" % __VERSION__
    print ""
    print "Subcommands:"
    print "    get [sec] [prop]        Get a property."
    print "    set [sec] [prop] [val]  Set a property."
    print "    del [sec] [prop]        Delete a property."
    print "    dump                    Dump properties for current project."
    print "    test [sec] [prop]       Test if a value is set (returns 1 or 0)."
    print ""

def main(argv):

    rtn = 0

    # Pop the program name off forever
    argv.pop(0)
    sub_cmd = argv.pop(0)

    # Get a property
    if sub_cmd == "get":

        if len(argv) != 2:
            print "[ERROR] A section and property must be specified."
            usage()
            return -3

        section = argv[0]
        prop = argv[1]

        try:
            value = get_prop(section, prop)
        except PropertyError:
            value = ""
            rtn = -1

        print value

    # Set a property
    elif sub_cmd == "set":

        if len(argv) < 3:
            print "[ERROR] A section, property, and value must be specified."
            usage()
            return -3

        section = argv[0]
        prop = argv[1]
        value = " ".join(argv[2:])

        rtn = set_prop(section, prop, value)

    # Delete a property
    elif sub_cmd == "del":

        if len(argv) != 2:
            print "[ERROR] A section and property must be specified."
            usage()
            return -3

        section = argv[0]
        prop = argv[1]

        rtn = del_prop(section, prop)

    # Dump the config
    elif sub_cmd == "dump":

        config = ConfigParser.ConfigParser()
        config.read(CONFIG_FILE_NAME)

        for section in config.sections():
            print "[%s]" % section
            for name, value in config.items(section):
                print "%s = %s" % (name, value)

            print ""

    # Test if a property is set
    elif sub_cmd == "test":

        if len(argv) != 2:
            print "[ERROR] A section and property must be specified."
            usage()
            return -3

        section = argv[0]
        prop = argv[1]

        rtn = test_prop(section, prop)

    # Something not supported
    else:
        print "[ERROR] Unknown command '%s' supplied." % sub_cmd
        usage()
        rtn = -3

    return rtn

if __name__ == '__main__':

    rtn = 0

    if len(argv) >= 2:
        rtn = main(argv)
    else:
        usage()

    exit(rtn)
