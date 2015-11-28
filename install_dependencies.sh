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

# Are you root?
if [ "$(id -u)" != "0" ]; then
   echo "[ERROR] Please run this script as root! Exiting." 1>&2
   exit 1
fi

echo "### dtf Dependency Installation Script ###"
echo ""
echo "This script will attempt to configure your environment to work with"
echo "dtf and the 'dtfmods-core' packages."
echo ""
echo "Offically supported OSes are:"
echo "  - Ubuntu 14.04 LTS (64-bit)"
echo "  - Ubuntu 15.04 (64-bit)"
echo ""
echo -n "Press enter to continue. "

read REPLY

# Determine if we are Ubuntu 14/15. For other operating system, do not 
# continue.  For older (or newer) versions of Ubuntu, display 
# warning but try anyways.
ver=$(lsb_release -d|awk -F"\t" '{print $2}')

# Ubuntu 
os_ver=$(echo $ver | awk  '{ string=substr($0, 1, 6); print string; }' )
if [ "$os_ver" = "Ubuntu" ]; then

    ubuntu_ver=$(echo $ver | awk  '{ string=substr($0, 1, 10); print string; }' )

    # Is it the supported one?
    if [ "$ubuntu_ver" = "Ubuntu 14." -o "$ubuntu_ver" = "Ubuntu 15." ]; then
        echo "[+] Supported Ubuntu detected."
    else
        echo "[WARNING] It looks like you're using Ubuntu, but not the offically supported version."
        echo -n "Do you want to try the setup anyways? [y/N] "

        read response

        case $response in
            [yY][eE][sS]|[yY])
                ;;
            *)
                echo "Exiting."
                exit 0
                ;;
        esac
    fi
# Something else. Bail.
else
    echo "[ERROR] You're not using Ubuntu. You'll need to install dependencies manually. Sorry!"
    exit 2
fi

# Make sure everything is up to date.
echo "[+] Updating repos..."
dpkg --add-architecture i386 || exit 5
apt-get -qqy update || exit 6

# General stuff
echo "[+] Installing general purpose tools..."
apt-get -qqy install gdebi-core xz-utils sqlite3 build-essential || exit 3

# Android stuff
if [ `which adb` ]; then
    echo "[+] Skipping adb install..."
else
    echo "[+] Installing required Android tools..."
    apt-get -qqy install android-tools-adb || exit 4
fi

apt-get -qqy install libncurses5:i386 libstdc++6:i386 zlib1g:i386 || exit 7

echo "[+] Checking for valid python (2.6+)..."
py_ver=$(python --version  2>&1|head -n1)
py_sub_ver=$(echo $py_ver | awk  '{ string=substr($0, 1, 10); print string; }' )

if [ "$py_sub_ver" = "Python 2.6" -o "$py_sub_ver" = "Python 2.7" ]; then
    echo "[+] Python installation detected."
else
    echo "[+] Python not detected, installing 2.7..."
    apt-get -qqy install python2.7 || exit 8
fi

echo "[+] Getting Python pip..."
apt-get -qqy install python-pip || exit 9

echo "[+] Getting pip modules..."
pip install colored --upgrade || exit 10

echo "[+] Checking for Java (openjdk) 1.7..."
apt-get -qqy install openjdk-7-jdk || exit 11

echo "[+] Checking for Drozer..."

if [ `which drozer` ]; then
    echo "[+] Drozer already installed!"
else
    echo "[+] Getting drozer .deb and installing..."
    wget -O drozer.deb https://www.mwrinfosecurity.com/system/assets/931/original/drozer_2.3.4.deb
    gdebi --option=APT::Get::force-yes=1,APT::Get::Assume-Yes=1 -n -q drozer.deb
    rm drozer.deb 2>/dev/null
fi

echo "[+] Confirming true bash shell.."

shell=$(readlink -f $(which sh)|grep -o '....$')
if [ "$shell" = "bash" ]; then
    echo "[+] Bash detected."
else
    echo -n "Your shell is not currently bash. At the prompt, select '<NO>' to use bash. (press enter key). "
    read _
    dpkg-reconfigure dash
fi
echo "[+] Dependency installation complete. Have fun!"
