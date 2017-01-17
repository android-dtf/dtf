# Android Device Testing Framework ("dtf")
# Copyright 2013-2017 Jake Valletta (@jake_valletta)
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
"""Integration tests for the "pm repo" utility"""

import dtf.testutils as testutils

class PmRepoTests(testutils.BasicIntegrationTest):

    """Wraper for integration tests"""

    def test_no_args(self):

        """Running repo with no args"""

        rtn = self.run_cmd("pm repo")
        assert(rtn.return_code == 0)

    def test_invalid_cmd(self):

        """Run repo with invalid cmd"""

        rtn = self.run_cmd("pm repo NOTHING")
        assert(rtn.return_code == 255)

    def test_repo_add_valid(self):

        """Try to readd a repo with same name"""

        rtn = self.run_cmd("pm repo add core-mods https://somethingsilly.com")
        assert(rtn.return_code == 0)


    def test_repo_add_wrong_args(self):

        """Run add with incorrect args"""

        rtn = self.run_cmd("pm repo add")
        assert(rtn.return_code == 255)

    def test_repo_add_invalid_url(self):

        """Try to add invalid repo URL"""

        rtn = self.run_cmd("pm repo add core-mods somethingsilly.com")
        assert(rtn.return_code == 254)

    def test_repo_add_already_exists(self):

        """Try to re-add a repo with same name"""

        rtn = self.run_cmd("pm repo add core-mods https://somethingsilly.com")
        assert(rtn.return_code == 0)

        rtn = self.run_cmd("pm repo add core-mods https://somethingsilly.com")
        assert(rtn.return_code == 253)

    def test_repo_remove_valid(self):

        """Add then remove a repo"""

        rtn = self.run_cmd("pm repo add core-mods https://somethingsilly.com")
        assert(rtn.return_code == 0)

        rtn = self.run_cmd("pm repo remove core-mods")
        assert(rtn.return_code == 0)

    def test_repo_remove_wrong_args(self):

        """Run remove with incorrect args"""

        rtn = self.run_cmd("pm repo remove")
        assert(rtn.return_code == 255)

    def test_repo_remove_nonexist(self):

        """Attempt to remove not exist repo"""

        rtn = self.run_cmd("pm repo remove silly")
        assert(rtn.return_code == 253)

    def test_repo_list_empty(self):

        """List no repos"""

        rtn = self.run_cmd("pm repo list")
        assert(rtn.return_code == 0)

    def test_repo_list_valid(self):

        """List no repos"""

        rtn = self.run_cmd("pm repo add mods-core https://silly.com")
        assert(rtn.return_code == 0)

        rtn = self.run_cmd("pm repo list")
        assert(rtn.return_code == 0)
