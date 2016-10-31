Android Device Testing Framework (dtf)
======================================

About
-----
The Android Device Testing Framework (`dtf`) is a data collection and analysis framework to help individuals answer the question: "Where are the vulnerabilities on this mobile device?" `dtf` provides a modular approach and built-in APIs that allows testers to quickly create scripts to interact with their Android devices. By default, `dtf` does not include any modules, but a collection of testing modules is made available on the [Cobra Den website](www.thecobraden.com/projects/dtf/). These modules allow testers to obtain information from their Android device, process this information into databases, and then start searching for vulnerabilities (all without requiring root privileges). These modules help you focus on changes made to AOSP components such as applications, frameworks, system services, as well as lower-level components such as binaries, libraries, and device drivers. In addition, you'll be able to analyze new functionality implemented by the OEMs and other parties to find vulnerabilities.

Installing & Using
------------------
`dtf` is offically supported on Ubuntu, particularly versions 14 and 15. To install `dtf` on Ubuntu, run the following command as root:

    analyst@testing$ sudo ./install_dependencies.sh
    analyst@testing$ sudo python setup.py install

You can use another OS if you'd like, but your mileage will vary. To help, the following packages are required:

- JRE 1.8
- Python 2.7 or higher
- sqlite3
- adb
- Python pip 
- 'colored' pip module
- 'lxml' python module

### Upgrading from 1.3.0
If you previously installed `dtf` version 1.3.0, you can use the uninstall script to ensure there are no conflicts:

    $ sudo ./uninstall_1_3.sh

Note that `dtf` version 1.3.1 *does not* require any changes to a user's PATH, so you should remove path changes related to `dtf`.

Using dtf
---------
For details on getting started with `dtf`, check out the documentation over at the www.thecobraden.com/projects/dtf/.

Licenses
--------
`dtf` is licensed under the Apache License, Version 2.0, but contains additional code from other projects.  Check the NOTICE file for additional projects and licensing.

Contributing & Building
-----------------------
If you're interested in building your own instance of `dtf`, you'll need a couple of dependences:

    $ sudo apt-get install lintian python2.7 openjdk-8-jdk python-pip devscripts shellcheck
    $ sudo pip install flake8 pylint pytest pytest-runner

You can now build the project, which is currently limited to Debian '.deb' packages. To build `dtf`, run the following command from the project root:

    $ ./gradlew clean build

### Creating Content
The `dtf` `man` pages are a great place to start. The `man` pages for `dtf-module(7)`, `dtf-binary(7)`, `dtf-library(7)` and `dtf-package(7)` will provide additional insight on the structure of `dtf` content. If you're creating a module, ensure that it passes all the checks with `dtf_check`. More information can be found in the `man` pages for `dtf-check(1)`. To check your new module:

    $ dtf_check -sa my_cool_module

Questions & Comments
--------------------
Please use the GitHub issue tracker for reporting bugs. Questions, comments, or frustrations can be directed to javallet[at]gmail[dot].com.
