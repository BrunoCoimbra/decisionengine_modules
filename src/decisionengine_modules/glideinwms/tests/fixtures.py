import json

from unittest import mock

import pytest

from glideinwms.lib.xmlParse import OrderedDict

CONFIG = """{
    "frontend_name": "mock_frontend",
    "groups": {
        "main": {}
    },
    "security": {
        "classad_proxy": "/proxy/vofe_proxy",
        "proxy_DN": "/DC=org/DC=incommon/C=US/ST=Illinois/L=Batavia/O=Fermi Research Alliance/OU=Fermilab/CN=mock_frontend.fnal.gov"
    },
    "collectors": [
        {
            "DN": "/DC=org/DC=incommon/C=US/ST=Illinois/L=Batavia/O=Fermi Research Alliance/OU=Fermilab/CN=mock_collector.fnal.gov",
            "group": "default",
            "node": "fermicloud001.fnal.gov:9618",
            "secondary": "False"
        }
    ]
}"""

INVALID_CONFIG = """{
    "frontend_name": "mock_frontend",
    "invalid_key": "test_value"
}"""

MODULE_CONFIG = '{"glideinwms": ' + CONFIG + '}'

@pytest.fixture(scope="module")
def gwms_src_dir():
    return "/tmp/gwms_mock_dir"


@pytest.fixture(scope="module")
def gwms_config():
    return json.loads(CONFIG, object_hook=OrderedDict)


@pytest.fixture(scope="module")
def gwms_invalid_config():
    return json.loads(INVALID_CONFIG, object_hook=OrderedDict)


@pytest.fixture(scope="module")
def de_client_config():
    return mock.patch("decisionengine.framework.engine.de_client.main", return_value=MODULE_CONFIG)
