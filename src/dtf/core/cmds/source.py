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
"""Built-in module for obtaining the path for sourcing"""

from dtf.module import Module
from dtf.globals import DTF_INCLUDED_DIR

class source(Module):

    """Module class for source dtf stuff"""

    def execute(self, args):

        """Main module executor"""

        print DTF_INCLUDED_DIR + "/dtf_core.sh"

        return 0
