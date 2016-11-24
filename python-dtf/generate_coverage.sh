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
#
# Generate coverage information

# If we are in travis, we don't need to use virtualenv. For now,
# locally we need to activate it.
if [ "$TRAVIS"  != "true" ]; then
    echo "Activating virtualenv"
    . venv/bin/activate
fi

export COVERAGE_PROCESS_START=.coveragerc

# Remove old coverage data
coverage erase

# Just incase, remove any .dtf* stuff.
rm .dtfini .dtflog 2>/dev/null

# Need this to test local install
python setup.py develop


# Run the unit tests.
coverage run --concurrency=multiprocessing -m py.test tests/unit

# Run the integration tests.
# We need to make sure there is no .dtf, but for local testing,
# I'd rather not have my stuff blown away. Move it, then move back.
if [ -e ~/.dtf ]; then
    mv ~/.dtf ~/.dtf_bk
fi
coverage run --concurrency=multiprocessing -m py.test tests/integration

# Move it back
if [ -e ~/.dtf_bk ]; then
    rm -rf ~/.dtf
    mv ~/.dtf_bk ~/.dtf
fi

# Combine and show
coverage combine
coverage report
coverage html

# Make sure to unset this
python setup.py develop --uninstall

if [ "$TRAVIS"  != "true" ]; then
    deactivate
fi
