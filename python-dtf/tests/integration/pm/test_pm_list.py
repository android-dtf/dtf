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

class PmListTests(testutils.BasicIntegrationTest):

    """Wraper for integration tests"""

    def test_no_args(self):

        """Running list with no args"""

        rtn = self.run_cmd("pm list")
        assert(rtn.return_code == 0)

        rtn = self.run_cmd("pm list -v")
        assert(rtn.return_code == 0)


    def test_quiet_verbose(self):

        """Try and fail to print verbose + quiet"""

        rtn = self.run_cmd("pm list -vq")
        assert(rtn.return_code == 255)


    def test_all_valid(self):

        """Print all types, with actual installed content"""

        data_file = testutils.DataFile("integration_pm_valid_zip.zip")

        rtn = self.run_cmd("pm install --zip %s" % str(data_file))
        assert(rtn.return_code == 0)

        rtn = self.run_cmd("pm list")
        assert(rtn.return_code == 0)

        rtn = self.run_cmd("pm list -v")
        assert(rtn.return_code == 0)

        rtn = self.run_cmd("pm list -q")
        assert(rtn.return_code == 0)


    def test_binaries(self):

        """List only binaries"""

        rtn = self.run_cmd("pm list binaries")
        assert(rtn.return_code == 0)

        rtn = self.run_cmd("pm list binaries -v")
        assert(rtn.return_code == 0)

        rtn = self.run_cmd("pm list binaries -q")
        assert(rtn.return_code == 0)


    def test_libraries(self):

        """List only libraries"""

        rtn = self.run_cmd("pm list libraries")
        assert(rtn.return_code == 0)

        rtn = self.run_cmd("pm list libraries -v")
        assert(rtn.return_code == 0)

        rtn = self.run_cmd("pm list libraries -q")
        assert(rtn.return_code == 0)


    def test_modules(self):

        """List only modules"""

        rtn = self.run_cmd("pm list modules")
        assert(rtn.return_code == 0)

        rtn = self.run_cmd("pm list modules -v")
        assert(rtn.return_code == 0)

        rtn = self.run_cmd("pm list modules -q")
        assert(rtn.return_code == 0)


    def test_packages(self):

        """List only packages"""

        rtn = self.run_cmd("pm list packages")
        assert(rtn.return_code == 0)

        rtn = self.run_cmd("pm list packages -v")
        assert(rtn.return_code == 0)

        rtn = self.run_cmd("pm list packages -q")
        assert(rtn.return_code == 0)

    def test_list_invalid(self):

        """List a invalid type"""

        rtn = self.run_cmd("pm list BAD")
        assert(rtn.return_code == 253)
