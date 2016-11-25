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
"""Integration tests for the "pm install" utility"""

import dtf.testutils as testutils

class PmInstallTests(testutils.BasicIntegrationTest):

    """Wraper for integration tests"""

    def test_no_args(self):

        """Running list with no args"""

        rtn = self.run_cmd("pm install")
        assert(rtn.return_code == 254)


    def test_zip_and_single(self):

        """Try to install zip and single"""

        rtn = self.run_cmd("pm install --single abc --zip abc")
        assert(rtn.return_code == 255)


    def test_install_non_existing_zip(self):

        """Try to install a ZIP that doesn't exist"""

        rtn = self.run_cmd("pm install --zip NOTHING.zip")
        assert(rtn.return_code == 253)

    def test_install_new_zip(self):

        """Install a ZIP"""

        data_file = testutils.DataFile("integration_pm_valid_zip.zip")

        rtn = self.run_cmd("pm install --zip %s" % str(data_file))
        assert(rtn.return_code == 0)

    def test_install_no_name(self):

        """Attempt to install module without name"""

        rtn = self.run_cmd("pm install --single module")
        assert(rtn.return_code == 251)

    def test_install_bad_typename(self):

        """Attempt to install bad type"""

        rtn = self.run_cmd("pm install --single TEST --name TEST")
        assert(rtn.return_code == 251)

    def test_install_bad_health(self):

        """Attempt to install bad health"""

        data_file = testutils.DataFile("integration_pm_module_install_bash")

        rtn = self.run_cmd("pm install --health BAD --single module --name %s" % str(data_file))
        assert(rtn.return_code == 251)

    def test_install_manual_version(self):

        """Install module with manual version"""

        data_file = testutils.DataFile("integration_pm_module_install_bash")

        rtn = self.run_cmd("pm install --version 1.0 --single module --name %s" % str(data_file))
        assert(rtn.return_code == 0)

    def test_install_manual_version(self):

        """Attempt to install module with bad version"""

        data_file = testutils.DataFile("integration_pm_module_install_bash")

        rtn = self.run_cmd("pm install --version BAD --single module --name %s" % str(data_file))
        assert(rtn.return_code == 251)

    def test_install_single_binary(self):

        """Install a single binary"""

        data_file = testutils.DataFile("integration_pm_binary_install")

        rtn = self.run_cmd("pm install --single binary --name %s" % str(data_file))
        assert(rtn.return_code == 0)

    def test_install_single_binary_auto(self):

        """Attempt to install binary, but try auto"""

        data_file = testutils.DataFile("integration_pm_binary_install")

        rtn = self.run_cmd("pm install --auto --single binary --name %s" % str(data_file))
        assert(rtn.return_code == 252)

    def test_install_single_binary_non_exist(self):

        """Attempt to install a binary that doesn't exist"""

        rtn = self.run_cmd("pm install --single binary --name Bad")
        assert(rtn.return_code == 251)

    def test_install_single_library(self):

        """Install a single library"""

        data_zip = testutils.DataZip("integration_pm_install_library.dz")

        rtn = self.run_cmd("pm install --single library --name %s" % str(data_zip))

        data_zip.close()

        assert(rtn.return_code == 0)

    def test_install_single_library_non_exist(self):

        """Attempt to install a library that doesn't exist"""

        rtn = self.run_cmd("pm install --single library --name Bad")
        assert(rtn.return_code == 251)

    def test_install_single_module_bash_auto(self):

        """Install a single module"""

        data_file = testutils.DataFile("integration_pm_module_install_bash")

        rtn = self.run_cmd("pm install --auto --single module --name %s" % str(data_file))
        assert(rtn.return_code == 0)

    def test_install_single_module_bash(self):

        """Install a single module"""

        data_file = testutils.DataFile("integration_pm_module_install_bash")

        rtn = self.run_cmd("pm install --single module --name %s" % str(data_file))
        assert(rtn.return_code == 0)

    def test_install_single_module_non_exist(self):

        """Attempt to install a module that doesn't exist"""

        rtn = self.run_cmd("pm install --single module --name Bad")
        assert(rtn.return_code == 251)

    def test_install_single_package(self):

        """Install a single package"""

        data_zip = testutils.DataZip("integration_pm_install_package.dz")

        rtn = self.run_cmd("pm install --single package --name %s" % str(data_zip))

        data_zip.close()

        assert(rtn.return_code == 0)


    def test_install_single_package_non_exist(self):

        """Attempt to install a package that doesn't exist"""

        rtn = self.run_cmd("pm install --single package --name Bad")
        assert(rtn.return_code == 251)
