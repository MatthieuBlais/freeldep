import pytest

from freeldep.modules.deploy import deploy_project


def test_deploy_project():
    with pytest.raises(FileNotFoundError):
        deploy_project("test", "test", "test.yaml")
    with pytest.raises(RuntimeError):
        deploy_project("test", "test", "tests/data/stack.yaml", "tests/data/package.sh")
