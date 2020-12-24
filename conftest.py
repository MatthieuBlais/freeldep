import configparser
import os

import boto3
import pytest
from moto import mock_cloudformation  # pylint: disable=import-error
from moto import mock_s3  # pylint: disable=import-error

from freeldep.config import ConfigParser


@pytest.fixture
def deployer():
    return {
        "name": "test",
        "cloud": "AWS",
        "artifact": "test-deployer-artifact-bucket-809322",
        "registry": "test-deployer-deployment-registry",
        "deployment-workflow": "test-deployer-core",
        "codebuild-service": "test-deployer-service",
        "service-trigger": "test-deployer-service-trigger",
        "service-role": "test-deployer-service-role",
        "subscriptions": ["test-deployer-de-data"],
        "repository": "test-subscription",
        "projects": ["test-project"],
    }


@pytest.fixture
def configfile():
    config = configparser.ConfigParser()
    config.read("./tests/data/config.ini")
    return config


@pytest.fixture
def config():
    return ConfigParser("./tests/data/config.ini")


@pytest.fixture
def template():
    return {
        "aws": {"region": "ap-southeast-1", "account-id": "123456789011"},
        "location": "./templates/aws/deployer-core.yaml",
        "template": {"name": "test", "parameters": {}, "lambda-code-key": "test"},
        "functions": [
            {
                "name": "package",
                "location": "./core/",
                "template-attribute": "lambda-code-key",
                "bucket": "test",
            }
        ],
    }


@pytest.fixture(scope="module")
def aws_credentials():
    os.environ["AWS_ACCESS_KEY_ID"] = "none"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "none"
    os.environ["AWS_SESSION_TOKEN"] = "none"
    os.environ["AWS_SECURITY_TOKEN"] = "none"


@pytest.yield_fixture(scope="module")
def cloudformation_client(aws_credentials):
    with mock_cloudformation:
        conn = boto3.client("cloudformation")
        yield conn


@pytest.yield_fixture(scope="module")
def s3_client(aws_credentials):
    with mock_s3:
        conn = boto3.client("s3")
        yield conn
