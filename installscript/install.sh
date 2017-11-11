#!/usr/bin/env bash
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

# dtf installer

BRANCH=master
CLEAN=0
DEBUG=0
NO_COLOR=0
PROMPT=1

DEB_NAME=android-dtf_all.deb

# trap ctrl-c and call ctrl_c()
trap ctrl_c INT

ctrl_c() {
    printf "%b" "\nCtrl+C received!\n"
    exit 1
}

usage() {
    printf "%b" "
dtf Installer Usage

  install.sh [options]

Options

  --auto             Disable prompts during install.
  --branch [branch]  Download from a specific branch.
  --clean            Purge all old data.
  --debug            Enable additional debugging.
"
}

parse_arguments() {

    while
        (( $# > 0 ))
    do
        token="$1"
        shift
        case "$token" in

            (--debug)
                DEBUG=1
                ;;

            (--auto)
                PROMPT=0
                ;;

            (--clean)
                CLEAN=1
                ;;

            (--branch)
                if [[ -n "${1:-}" ]]; then
                    BRANCH="$1"
                    shift
                else
                    error "--branch must be followed by a branchname."
                    exit 1
                fi
                ;;

            (--help|--usage)
                usage
                exit 0
                ;;
            (*)
                usage
                exit 1
                ;;
        esac
    done
}

info() {

    if [ "$NO_COLOR" = "1" ]; then
        echo "[+] $1"
    else
        printf "[%s+%s] %s\n" "${COLOR_INFO}" "${COLOR_RST}" "$1"
    fi
}

debug() {

    if [ "$DEBUG" = "0" ]; then
        return 0
    fi

    if [ "$NO_COLOR" = "1" ]; then
        echo "[D] $1"
    else
        printf "[%sD%s] %s\n" "${COLOR_DEB}" "${COLOR_RST}" "$1"
    fi
}

error() {

    if [ "$NO_COLOR" = "1" ]; then
        echo "[-] $1"
    else
        printf "[%s-%s] %s\n" "${COLOR_ERROR}" "${COLOR_RST}" "$1"
    fi
}

prompt() {

    if [ "$NO_COLOR" = "1" ]; then
        echo -n "[!] $1"
    else
        printf "[%s!%s] %s " "${COLOR_WARNING}" "${COLOR_RST}" "$1"
    fi

    if [ "$PROMPT" = "0" ]; then
        echo ""
    else
        read response
    fi
}

warning() {

    if [ "$NO_COLOR" = "1" ]; then
        echo "[!] $1"
    else
        printf "[%s!%s] %s\n" "${COLOR_WARNING}" "${COLOR_RST}" "$1"
    fi
}

has_dpkg() {

    dpkg -s "$1" &>/dev/null || return 1
    return 0
}

has_cmd() {

    hash "$1" 2>/dev/null || return 1
    return 0
}

do_colors() {

    COLOR_ERROR=$(tput setaf 1)
    COLOR_WARNING=$(tput setaf 3)
    COLOR_INFO=$(tput setaf 2)
    COLOR_DEB=$(tput setaf 5)
    COLOR_RST=$(tput sgr0)
}

do_install() {

    info "======================================================"
    info "Welcome to the dtf Installer!"
    info ""
    info "This utility will download dependencies and install dtf"
    info "on your system. This installer will require user input"
    info "and, at times, sudo privileges, and an Internet connection"
    info "Please be ready to answer the prompts and enter your credentials."
    info ""
    info "Note: if you have any security concerns, this script is"
    info "available from the dtf github project at:"
    info "   -https://github.com/android-dtf/dtf/installscript/install.sh"
    info ""
    prompt "Please press ENTER to continue or ctrl+C to abort."

    info "Checking for required (manual) dependencies..."

    debug "Checking for adb"
    if ! has_cmd adb; then
        error "\`adb\` (Android SDK) is required! You should configure this as instructed."
        exit 2
    fi
 
    info "Updating apt-get repos..."
    sudo apt-get update -qqy

    info "Checking and installing dependencies..."
    do_prompt_dependencies

    info "Installing Ubuntu specific dependencies (mostly for lxml)..."
    sudo apt-get install -qqy libxml2-dev libxslt1-dev python-dev zlib1g-dev
    sudo apt-get install -qqy libc6:i386 libncurses5:i386 libstdc++6:i386 lib32z1 libbz2-1.0:i386

    info "Dependencies installed. Pulling the android-dtf Debian package..."
    wget_link=https://raw.githubusercontent.com/android-dtf/dtf/${BRANCH}/release/${DEB_NAME}

    # wget the deb, sudo dpkg it.
    wget --no-verbose "${wget_link}" -O "/tmp/${DEB_NAME}"

    if [ "$?" != "0" ]; then
        error "Unable to download Debian file!"
        exit 2
    fi

    info "Installing the android-dtf Debian package..."
    sudo dpkg -i "/tmp/${DEB_NAME}"

    info "dtf framework installation complete."

    debug "Cleaning up..."
    rm "/tmp/${DEB_NAME}"
    
    # Run dtf to start basic setup of DB + included.
    dtf

	# Next, incase this is an upgrade, let's update the config.
	dtf upgrade core --reconfigure

    # As a last step, we install to install packages.
    prompt_install_content

    info "dtf installation complete. Enjoy!"
}

do_prompt_dependencies() {

    debug "Checking for python..."
    if ! has_cmd python; then
        prompt "Python is required. Press ENTER to install. (Ctrl+C to do this manually)"
        sudo apt-get install -qqy python
    fi

    debug "Checking for java..."
    if ! has_cmd java; then
        prompt "Java is required. Press ENTER to install. (Ctrl+C to do this manually)"

        # Some Ubuntu distro's may be missing this.
        if ! has_cmd add-apt-repository; then
            sudo apt update -qqy
            info "Installing additional add-apt-repository package..."
            sudo apt-get install -qqy software-properties-common
        fi

        sudo add-apt-repository ppa:webupd8team/java
        sudo apt update -qqy
        sudo apt install -qqy oracle-java8-installer
        sudo apt install -qqy oracle-java8-set-default
    fi

    debug "Checking for pip..."
    if ! has_cmd pip; then
        prompt "pip is required. Press ENTER to install. (Ctrl+C to do this manually)"
        sudo apt-get install -qqy python-pip
    fi
}

prompt_install_content() {

    prompt "Would you like to automatically retrieve core components [Y/n]?"

    if [ "$response" != "n" ]; then

        info "Pulling core content..."
        dtf pm repo add core https://www.thecobraden.com/dtf-repos/core

        # Add aosp-data TODO

        debug "Performing sync..."
        dtf pm upgrade

        info "Content installation complete."
    else
        warning "You've choosen to skip install core content. You'll have to manually install."
    fi
}

do_uninstall() {

    if [ "$CLEAN" = "1" ]; then
        info "Removing current dtf installation..."
        sudo apt-get remove --purge -qqy android-dtf
    else
        info "Removing current dtf installation (not purge)..."
        sudo apt-get remove -qqy android-dtf
    fi

    info "dtf has been removed!"
}

dtf_installer() {

    # Parse arguments.
    parse_arguments "$@"

    # Before we begin, can we do colors?
    if ! has_cmd tput; then
        NO_COLOR=1
    else
        do_colors
    fi

    # As a first check, make sure the user has the required utilities
    debug "Checking for required utilities..."

    if ! has_cmd wget; then
        error "wget is required!"
        exit 1

    elif ! has_cmd apt-get; then
        error "apt-get is required!"
        exit 1

    elif ! has_cmd dpkg; then
        error "dpkg is required!"
        exit 1
    fi

    # Next, determine if we are installing, or upgrading.
    if has_dpkg android-dtf; then

        prompt "Installation of dtf detected, pressing ENTER will re-install."

        do_uninstall
        do_install
    else
        do_install
    fi
}

dtf_installer "$@"
