import json
import os

import pytest
import yaml

from cli.modules.utils import delete_deployer
from cli.modules.utils import execute_script
from cli.modules.utils import file_exists
from cli.modules.utils import get_workflow_id
from cli.modules.utils import list_files
from cli.modules.utils import load_deployer
from cli.modules.utils import mkdir
from cli.modules.utils import read_json
from cli.modules.utils import read_yaml
from cli.modules.utils import save_deployer
from cli.modules.utils import save_json
from cli.modules.utils import shorten_expr
from cli.modules.utils import valid_expr

TEMP_FOLDER = "/tmp/"


def test_valid_expr():
    assert valid_expr("test", "test", r"^test$") is None
    with pytest.raises(ValueError):
        valid_expr("test", "testtest", r"^test$")


def test_shorten_expr():
    assert shorten_expr("12345", 10) == "12345"
    assert shorten_expr("12345", 2) == "12"


def test_mkdir():
    directory = TEMP_FOLDER + "pytest/subg"
    assert os.path.isdir(directory) is False
    mkdir(directory)
    assert os.path.isdir(directory) is True
    os.removedirs(directory)


def test_file_exists():
    filename = TEMP_FOLDER + "pytest.txt"
    assert file_exists(filename) is False
    with open(filename, "w+") as f:
        json.dump([], f)
    assert file_exists(filename) is True
    os.remove(filename)


def test_list_files():
    FOLDER = "./tests/data/"
    files = list_files(FOLDER)
    for f in files:
        print(f)
        assert os.path.isfile(FOLDER + f)
    assert len(files) == 1


def test_save_json():
    filename = TEMP_FOLDER + "test.json"
    data = {"test": True}
    if file_exists(filename):
        os.remove(filename)
    assert file_exists(filename) is False
    save_json(filename, data)
    assert file_exists(filename)
    data = read_json(filename)
    assert data["test"] is True


def test_read_yaml():
    filename = TEMP_FOLDER + "test.yaml"
    data = {"test": True}
    with open(filename, "w+") as f:
        yaml.dump(data, f)
    assert file_exists(filename)
    data = read_yaml(filename)
    assert data["test"] is True


def test_manage_deployer(deployer, config, configfile):
    home_folder = configfile["cli"].get("home_folder")
    test_deployer = home_folder + "/test.json"
    assert file_exists(test_deployer) is False
    save_deployer(deployer, config)
    assert file_exists(test_deployer) is True
    saved_deployer = load_deployer(config, "test")
    for key in saved_deployer:
        assert saved_deployer[key] is deployer[key]
    delete_deployer(config, "test")
    assert file_exists(test_deployer) is False


def test_load_deployer(deployer, config, configfile):
    home_folder = configfile["cli"].get("home_folder")
    test_deployer = home_folder + "/test.json"
    assert file_exists(test_deployer) is False
    save_deployer(deployer, config)
    assert file_exists(test_deployer) is True
    saved_deployer = load_deployer(config, "test")
    for key in saved_deployer:
        assert saved_deployer[key] == deployer[key]
    delete_deployer(config, "test")
    assert file_exists(test_deployer) is False


def test_load_missing_deployer(deployer, config, configfile):
    saved_deployer = load_deployer(config, "test")
    assert saved_deployer is None


def test_execute_script():
    filename = TEMP_FOLDER + "test.sh"
    with open(filename, "w+") as f:
        f.write("ls -l")
    assert execute_script(filename)
    os.remove(filename)


def test_get_workflow_id(deployer, config):
    workflow_name = "test-workflow"
    expected_aws_arn = f"arn:aws:states: :stateMachine:{workflow_name}"
    assert get_workflow_id("test-workflow", config) == expected_aws_arn
