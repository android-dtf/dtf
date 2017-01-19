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
"""Integration tests for the "pm purge" utility"""

from __future__ import absolute_import
import dtf.testutils as testutils

class PmPurgeTests(testutils.BasicIntegrationTest):

    """Wraper for integration tests"""

    def test_purge_cancel(self):

        """Run purge but cancel"""

        rtn = self.run_cmd("pm purge", input_data="n\n")
        assert(rtn.return_code == 0)

    def test_purge_go(self):

        """Run purge"""

        rtn = self.run_cmd("pm purge", input_data="y\n")
        assert(rtn.return_code == 0)
