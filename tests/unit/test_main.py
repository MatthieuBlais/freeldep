import logging
import os

import pytest
from click.testing import CliRunner

from freeldep.main import Cli
from freeldep.main import cli


def test_cli():
    runner = CliRunner()
    result = runner.invoke(cli)
    assert result.exit_code == 0


def test_cli_logging():
    cli_obj = Cli(aws_profile=None, verbose=0)
    assert cli_obj._get_logging_level(0) == logging.WARNING
    assert cli_obj._get_logging_level(1) == logging.INFO
    assert cli_obj._get_logging_level(2) == logging.DEBUG
    assert cli_obj._get_logging_level(1029) == logging.DEBUG
    assert cli_obj._get_logging_level(-1029) == logging.WARNING


def test_cli_cloud():
    os.environ["AWS_PROFILE"] = ""
    cli_obj = Cli()
    with pytest.raises(RuntimeError):
        cli_obj.require_cloud_access()
    cli_obj = Cli(aws_profile="default")
    cli_obj.require_cloud_access()


def test_version():
    runner = CliRunner()
    result = runner.invoke(cli, ["version"])
    assert result.exit_code == 0
    assert "CLI" in result.output and "Version" in result.output
