#!/usr/bin/env bash
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

# This this is a wraper script for "drozer".

dtf_drozer()
{

    # Source to get project dir.
    . `dtf source`
    cd "$TOP"

    serial=$(dtf prop get Info serial)

    # Make sure we can get to our device.
    echo "Waiting for device..."
    adb -s ${serial} wait-for-device

    # Set up the port forward rules
    adb -s ${serial} forward tcp:31415 tcp:31415

    drozer console connect

    return 0
}
