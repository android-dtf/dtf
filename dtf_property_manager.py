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
# DTF's property management layer.

import ConfigParser
import shlex
from sys import argv

__VERSION__ = 1.0
DTF_CONFIG_FILE = ".dtfini"

def usage():

    print "DTF Property Manager Version %s" % __VERSION__
    print ""
    print "Subcommands:"
    print "    get     Get a property."
    print "    set     Set a property."
    print "    del     Delete a property."
    print "    dump    Dump all properties for current project."
    print "    test    Test if a value is set (returns 1 or 0)."
    print ""

def getProp(args):

    if len(args) != 2:
        print "[ERROR] A section and property must be specified."
        usage()
        return -3

    section =  args[0]
    prop = args[1]  

    config = ConfigParser.ConfigParser()

    try:
        config.read(DTF_CONFIG_FILE)
    except IOError:
        return -5

    # Caller needs to check return if he/she cares what the issue was.
    try:
	rtn = config.get(section, prop)
    except ConfigParser.NoSectionError:
	return -1
    except ConfigParser.NoOptionError:
	return -2

    print rtn
    return 0


def setProp(args):

    if len(args) < 3:
        print "[ERROR] A section, property, and value must be specified."
	usage()
        return -3

    section=args[0]
    prop=args[1]
    value=" ".join(args[2:])

    config = ConfigParser.ConfigParser()

    try:
        config.read(DTF_CONFIG_FILE)
    except IOError:
        print "[ERROR] Unable to read configuration file, does it exist?"
        return -5

    # Add section if it doesnt exist
    if not config.has_section(section):
	config.add_section(section)

    # Set the new parameter
    config.set(section, prop, value)

    f = open(DTF_CONFIG_FILE, 'w')
    config.write(f)
    f.close()

def delProp(args):

    if len(args) != 2:
        print "[ERROR] A section and property must be specified."
        usage()
        return -3

    section=args[0]
    prop=args[1]

    config = ConfigParser.ConfigParser()

    try:
        config.read(DTF_CONFIG_FILE)
    except IOError:
        print "[ERROR] Unable to read configuration file, does it exist?"
        return -5

    rtn = None

    # Remove the parameter
    try:
	rtn = config.remove_option(section, prop)
    except ConfigParser.NoSectionError:
	print "[WARN] Property not removed (the section did not exist)."
	exit -2

    if not rtn:
	print "[WARN] Property not removed (did not exist)."
        return -3

    # Let's make sure we don't have an empty section now.
    if len(config.items(section)) == 0:
        config.remove_section(section)

    f = open(DTF_CONFIG_FILE, 'w')
    config.write(f)
    f.close()

def dumpConfig():

    config = ConfigParser.ConfigParser()
    config.read(DTF_CONFIG_FILE)

    for section in config.sections():
        print "[%s]" % section
        for name, value in config.items(section):
            print "%s = %s" % (name, value)

        print ""

    return  0

def testProp(args):

    if len(args) != 2:
        print "[ERROR] A section and property must be specified."
        usage()
        return -3

    section = args[0]
    prop = args[1]

    config = ConfigParser.ConfigParser()
    config.read(DTF_CONFIG_FILE)

    if config.has_option(section, prop):
        print "1"
        return 1
    else:
        print "0"
        return 0

def main(argv):

    rtn = 0

    # Pop the program name off forever
    argv.pop(0)
    sub_cmd = argv.pop(0)

    if sub_cmd == "get":
        rtn = getProp(argv)
    elif sub_cmd == "set":
        rtn = setProp(argv)
        pass
    elif sub_cmd == "del":
        rtn = delProp(argv)
        pass
    elif sub_cmd == "dump":
        rtn = dumpConfig()
        pass
    elif sub_cmd == "test":
        rtn = testProp(argv)
        pass
    else:
        print "[ERROR] Unknow command '%s' supplied." % sub_cmd
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

