from argparse import ArgumentParser, Namespace

from decisionengine_modules.glideinwms import configure_gwms_frontend
from decisionengine_modules.glideinwms.tests.fixtures import de_client_config  # noqa: F401


def test_get_arg_parser():
    parser = configure_gwms_frontend.get_arg_parser()
    assert isinstance(parser, ArgumentParser)


def test_main(de_client_config):
    args = Namespace()
    args.web_base_dir = "/var/lib/gwms-frontend/web-base"
    args.update_scripts = False
    args.de_frontend_config = "/var/lib/gwms-frontend/vofrontend/de_frontend_config"
    with de_client_config:
        configure_gwms_frontend.main(args)
