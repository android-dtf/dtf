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

- JRE 1.7 or 1.8
- Python 2.7 or higher
- A true Bash shell (no Dash!!!), with general purpose Linux utilities (sed, awk, etc.)
- sqlite3
- adb
- Python pip 
- 'colored' pip module

Using dtf
---------
For details on getting started with `dtf`, check out the documentation over at the www.thecobraden.com/projects/dtf/.

Licenses
--------
`dtf` is licensed under the Apache License, Version 2.0, but contains additional code from other projects.  Check the NOTICE file for additional projects and licensing.

Contributing & Building
-----------------------
Pull requests are welcome. In order to build `dtf`, you'll need a couple of dependences:

    $ sudo apt-get install pylint lintian python2.7 openjdk-8-jdk python-pip
    $ sudo pip install flake8

Building `dtf` is currently limited to Debian '.deb' packages. To generate a new Debian archive, you can use the following command:

    $ gradle build

`dtf` is fully PEP8 compliant and uses both `pylint` and `flake8` for syntax/style checking. Please confirm that all changes made to the Python code pass these checks.

    $ gradle doPythonTests

Questions & Comments
--------------------
Please use the GitHub issue tracker for reporting bugs. Questions, comments, or frustrations can be directed to javallet[at]gmail[dot].com.
