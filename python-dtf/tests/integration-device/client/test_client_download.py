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
"""Integration tests for the "client download" utility"""

from __future__ import absolute_import
import dtf.testutils as testutils
import dtf.core.utils as utils

class ClientDownloadTests(testutils.BasicIntegrationDeviceTest):

    """Wraper for integration tests"""

    def test_download(self):

        """Do an download"""

        rtn = self.run_cmd("client download /system/etc/hosts")

        utils.delete_file("hosts")

        assert(rtn.return_code == 0)

    def test_download_local_exists(self):

        """Try to download a file that already exists"""

        utils.touch("hosts")
        rtn = self.run_cmd("client download /system/etc/hosts")

        utils.delete_file("hosts")

        assert(rtn.return_code == 255)

    def test_download_path(self):

        """Do a download to a path"""

        rtn = self.run_cmd("client download --path ./hosts /system/etc/hosts")

        utils.delete_file("hosts")

        assert(rtn.return_code == 0)

    def test_download_not_installed(self):

        """Attempt to download with non-existent APK"""

        rtn = self.run_cmd("client remove")
        assert(rtn.return_code == 0)

        rtn = self.run_cmd("client download /system/etc/hosts")
        assert(rtn.return_code == 255)

        rtn = self.run_cmd("client install")
        assert(rtn.return_code == 0)
