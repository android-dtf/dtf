#!/bin/sh
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

# Modules that want to take advantage of built-in functionality should source this file.

# This allows modules to access dtf resources
DTF_DIR=~/.dtf
DTF_BINS=${DTF_DIR}/binaries
DTF_LIBS=${DTF_DIR}/libraries
DTF_MODULES=${DTF_DIR}/modules
DTF_PACKAGES=${DTF_DIR}/packages
DTF_INCLUDED=${DTF_DIR}/included

export DTF_BINS DTF_LIBS DTF_MODULES DTF_PACKAGES DTF_INCLUDED

# API Levels for quick references.
export API_1=1
export API_2=2
export API_CUPCAKE=3
export API_DONUT=4
export API_ECLAIR=5
export API_ECLAIR_R1=6
export API_ECLAIR_R2=7
export API_FROYO=8
export API_GINGERBREAD=9
export API_GINGERBREAD_R1=10
export API_HONEYCOMB=11
export API_HONEYCOMB_R1=12
export API_HONEYCOMB_R2=13
export API_ICE_CREAM_SANDWICH=14
export API_ICE_CREAM_SANDWICH_R1=15
export API_JELLY_BEAN=16
export API_JELLY_BEAN_R1=17
export API_JELLY_BEAN_R2=18
export API_KITKAT=19
export API_WEAR=20
export API_LOLLIPOP=21
export API_LOLLIPOP_R1=22
export API_MARSHMALLOW=23
export API_NOUGAT=24

# In the case of $TOP not being set, you can use this to obtain the project
# path. Chances are that you won't ever need to call this.
getroot () {

    if [ -f .dtfini ]; then echo "$PWD" && return; fi

    test / = "$PWD" && return || test -e "$1" && echo "$PWD" && return || cd .. && upsearch ".dtfini"
}

# Helper for obtaining project root. Not meant to be called (unless you wanted
# to?)
upsearch () {
    test / = "$PWD" && return || test -e "$1" && echo "$PWD" && return || cd .. && upsearch "$1"
}

# Top of the project.
export TOP
TOP=$(upsearch .dtfini)

# Change back to the launch directory
dtf_reset_dir() {

    cd "$LAUNCH_DIR" || exit 1
}

# Method to check if device is connected.
# returns 1 if connected, 0 if not connected. 
dtf_device_connected ()
{
    state=$(adb get-state)

    if [ "$state" = "device" ]; then
        return 0
    fi

    return 1
}

# Check if a module is installed.
dtf_has_module ()
{
    module_name=$1

    if dtf pm list modules -q |grep "\b${module_name}$" > /dev/null; then
        return 0
    else
        return 1
    fi
}

# Check if a binary is installed.
dtf_has_binary ()
{
    binary_name=$1

    if dtf pm list binaries -q |grep "\b${binary_name}$" > /dev/null; then
        return 0
    else
        return 1
    fi
}

# Check if a library is installed.
dtf_has_library ()
{
    library_name=$1

    if dtf pm list libraries -q |grep "\b${library_name}$" > /dev/null; then
        return 0
    else
        return 1
    fi
}

# Check if a package is installed.
dtf_has_package ()
{
    package_name=$1

    if dtf pm list packages -q |grep "\b${package_name}$" > /dev/null; then
        return 0
    else
        return 1
    fi
}
