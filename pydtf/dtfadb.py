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
from pydtf.dtfcore import DTF_CLIENT

ADB_BINARY="adb"

class DtfAdb():

    serial = ''
    stdout = None
    stderr = None
    returncode = ''

    def __init__(self):
        self.serial = dtfconfig.get_prop("Info", "serial")

    def __run_command(self, in_cmd):

        cmd = ("%s -s %s %s" %(ADB_BINARY, self.serial, in_cmd)).split(' ')

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

    def pull(self, file_name, local="./"):
        self.__run_command("pull %s %s" % (file_name, local))

    def busybox(self, cmd):
        busybox = dtfconfig.get_prop("Info", "busybox")
        self.shell_command("run-as %s %s %s" % (DTF_CLIENT, busybox, cmd))

    def is_file(self, file_name):
        self.shell_command("ls %s" % file_name)

        if self.stdout[0] == file_name:
            return True
        else:
            return False

    def is_dir(self, dir_name):
        self.shell_command("ls -ld %s" % dir_name)

        line = self.stdout[0]

        if line[-26:] == " No such file or directory":
            return False
        elif line[0] == 'd':
            return True
        else:
            return False
