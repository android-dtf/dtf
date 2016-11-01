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
"""pytest for using dtf property manager"""

import dtf.properties as prop
import common
import pytest


# prop_set() tests
def test_set_new_property():

    """Attempt to set a new property (existing section)"""

    value = '1'
    contents = ("[info]\n"
                "real = not_real")

    common.deploy_config_raw(contents)

    prop.set_prop('info', 'sdk', value)
    assert prop.get_prop('info', 'sdk') == value

    common.undeploy()


def test_set_new_section_property():

    """Set a property that has no section (yet)"""

    value = '1'
    common.deploy_config_raw("")

    prop.set_prop('info', 'sdk', value)
    assert prop.get_prop('info', 'sdk') == value

    common.undeploy()

    return 0


def test_set_existing_property():

    """Set a property that already exists"""

    value = 'new'

    contents = ("[Info]\n"
                "sdk = old")

    common.deploy_config_raw(contents)

    prop.set_prop('info', 'sdk', value)
    assert prop.get_prop('info', 'sdk') == value

    common.undeploy()

    return 0


def test_set_property_casing():

    """Set a prop and try to retrieve with casing"""

    sdk = '1'
    common.deploy_config_raw("")

    prop.set_prop('INFO', 'sdk', sdk)
    assert prop.get_prop('info', 'sdk') == sdk
    assert prop.get_prop('Info', 'sdk') == sdk
    assert prop.get_prop('INFO', 'sdk') == sdk

    common.undeploy()

    return 0


# prop_get() tests
def test_get_empty_config():

    """Attempts to get a property without a valid config"""

    common.deploy_config_raw("")

    with pytest.raises(prop.PropertyError):
        prop.get_prop('info', 'sdk')

    common.undeploy()

    return 0


def test_get_property():

    """Attempts to get a valid property"""

    sdk = '23'
    contents = ("[Info]\n"
                "sdk = %s" % sdk)

    common.deploy_config_raw(contents)

    assert prop.get_prop('info', 'sdk') == sdk

    common.undeploy()

    return 0


def test_get_property_no_option():

    """Attempt to get property that doesnt exist"""

    contents = ("[Info]\n"
                "vmtype = arm64")

    common.deploy_config_raw(contents)

    with pytest.raises(prop.PropertyError):
        prop.get_prop('info', 'sdk')

    common.undeploy()

    return 0


def test_get_property_casing():

    """Get a prop with alternating casing"""

    sdk = '23'
    contents = ("[Info]\n"
                "sdk = %s" % sdk)

    common.deploy_config_raw(contents)

    assert prop.get_prop('info', 'sdk') == sdk
    assert prop.get_prop('Info', 'sdk') == sdk
    assert prop.get_prop('INFO', 'sdk') == sdk

    common.undeploy()

    return 0


# prop_del() tests
def test_del_empty_config():

    """Attempts to delete a property without a valid config"""

    common.deploy_config_raw("")

    assert prop.del_prop('info', 'sdk') != 0

    common.undeploy()

    return 0


def test_del_property():

    """Attempts to delete a valid property"""

    contents = ("[Info]\n"
                "sdk = 23")

    common.deploy_config_raw(contents)

    prop.del_prop('info', 'sdk')

    common.undeploy()

    return 0


def test_del_property_invalid():

    """Attempts to delete a property that doesnt exist"""

    contents = ("[Info]\n"
                "vmtype = 64")

    common.deploy_config_raw(contents)

    assert prop.del_prop('info', 'sdk') != 0

    common.undeploy()

    return 0


def test_del_property_casing():

    """Delete a prop with alternating casing"""

    sdk = '23'
    contents = ("[Info]\n"
                "sdk = %s" % sdk)

    common.deploy_config_raw(contents)

    prop.del_prop('info', 'sdk')

    common.undeploy()

    return 0


# prop_test() tests
def test_test_empty_config():

    """Test a property without a valid config"""

    common.deploy_config_raw("")

    assert prop.test_prop('info', 'sdk') == 0

    common.undeploy()

    return 0


def test_test_property():

    """Test a valid property"""

    contents = ("[Info]\n"
                "sdk = 23")

    common.deploy_config_raw(contents)

    assert prop.test_prop('info', 'sdk') == 1

    common.undeploy()

    return 0


def test_test_invalid_property():

    """Test a missingproperty"""

    contents = ("[Info]\n"
                "vmtype = arm64")

    common.deploy_config_raw(contents)

    assert prop.test_prop('info', 'sdk') == 0

    common.undeploy()

    return 0


def test_test_property_casing():

    """Test a prop with alternating casing"""

    sdk = '23'
    contents = ("[Info]\n"
                "sdk = %s" % sdk)

    common.deploy_config_raw(contents)

    assert prop.test_prop('info', 'sdk') == 1

    common.undeploy()

    return 0
