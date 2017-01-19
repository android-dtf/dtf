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

from __future__ import absolute_import
import dtf.testutils as testutils
import dtf.core.utils as utils

import os.path

class ArchiveTests(testutils.BasicIntegrationTest):

    """Wraper for integration tests"""

    def test_no_args(self):

        """Run with not args"""

        rtn = self.run_cmd("archive")

        assert(rtn.return_code == 0)


    def test_not_subcommand(self):

        """Try to call invalid sub command"""

        rtn = self.run_cmd("archive NOT_EXIST")

        assert(rtn.return_code == 0)

    def test_help(self):

        """Force the usage"""

        rtn = self.run_cmd("archive -h")

        assert(rtn.return_code == 0)

    def test_no_name(self):

        """Attempt create an archive using builtin name"""

        config = testutils.get_default_config()

        version_string = "android-17_XTS"
        zip_name = "%s.zip" % version_string
        config.set("Info", "version-string", version_string)

        self.update_config(config)

        rtn = self.run_cmd("archive create")

        assert(rtn.return_code == 0)
        assert(os.path.isfile(zip_name))

        utils.delete_file(zip_name)

    def test_named(self):

        """Attempt to create an archive using custom name"""

        version_string = "android-17_XTS"
        zip_name = "%s.zip" % version_string

        rtn = self.run_cmd("archive create %s" % zip_name)

        assert(rtn.return_code == 0)
        assert(os.path.isfile(zip_name))

        utils.delete_file(zip_name)
