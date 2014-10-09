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
# dtf core functionality from Python
from subprocess import Popen, PIPE
from pydtf import dtfconfig

# Core Globals
DTF_VERSION='1.1.0'


# Launch a module
def launch_module(module, args):

    cmd = ("dtf %s %s" %(module, args)).split(' ')

    p = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=False)
    stdout = p.stdout.read().split("\r\n")
    stderr = p.stderr.read().split("\r\n")

    p.terminate()

    return stdout, stderr
