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
"""dtf Libraries Template"""

from __future__ import absolute_import

import os.path
import sqlite3

import dtf.core.utils as utils
import dtf.properties as prop

TAG = "dtf-library"
AOSP_PACKAGE_PREFIX = "aosp-data-"


class DtfDbException(Exception):  # pylint: disable=too-few-public-methods

    """Base class for DB Exceptions"""

    def __init__(self, message):

        """Raise new exception"""

        # Call the base class constructor with the parameters it needs
        Exception.__init__(self, message)


class DbLibrary(object):

    """
    Base class for creating a python database library with dtf.
    """

    # This needs to be set
    db_name = ""

    db_path = ""
    db_connection = None

    def __init__(self, safe=False, project_dir=None):

        """Initialize new instance"""

        if project_dir is None:
            db_path = "%s/%s/%s" % (prop.TOP, utils.DBS_DIRECTORY,
                                    self.db_name)
        else:
            db_path = "%s/%s/%s" % (project_dir, utils.DBS_DIRECTORY,
                                    self.db_name)

        if safe and not os.path.isfile(db_path):
            raise DtfDbException("Database file not found : %s!" % db_path)

        self.db_path = db_path
        self.db_connection = sqlite3.connect(db_path)

        # Call post init for anyone needing additional stuff here
        self.post_init()

    def post_init(self):

        """Post-init to allow additional processing after __init__"""
        pass

    # The following are not meant to be overridden.
    def commit(self):

        """Commit DB changes"""

        if self.db_connection is None:
            raise DtfDbException("No active DB connection!")

        return self.db_connection.commit()

    def get_cursor(self):

        """Obtain handle to cursor"""

        if self.db_connection is None:
            raise DtfDbException("No active DB connection!")

        return self.db_connection.cursor()

    def close(self):

        """Close handle to DB"""

        if self.db_connection is None:
            raise DtfDbException("No Active DB connection!")

        self.db_connection.close()

        return

    @classmethod
    def exists(cls):

        """Simple check to determine if DB exists"""

        db_path = "%s/%s/%s" % (prop.TOP, utils.DBS_DIRECTORY,
                                cls.db_name)

        return bool(os.path.isfile(db_path))
