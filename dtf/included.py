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
"""Python wrapper for Android tools"""

from dtf.globals import DTF_INCLUDED_DIR

from subprocess import Popen, PIPE


def aapt(cmd):

    """aapt wrapper"""

    aapt_path = "%s/aapt/aapt-22.0.1" % DTF_INCLUDED_DIR
    cmd = ("%s %s" % (aapt_path, cmd)).split(' ')

    proc = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=False)

    stdout, stderr = proc.communicate()

    stdout = stdout.split("\n")
    stderr = stderr.split("\n")
    rtn = proc.returncode

    return stdout, stderr, rtn


def apktool(cmd):

    """apktool wrapper"""

    apktool_path = ("%s/apktool/apktool_2.0.3-83f327-SNAPSHOT.jar"
                    % DTF_INCLUDED_DIR)

    java_args = "java -Xmx512M -jar"

    cmd = ("%s %s %s" % (java_args, apktool_path, cmd)).split(' ')

    proc = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=False)

    stdout, stderr = proc.communicate()

    stdout = stdout.split("\n")
    stderr = stderr.split("\n")
    rtn = proc.returncode

    return stdout, stderr, rtn


def smali(cmd):

    """smali wrapper"""

    smali_path = ("%s/smali/smali-2.1.0-3e265038.jar"
                  % DTF_INCLUDED_DIR)

    java_args = "java -Xmx512M -jar"

    cmd = ("%s %s %s" % (java_args, smali_path, cmd)).split(' ')

    proc = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=False)

    stdout, stderr = proc.communicate()

    stdout = stdout.split("\n")
    stderr = stderr.split("\n")
    rtn = proc.returncode

    return stdout, stderr, rtn


def baksmali(cmd):

    """baksmali wrapper"""

    baksmali_path = ("%s/smali/baksmali-2.1.0-3e265038.jar"
                     % DTF_INCLUDED_DIR)

    java_args = "java -Xmx512M -jar"

    cmd = ("%s %s %s" % (java_args, baksmali_path, cmd)).split(' ')

    proc = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=False)

    stdout, stderr = proc.communicate()

    stdout = stdout.split("\n")
    stderr = stderr.split("\n")
    rtn = proc.returncode

    return stdout, stderr, rtn


def dex2jar():

    """dex2jar wrapper"""

    raise NotImplementedError


def axmlprinter2(manifest_file_name, out_file_name):

    """axmlprinter2 wrapper"""

    axmlprinter2_path = ("%s/axmlprinter2/axmlprinter2.jar"
                         % DTF_INCLUDED_DIR)

    java_args = "java -Xmx256M -jar"

    cmd = ("%s %s %s"
           % (java_args, axmlprinter2_path, manifest_file_name)).split(' ')

    proc = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=False)

    stdout = proc.communicate()[0]

    rtn = proc.returncode

    if len(stdout) == 0:
        return -1

    out_f = open(out_file_name, 'wb')

    try:
        out_f.write(stdout)
    finally:
        out_f.close()

    return rtn
