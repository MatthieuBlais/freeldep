import os
import uuid

import pytest

from freeldep.cloud.aws.validate import CfnStackValidation


def test_file_exists():
    filename = "/tmp/" + uuid.uuid1().hex + ".test"
    assert CfnStackValidation._file_exists(filename) is False
    with open(filename, "w+") as f:
        f.write("hello")
    assert CfnStackValidation._file_exists(filename) is True
    os.remove(filename)


def test_validate_lambda():
    filename = "/tmp/" + uuid.uuid1().hex + ".test"
    with open(filename, "w+") as f:
        f.write("hello")
    config = {
        "name": "test",
        "location": filename,
        "template-attribute": "asdasd",
        "bucket": "sfsdfs",
    }
    with pytest.raises(ValueError):
        CfnStackValidation._validate_lambda_config([config])
    os.remove(filename)
    config["location"] = "/tmp/"
    assert CfnStackValidation._validate_lambda_config([config]) is None
    config_failed = config.copy()
    del config_failed["name"]
    with pytest.raises(KeyError):
        CfnStackValidation._validate_lambda_config([config_failed])
    config_failed = config.copy()
    del config_failed["location"]
    with pytest.raises(KeyError):
        CfnStackValidation._validate_lambda_config([config_failed])


def test_config(template):
    assert CfnStackValidation.validate_config(template) is None
    template_test = template.copy()
    del template_test["aws"]
    with pytest.raises(KeyError):
        CfnStackValidation.validate_config(template_test)
    template_test = template.copy()
    del template_test["template"]
    with pytest.raises(KeyError):
        CfnStackValidation.validate_config(template_test)
    template_test = template.copy()
    del template_test["location"]
    with pytest.raises(KeyError):
        CfnStackValidation.validate_config(template_test)
    template_test = template.copy()
    template_test["location"] = "dsdsdds"
    with pytest.raises(FileNotFoundError):
        CfnStackValidation.validate_config(template_test)


def test_validate_template():
    config = {"name": "test", "parameters": ""}
    with pytest.raises(ValueError):
        CfnStackValidation._validate_template_config([config])
    with pytest.raises(ValueError):
        CfnStackValidation._validate_template_config(config)
    config = {"name": "test", "parameters": {}}
    assert CfnStackValidation._validate_template_config(config) is None


def test_validate_aws():
    config = {"region": "test", "account-id": "111111111111"}
    assert CfnStackValidation._validate_aws_config(config) is None
    config["region"] = 22
    with pytest.raises(ValueError):
        CfnStackValidation._validate_aws_config(config)
    with pytest.raises(ValueError):
        CfnStackValidation._validate_aws_config([config])
    config = {"region": "test", "account-id": "222"}
    with pytest.raises(ValueError):
        CfnStackValidation._validate_aws_config(config)
    config = {"name": "test", "parameters": {}}
    with pytest.raises(KeyError):
        CfnStackValidation._validate_aws_config(config)
    config = {"region": "test", "parameters": {}}
    with pytest.raises(KeyError):
        CfnStackValidation._validate_aws_config(config)
