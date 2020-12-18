import pytest

from cli.modules.create import validate_bucket
from cli.modules.create import validate_emails
from cli.modules.create import validate_name
from cli.modules.create import validate_registry


def test_validate_name():
    assert validate_name("sdfsdfdfsdf") == "sdfsdfdfsdf"
    assert (
        validate_name("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
        == "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    )
    with pytest.raises(ValueError):
        validate_name("sdfsdfd223!#fsdf") == "sdfsdfdfsdf"


def test_validate_bucket():
    assert validate_bucket("test", "testbucket") == "testbucket"
    with pytest.raises(ValueError):
        validate_bucket("test", "testbucket@")
    bucket = validate_bucket("test", None)
    assert bucket.startswith("test")
    assert bucket.startswith("test-deployer-artifact-bucket-")
    assert len(bucket.split("-")[-1]) == 6


def test_validate_registry():
    assert validate_registry("test", "testregistry") == "testregistry"
    assert (
        validate_registry(
            "test",
            "testregistrysssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssss"
            "sssssssssssssssssssssssss",
        )
        == "testregistrysssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssss"
        "sssssssssssssssssssss"
    )
    with pytest.raises(ValueError):
        validate_bucket("test", "testregistry@")
    registry = validate_registry("test", None)
    assert registry.startswith("test")


def test_validate_emails():
    assert validate_emails("test@gmail.com")[0] == "test@gmail.com"
    assert len(validate_emails("test@gmail.com,test2@gmail.com")) == 2
    assert len(validate_emails("test@gmail.com,test2")) == 1
