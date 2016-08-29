#!/bin/sh
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

# Uninstaller script to remove dtf 1.3.0
# Usage: sudo ./uninstall_1_3.sh

# Delete the bash completion
echo "Removing bash completion..."
rm /etc/bash_completion.d/dtf_bash_completion.sh


echo "Removing launcher..."
# Delete the launcher
rm /usr/local/bin/dtf


echo "Removing Python library..."
# Delete the library
sudo pip uninstall dtf
rm -rf /usr/local/lib/python2.7/dist-packages/dtf

echo "Uninstall complete!"
