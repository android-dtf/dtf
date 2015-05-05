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
from hashlib import md5
from os import getcwd, pardir
from os.path import abspath, join, isfile
from pydtf import dtfconfig
from pydtf.dtfglobals import DTF_INCLUDED, DTF_DIR
from subprocess import Popen, PIPE

# Core Globals
DTF_VERSION='1.1.0-dev'

# Client stuff
DTF_CLIENT="com.dtf.client"

def __upsearch(file_name, dir):
        if isfile("%s/%s" % (dir,file_name)):
            return dir
        else:
            new_dir = abspath(join(dir, pardir))
            if dir == new_dir:
                return None
            return __upsearch(file_name, new_dir)

TOP = __upsearch(".dtfini", getcwd())

# MD5 local file
def md5_local(file_path):

    f = open(file_path,'rb')

    m = md5()
    while True:
        data = f.read(128)
        if not data:
            break
        m.update(data)
    return m.hexdigest()


# Use apktool
def apktool(cmd):

    apktool_path = "%s/apktool/apktool_2.0.1-548137-SNAPSHOT.jar" % DTF_INCLUDED
    java_args = "java -Xmx512M -jar"

    cmd = ("%s %s %s" %(java_args, apktool_path, cmd)).split(' ')

    p = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=False)

    (out, err) = p.communicate()

    stdout = out.split("\n")
    stderr = out.split("\n")
    rtn = p.returncode

    return stdout, stderr, rtn

# Use apksign
def apksign(cmd):
    raise NotImplementedError

# Use smali
def smali(cmd):

    smali_path = "%s/smali/smali-2.0.3-686cf35c-dirty.jar" % DTF_INCLUDED
    java_args = "java -Xmx512M -jar"

    cmd = ("%s %s %s" %(java_args, smali_path, cmd)).split(' ')

    p = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=False)
    stdout = p.stdout.read().split("\n")
    stderr = p.stderr.read().split("\n")

    rtn = p.wait()

    return stdout, stderr, rtn

# Use baksmali
def baksmali(cmd):

    baksmali_path = "%s/smali/baksmali-2.0.3-686cf35c-dirty.jar" % DTF_INCLUDED
    java_args = "java -Xmx512M -jar"

    cmd = ("%s %s %s" %(java_args, baksmali_path, cmd)).split(' ')

    p = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=False)
    stdout = p.stdout.read().split("\n")
    stderr = p.stderr.read().split("\n")

    rtn = p.wait()

    return stdout, stderr, rtn

# Use dex2jar
def dex2jar(cmd):
    raise NotImplementedError

# Use axmlprinter2
def axmlprinter2(manifest_file_name, out_file_name):

    axmlprinter2_path = "%s/axmlprinter2/axmlprinter2.jar" % DTF_INCLUDED
    java_args = "java -Xmx256M -jar"

    cmd = ("%s %s %s" %(java_args, axmlprinter2_path, manifest_file_name)).split(' ')

    p = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=False)
    stdout = p.stdout.read()
    stderr = p.stderr.read()

    rtn = p.wait()
 

    if len(stdout) == 0:
        return -1

    out_f = open(out_file_name, 'wb')

    try:
        out_f.write(stdout)
    finally:
        out_f.close()

    return rtn

# Launch a module
def launch_module(module, args):

    cmd = ("dtf %s %s" %(module, args)).split(' ')

    p = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=False)
    stdout = p.stdout.read().split("\n")
    stderr = p.stderr.read().split("\n")

    rtn = p.wait()

    return stdout, stderr, rtn


# Launch a binary
def launch_binary(binary, args, launcher=None):

    if launcher == None:
        cmd = ("%s/bin/%s %s" % (DTF_DIR, binary, args)).split(' ')
    else:
        cmd = ("%s %s/bin/%s %s" % (launcher, DTF_DIR, binary, args)).split(' ')
     
    p = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=False)
    stdout = p.stdout.read().split("\n")
    stderr = p.stderr.read().split("\n")

    rtn = p.wait()

    return stdout, stderr, rtn
