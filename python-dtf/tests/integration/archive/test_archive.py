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
"""Integration tests for archiving"""

import os.path

import dtf.testutils as testutils


def test_no_args():

    """Run with not args"""

    contents = ("[Info]\n"
                "sdk = 23")

    testutils.deploy_config_raw(contents)

    rtn = testutils.dtf("archive")

    testutils.undeploy()

    assert(rtn.return_code == 0)


def test_help():

    """Force the usage"""

    contents = ("[Info]\n"
                "sdk = 23")

    testutils.deploy_config_raw(contents)

    rtn = testutils.dtf("archive -h")

    testutils.undeploy()

    assert(rtn.return_code == 0)


def test_no_name():

    """Attempt create an archive using builtin name"""

    version_string = "android-17_XTS"
    zip_name = "%s.zip" % version_string
    contents = ("[Info]\n"
                "sdk = 23\n"
                "version-string = %s" % version_string)

    testutils.deploy_config_raw(contents)

    rtn = testutils.dtf("archive create")

    testutils.undeploy()

    assert(rtn.return_code == 0)
    assert(os.path.isfile(zip_name))

    os.remove(zip_name)
