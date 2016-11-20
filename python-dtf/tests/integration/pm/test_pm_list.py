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
"""Integration tests for the "pm list" utility"""

import dtf.testutils as testutils


def test_no_args():

    """Running list with no args"""

    rtn = testutils.dtf("pm list")
    assert(rtn.return_code == 0)

    rtn = testutils.dtf("pm list -v")
    assert(rtn.return_code == 0)


def test_quiet_verbose():

    """Try and fail to print verbose + quiet"""

    rtn = testutils.dtf("pm list -vq")
    assert(rtn.return_code == 255)


def test_binaries():

    """List only binaries"""

    rtn = testutils.dtf("pm list binaries")
    assert(rtn.return_code == 0)

    rtn = testutils.dtf("pm list binaries -v")
    assert(rtn.return_code == 0)

    rtn = testutils.dtf("pm list binaries -q")
    assert(rtn.return_code == 0)


def test_libraries():

    """List only libraries"""

    rtn = testutils.dtf("pm list libraries")
    assert(rtn.return_code == 0)

    rtn = testutils.dtf("pm list libraries -v")
    assert(rtn.return_code == 0)

    rtn = testutils.dtf("pm list libraries -q")
    assert(rtn.return_code == 0)


def test_modules():

    """List only modules"""

    rtn = testutils.dtf("pm list modules")
    assert(rtn.return_code == 0)

    rtn = testutils.dtf("pm list modules -v")
    assert(rtn.return_code == 0)

    rtn = testutils.dtf("pm list modules -q")
    assert(rtn.return_code == 0)


def test_packages():

    """List only packages"""

    rtn = testutils.dtf("pm list packages")
    assert(rtn.return_code == 0)

    rtn = testutils.dtf("pm list packages -v")
    assert(rtn.return_code == 0)

    rtn = testutils.dtf("pm list packages -q")
    assert(rtn.return_code == 0)
