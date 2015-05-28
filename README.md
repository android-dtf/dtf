Android Device Testing Framework (dtf)
======================================

About
-----
The Android Device Testing Framework ("dtf") is a data collection and analysis framework to help individuals answer the question: "Where are the vulnerabilities on this mobile device?" Dtf provides a modular approach and built-in APIs that allows testers to quickly create scripts to interact with their Android devices. By default, dtf does not include any modules, but a collection of testing modules is made available on the Cobra Den website (www.thecobraden.com/projects/dtf/). These modules allow testers to obtain information from their Android device, process this information into databases, and then start searching for vulnerabilities (all without requiring root privileges). These modules help you focus on changes made to AOSP components such as applications, frameworks, system services, as well as lower-level components such as binaries, libraries, and device drivers. In addition, you'll be able to analyze new functionality implemented by the OEMs and other parties to find vulnerabilities.

Installing & Using
-------------
dtf is offically supported on Ubuntu 14.04 LTS (x64). To install dtf on Ubuntu, run the following command as root:

    analyst@testing$ sudo ./install_dependencies.sh

You can use another OS if you'd like, but your mileage will vary. To help, the following packages are required:

- JRE 1.7
- Python 2.6 or higher
- A true Bash shell (no Dash!!!), with general purpose Linux utilities (sed, awk, etc.)
- sqlite3
- adb

Using dtf
---------
For details on getting started with dtf, check out the documentation over at the www.thecobraden.com/projects/dtf/.

Licenses
--------
Dtf is licensed under the Apache License, Version 2.0, but contains additional code from other projects.  Check the NOTICE file for additional projects and licensing.

Questions & Comments
--------------------
Any bug reports, questions, comments, frustrations, please direct them to javallet[at]gmail[dot].com.  I'll do my best to help! Also be sure to check any updates on www.thecobraden.com.
