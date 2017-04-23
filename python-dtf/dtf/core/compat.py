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
"""Compatibility helpers"""

# pylint: disable=invalid-name,input-builtin,raw_input-builtin
# pylint: disable=wrong-import-position

from __future__ import absolute_import

try:
    raw_input = raw_input  # pylint: disable=redefined-builtin
except NameError:
    raw_input = input

try:
    from io import StringIO
except ImportError:
    from cStringIO import StringIO

StringIO = StringIO

try:
    import urlparse
except ImportError:
    # pylint: disable=no-name-in-module,import-error
    import urllib.parse as urlparse

urlparse = urlparse
