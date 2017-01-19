# Android Device Testing Framework ("dtf")
# Copyright 2013-2016 Jake Valletta (@jake_valletta)
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
"""Unit tests for testing included wrappers"""

from __future__ import absolute_import
import dtf.included as included
import dtf.core.utils as utils
import dtf.testutils as testutils


def test_aapt():

    """Run test aapt command"""
    data_file = testutils.DataFile("hello-world.apk")

    stdout, stderr, rtn = included.aapt("d badging %s" % str(data_file))

    assert rtn == 0

def test_apktool():

    """Run test apktool command"""

    data_file = testutils.DataFile("hello-world.apk")

    stdout, stderr, rtn = included.apktool("d %s" % str(data_file))

    utils.delete_tree("hello-world")

    assert rtn == 0

def test_smali():

    """Run test smali/baksmali command"""

    data_file = testutils.DataFile("hello-world.apk")

    stdout, stderr, rtn_bak = included.baksmali("-o out %s" % str(data_file))
    stdout, stderr, rtn_smali = included.smali("-o classes.dex out")

    utils.delete_tree("out")
    utils.delete_file("classes.dex")

    assert rtn_bak == 0
    assert rtn_smali == 0


def test_axmlprinter2():

    """Run test axmlprinter2 command"""

    data_file = testutils.DataFile("valid_android_manifest.xml")
    out_file = "out.xml"

    rtn = included.axmlprinter2(str(data_file), out_file)

    utils.delete_file(out_file)

    assert rtn == 0
