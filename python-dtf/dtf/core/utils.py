# Android Device Testing Framework ("dtf")
# Copyright 2013-2015 Jake Valletta (@jake_valletta)
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
""" dtf Utilities """

from hashlib import md5
from urlparse import urlparse
import errno
import os
import os.path
import shutil
import stat

CONFIG_FILE_NAME = '.dtfini'
LOG_FILE_NAME = '.dtflog'

REPORTS_DIRECTORY = 'reports'
DBS_DIRECTORY = '.dbs'
LOCAL_MODULES_DIRECTORY = 'local_modules'


def __upsearch(file_name, dir_name):

    """Recursively find a file, searching up."""

    if os.path.isfile("%s/%s" % (dir_name, file_name)):
        return dir_name
    else:
        new_dir = os.path.abspath(os.path.join(dir_name, os.pardir))
        if dir_name == new_dir:
            return None
        return __upsearch(file_name, new_dir)


def get_project_root():

    """Search for and return the dtf project root."""

    return __upsearch(CONFIG_FILE_NAME, os.getcwd())


def get_pydtf_dir():

    """Return the location of the dtf dist-packages directory."""

    return os.path.dirname(os.path.split(os.path.abspath(__file__))[0])


def get_dtf_data_dir():

    """Return the location of the dtf data directory."""

    return os.path.expanduser('~') + '/.dtf'


def md5_local(file_path):

    """MD5 a local file"""

    file_f = open(file_path, 'rb')

    local_m = md5()
    while True:
        data = file_f.read(128)
        if not data:
            break
        local_m.update(data)

    return local_m.hexdigest()


def is_exe(fpath):

    """ Check if file is an executable"""

    # stackoverflow.com/questions/377017/test-if-executable-exists-in-python
    return os.path.isfile(fpath) and os.access(fpath, os.X_OK)


def which(program):

    """Test if program is pathed."""

    # stackoverflow.com/questions/377017/test-if-executable-exists-in-python

    fpath = os.path.split(program)[0]

    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            path = path.strip('"')
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None


def is_executable(file_name):

    """Check if a file can be executed"""

    return bool(stat.S_IXUSR & os.stat(file_name)[stat.ST_MODE])


def mkdir_recursive(path):

    """Recursively create a directory"""

    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


# http://stackoverflow.com/questions/1158076/implement-touch-using-python
def touch(file_name, times=None):

    """Touch a file"""

    with open(file_name, 'a'):
        os.utime(file_name, times)


def delete_file(file_name):

    """Delete a file (show errors optional)"""

    try:
        os.remove(file_name)
    except OSError:
        pass

    return 0


def delete_tree(directory_name):

    """Delete a directory recursively"""

    try:
        shutil.rmtree(directory_name)
    except OSError:
        pass

    return 0


def file_in_zip(zip_f, file_name):

    """Determine if a file exists in a ZIP"""

    try:
        zip_f.read(file_name)
        return True
    except KeyError:
        return False


def directory_in_zip(zip_f, directory_name):

    """Determine if a directory exists in a ZIP"""

    return any(x.startswith("%s/" % directory_name.rstrip("/"))
               for x in zip_f.namelist())


def is_valid_url(url_string):

    """Test and return valid URL"""

    parsed_url = urlparse(url_string)

    return bool(parsed_url.scheme)
