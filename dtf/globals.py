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
"""Global dtf locations"""

import dtf.core.utils as utils

DTF_DATA_DIR = utils.get_dtf_data_dir()
DTF_BINARIES_DIR = DTF_DATA_DIR + "/binaries/"
DTF_LIBRARIES_DIR = DTF_DATA_DIR + "/libraries/"
DTF_MODULES_DIR = DTF_DATA_DIR + "/modules/"
DTF_PACKAGES_DIR = DTF_DATA_DIR + "/packages/"
DTF_DB = DTF_DATA_DIR + "/main.db"

DTF_INCLUDED_DIR = utils.get_pydtf_dir() + "/included"
