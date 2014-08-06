#!/usr/bin/env python
# Android Device Testing Framework ("dtf")
# Copyright 2013-2014 Jake Valletta (@jake_valletta)
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
# Python global values.

import os
from re import sub

__root_dir = sub( "/pydtf/dtfglobals.py(c)?$", "", os.path.realpath(__file__))

DTF_DIR = __root_dir
DTF_BINS = __root_dir+"/bin"
DTF_CORE = __root_dir+"/dtf-core"
DTF_INCLUDED = __root_dir+"/included"
DTF_LIBS = __root_dir+"/lib"
DTF_MODULES = __root_dir+"/modules"
DTF_PACKAGES = __root_dir+"/packages"
