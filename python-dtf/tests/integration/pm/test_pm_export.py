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
"""Integration tests for the "pm export" utility"""

from __future__ import absolute_import
import os.path

import dtf.testutils as testutils
import dtf.core.utils as utils


class PmExportTests(testutils.BasicIntegrationTest):

    """Wraper for integration tests"""

    def test_no_content(self):

        """Attempt to export nothing"""

        rtn = self.run_cmd("pm export test.zip")
        assert(rtn.return_code == 254)

    def test_existing_file(self):

        """Attempt to export to exisitng file"""

        utils.touch("test.zip")

        rtn = self.run_cmd("pm export test.zip")

        utils.delete_file("test.zip")
        
        assert(rtn.return_code == 255)

    def test_real_export(self):

        """Perform an export"""

        data_file = testutils.DataFile("integration_pm_valid_zip.zip")

        rtn = self.run_cmd("pm install --zip %s" % str(data_file))
        assert(rtn.return_code == 0)

        rtn = self.run_cmd("pm export test.zip")
        assert(rtn.return_code == 0)
        assert(os.path.isfile("test.zip"))

        utils.delete_file("test.zip")
