import os

import click
import pytest

from cli.config import ConfigParser


def test_config_error():
    os.environ["FREELDEP_CONFIG"] = ""
    os.environ["FREELDEP_HOME"] = ""
    with pytest.raises(click.UsageError):
        ConfigParser("")


def test_config_filename():
    os.environ["FREELDEP_CONFIG"] = ""
    os.environ["FREELDEP_HOME"] = ""
    ConfigParser("./tests/data/config.ini")


def test_config_env():
    os.environ["FREELDEP_CONFIG"] = ""
    os.environ["FREELDEP_HOME"] = "./cli/"
    ConfigParser("")


def test_config_env_2():
    os.environ["FREELDEP_CONFIG"] = "./tests/data/config.ini"
    os.environ["FREELDEP_HOME"] = ""
    ConfigParser("")


def test_config_get_en():
    os.environ["FREELDEP_CONFIG"] = ""
    os.environ["FREELDEP_HOME"] = ""
    config = ConfigParser("./tests/data/config.ini")
    assert config.get("cli", "name", "") == "testcli"
    assert config.get("cli", "asdasd", "default") == "default"
    assert config.get("assdasd", "asdasd", "1111") == "1111"
    assert config.get("aws", "region", "1111") == "region"
