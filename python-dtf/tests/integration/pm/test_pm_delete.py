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
"""Integration tests for the "pm delete" utility"""

from __future__ import absolute_import
import dtf.testutils as testutils
import dtf.core.utils as utils


class PmDeletetTests(testutils.BasicIntegrationTest):

    """Wraper for integration tests"""

    def test_no_args(self):

        """Run with no args"""

        rtn = self.run_cmd("pm delete")
        assert(rtn.return_code == 255)

    def test_wrong_type(self):

        """Delete wrong type"""

        rtn = self.run_cmd("pm delete --name ye --type WRONG")
        assert(rtn.return_code == 254)
 
    def test_delete_binary(self):

        """Delete a binary"""

        data_file = testutils.DataFile("integration_pm_valid_zip.zip")

        rtn = self.run_cmd("pm install --zip %s" % str(data_file))
        assert(rtn.return_code == 0)

        rtn = self.run_cmd("pm delete --name GenerateAIDL-1.0.jar --type binary",
                            input_data="y\n")
        assert(rtn.return_code == 0)
 
    def test_delete_library(self):

        """Delete a library"""

        data_file = testutils.DataFile("integration_pm_valid_zip.zip")

        rtn = self.run_cmd("pm install --zip %s" % str(data_file))
        assert(rtn.return_code == 0)

        rtn = self.run_cmd("pm delete --name Utils --type library",
                            input_data="y\n")
        assert(rtn.return_code == 0)
 
    def test_delete_module(self):

        """Delete a module"""

        data_file = testutils.DataFile("integration_pm_valid_zip.zip")

        rtn = self.run_cmd("pm install --zip %s" % str(data_file))
        assert(rtn.return_code == 0)

        rtn = self.run_cmd("pm delete --name apkget --type module",
                            input_data="y\n")

        assert(rtn.return_code == 0)
 
    def test_delete_package(self):

        """Delete a package"""

        data_file = testutils.DataFile("integration_pm_valid_zip.zip")

        rtn = self.run_cmd("pm install --zip %s" % str(data_file))
        assert(rtn.return_code == 0)

        rtn = self.run_cmd("pm delete --name HelloWorld_app --type package",
                            input_data="y\n")
        assert(rtn.return_code == 0)
