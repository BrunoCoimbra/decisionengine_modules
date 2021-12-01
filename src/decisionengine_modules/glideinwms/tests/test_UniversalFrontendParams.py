from decisionengine_modules.glideinwms.tests.fixtures import (  # noqa: F401
    gwms_config,
    gwms_invalid_config,
    gwms_src_dir,
)
from decisionengine_modules.glideinwms.UniversalFrontendParams import UniversalFrontendParams


def test_instantiation(gwms_src_dir, gwms_config):  # noqa: F811
    params = UniversalFrontendParams(gwms_src_dir, gwms_config)
    assert params.subparams["frontend_name"] == "mock_frontend"


def test_config_error(gwms_src_dir, gwms_invalid_config):  # noqa: F811
    try:
        _ = UniversalFrontendParams(gwms_src_dir, gwms_invalid_config)
    except Exception as e:
        assert isinstance(e, RuntimeError)
