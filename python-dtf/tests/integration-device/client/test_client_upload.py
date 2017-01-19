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
"""Integration tests for the "client upload" utility"""

from __future__ import absolute_import
import dtf.testutils as testutils


PATH_TO_DTF_DATA = '/data/data/com.dtf.client'

class ClientUploadTests(testutils.BasicIntegrationDeviceTest):

    """Wraper for integration tests"""

    def test_upload(self):

        """Do an upload"""

        data_file = testutils.DataFile("integration_client_upload_data")

        rtn = self.run_cmd("client upload %s" % str(data_file))
        assert(rtn.return_code == 0)

        rtn = self.run_cmd("client execute \"rm %s/integration_client_upload_data\""
                           % PATH_TO_DTF_DATA)
        assert(rtn.return_code == 0)
 

    def test_upload_no_exist(self):

        """Upload non-existent file"""

        rtn = self.run_cmd("client upload TEST")
        assert(rtn.return_code == 255)

    def test_upload_path(self):

        """Do an upload to a path"""

        data_file = testutils.DataFile("integration_client_upload_data")

        rtn = self.run_cmd("client upload --path /data/data/com.dtf.client/test %s"
                           % str(data_file))
        assert(rtn.return_code == 0)

        rtn = self.run_cmd("client execute \"rm %s/integration_client_upload_data\""
                           % PATH_TO_DTF_DATA)
        assert(rtn.return_code == 0)

    def test_upload_not_installed(self):

        """Attempt to upload with non-existent APK"""

        rtn = self.run_cmd("client remove")
        assert(rtn.return_code == 0)

        data_file = testutils.DataFile("integration_client_upload_data")

        rtn = self.run_cmd("client upload %s" % str(data_file))
        assert(rtn.return_code == 255)

        rtn = self.run_cmd("client install")
        assert(rtn.return_code == 0)
