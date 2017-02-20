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
"""Integration tests for launching modules"""

from __future__ import absolute_import
import dtf.testutils as testutils

class ModuleInstallTests(testutils.BasicIntegrationTest):

    """Wraper for integration tests"""

    def test_valid_python_execute(self):

        """Run module with default execute"""

        data_file = testutils.DataFile("integration_module_valid_mod")

        rtn = self.run_cmd("pm install --force --single module --install_name test_execute --name %s --auto" % str(data_file))
        assert(rtn.return_code == 0)

        rtn = self.run_cmd("test_execute")

        assert(rtn.return_code == 0)

    def test_valid_python_sub_cmd(self):

        """Run module with valid sub_cmd"""
 
        data_file = testutils.DataFile("integration_module_valid_subs")

        rtn = self.run_cmd("pm install --force --single module --install_name test_sub --name %s --auto" % str(data_file))
        assert(rtn.return_code == 0)

        rtn = self.run_cmd("test_sub test")

        assert(rtn.return_code == 0)

    def test_valid_python_wrong_sub(self):

        """Run module with not existant subcmd"""
 
        data_file = testutils.DataFile("integration_module_valid_subs")

        rtn = self.run_cmd("pm install --force --single module --install_name test_sub --name %s --auto" % str(data_file))
        assert(rtn.return_code == 0)

        rtn = self.run_cmd("test_sub nope")

        assert(rtn.return_code == 241)

    def test_valid_python_raise_exception(self):

        """Run module and immediately raise an exception"""
 
        data_file = testutils.DataFile("integration_module_valid_raise")

        rtn = self.run_cmd("pm install --force --single module --install_name test_raise --name %s --auto" % str(data_file))
        assert(rtn.return_code == 0)

        rtn = self.run_cmd("test_raise test")

        assert(rtn.return_code == 246)

    def test_valid_python_raise_kb_exception(self):

        """Run module and immediately raise a keyboard exception"""
 
        data_file = testutils.DataFile("integration_module_valid_kraise")

        rtn = self.run_cmd("pm install --force --single module --install_name test_kraise --name %s --auto" % str(data_file))
        assert(rtn.return_code == 0)

        rtn = self.run_cmd("test_kraise test")

        assert(rtn.return_code == 245)

    # TODO: this cant be ran until --install_name is parsed correctly.
    #def test_invalid_python_missing_class(self):
    #
    #    """Attempt to run module with missing class"""
    #
    #    data_file = testutils.DataFile("integration_module_invalid_noclass")
    #
    #    rtn = self.run_cmd("pm install --force --single module --install_name test_noclass --name %s" % str(data_file))
    #    assert(rtn.return_code == 0)
    #
    #    rtn = self.run_cmd("test_noclass test")
    #
    #    assert(rtn.return_code == 247)

    def test_invalid_python_no_exec_zero_args(self):

        """Attempt to run module with no args or exec"""

        data_file = testutils.DataFile("integration_module_invalid_noexecargs")

        rtn = self.run_cmd("pm install --force --single module --install_name test_noexecargs --name %s --auto" % str(data_file))
        assert(rtn.return_code == 0)

        rtn = self.run_cmd("test_noexecargs test")

        assert(rtn.return_code == 242)
