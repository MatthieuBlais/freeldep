import json
import os.path
import re
import subprocess
from os import listdir
from os.path import isfile
from os.path import join
from pathlib import Path

import yaml


def valid_expr(name, val, regex):
    if not bool(re.match(regex, val)):
        raise ValueError(f"{name} must match this format {regex}")


def shorten_expr(val, max_len):
    return val if len(val) < max_len else val[:max_len]


def mkdir(directory):
    Path(os.path.expanduser(directory)).mkdir(parents=True, exist_ok=True)


def file_exists(file_path):
    return os.path.exists(os.path.expanduser(file_path))


def list_files(directory):
    directory = os.path.expanduser(directory)
    return [f for f in listdir(directory) if isfile(join(directory, f))]


def save_json(filepath, event, indent=None):
    with open(os.path.expanduser(filepath), "w+") as f:
        json.dump(event, f, indent=indent)


def read_json(filepath):
    with open(os.path.expanduser(filepath), "r") as f:
        return json.load(f)


def read_yaml(filepath):
    with open(os.path.expanduser(filepath), "r") as f:
        return yaml.safe_load(f)


def save_deployer(deployer, config):
    """Save the deployer configuration locally"""
    home_folder = config.get("cli", "home_folder", "~/.freeldep")
    mkdir(home_folder)
    save_json(f"{home_folder}/{deployer['name']}.json", deployer)


def load_deployer(config, deployer):
    home_folder = config.get("cli", "home_folder", "~/.freeldep")
    config_file = home_folder + "/" + deployer + ".json"
    if not file_exists(config_file):
        return None
    return read_json(config_file)


def delete_deployer(config, deployer):
    home_folder = config.get("cli", "home_folder", "~/.freeldep")
    config_file = home_folder + "/" + deployer + ".json"
    if file_exists(config_file):
        os.remove(os.path.expanduser(config_file))


def execute_script(script):
    try:
        subprocess.check_call(f"/bin/bash {script}".split(" "))
        return True
    except subprocess.CalledProcessError:
        return False


def get_workflow_id(workflow_name, config):
    if config.get("aws", "account", None) is not None:
        region = config.get("aws", "region", "ap-southeast-1")
        account = config.get("aws", "account", None)
        return f"arn:aws:states:{region}:{account}:stateMachine:{workflow_name}"
