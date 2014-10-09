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
# Python helper for using "adb"
from subprocess import Popen, PIPE
from pydtf import dtfconfig

ADB_BINARY="adb"
SERIAL = dtfconfig.get_prop("Info", "serial")

class DtfAdb():

    stdout = None
    stderr = None
    returncode = ""

    def __run_command(self, in_cmd):

        cmd = ("%s -s %s %s" %(ADB_BINARY, SERIAL, in_cmd)).split(' ')

        p = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=False)
        self.stdout = p.stdout.read().split("\r\n")
        self.stderr = p.stderr.read().split("\r\n")

        p.terminate()

    def get_output(self):
        return self.stdout

    def get_errors(self):
        return self.stderr

    def shell_command(self, cmd):
        self.__run_command("shell %s" % cmd)

    def wait_for_device(self):
        self.__run_command("wait-for-device")
