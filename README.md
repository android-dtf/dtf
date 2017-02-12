Android Device Testing Framework (dtf)
======================================

[![Build Status](https://travis-ci.org/jakev/dtf.svg?branch=dev)](https://travis-ci.org/jakev/dtf)

About
-----
The Android Device Testing Framework (`dtf`) is a data collection and analysis framework to help individuals search for vulnerabilities on mobile devices. `dtf` _is not_ a:

* Vulnerability scanner or explitation framework for mobile devices
* An application assessment tool
* A "turn your phone into a hacking device" tool

Instead, `dtf` aims to allow testers to obtain information from their Android device, process this information into databases, and then start searching for vulnerabilities (all without requiring root privileges). These modules help you focus on changes made to AOSP components such as applications, frameworks, system services, as well as lower-level components such as binaries, libraries, and device drivers. In addition, you'll be able to analyze new functionality implemented by the OEMs and other parties to find vulnerabilities.

### Key Features
* 30+ modules for collecting, processing, and interacting with a device
* Builtin API for interfacing with your target device
* Python and shell bindings for creating modules
* Per-project property sub-system and logging/auditing
* Bundled versions of numerous Android tools (think apktool/smali/dex2jar)

Installing
----------
`dtf` is offically supported on Ubuntu, particularly versions 14 through 16. At this time there is not support for Windows or OS X.

### Manual Prerequisites
The only manual installation requirement for `dtf` is the Android SDK (`dtf` relies on the `adb` utility). It is recommended that you install [Android Studio](https://developer.android.com/studio/install.html), and add `adb` to your `$PATH`.

### Installation Script
To install `dtf` on Ubuntu (or update the framework), run the following commands:

    $ curl -sSL thecobraden.com/getdtf > install.sh
    $ chmod u+x install.sh
    $ ./install.sh

If you're one of those people who doesn't trust the whole `curl|bash` model, just download the script from the [GitHub](https://github.com/android-dtf/dtf/blob/dev/installscript/install.sh) page.

### Managing Installed Content
During installation, `dtf` will automatically configure itself to pull from the stable feed of core content. It is a good idea to routinely run the following command to ensure `dtf` remains up-to-date:

    $ dtf pm upgrade

### Upgrading from 1.3.0
If you previously installed `dtf` version 1.3.0, you can use the uninstall script to ensure there are no conflicts:

    $ sudo ./uninstall_1_3.sh

Note that `dtf` version 1.3.1 *does not* require any changes to a user's `$PATH`, so you should remove any `$PATH` changes related to `dtf`.

Using dtf
---------
Before using `dtf`, you'll need to enable USB debugging on your target device. If you're unsure of what this is, `dtf` is probably not the tool for you. Once it's enabled, update all Play applications, and connect the device to your PC. Assuming `adb` sees your device, we can create our project with the `init` built-in command:

    $ mkdir MyProject
    $ cd MyProject
    $ dtf init

From here, you'll want to read up on each of the many modules that `dtf` supports. See the project Wiki for additional details on using `dtf`.

Licenses
--------
`dtf` is licensed under the Apache License, Version 2.0, but contains additional code from other projects.  Check the NOTICE file for additional projects and licensing.

Contributing & Building
-----------------------
If you're interested in building your own instance of `dtf`, you'll need a couple of dependences:

    $ sudo apt-get install lintian python2.7 openjdk-8-jdk python-pip devscripts shellcheck
    $ sudo pip install flake8 pylint pytest pytest-runner wheel

You can now build the project, which is currently limited to Debian '.deb' packages. To build `dtf`, run the following command from the project root:

    $ ./gradlew clean useDebugApk makeDeb

### Creating Content
The `dtf` `man` pages are a great place to start. The `man` pages for `dtf-module(7)`, `dtf-binary(7)`, `dtf-library(7)` and `dtf-package(7)` will provide additional insight on the structure of `dtf` content. If you're creating a module, it's a good idea to ensure that it passes all the checks with the `dtf_check` utility. More information can be found in the `man` pages for `dtf-check(1)`. To check your new module:

    $ dtf_check -sa my_cool_module

Questions & Comments
--------------------
Please use the project's GitHub issue tracker for reporting bugs. For bugs related to a specific module, please use the issue tracker for that particular git repo.
