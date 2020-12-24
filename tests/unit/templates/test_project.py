import os
from subprocess import call

import pytest

from freeldep.templates import ProjectTemplate


def test_name(deployer):
    assert ProjectTemplate.name(deployer, "project") == "test-deployer-project-project"


def test_nocloud(deployer, config):
    testdeployer = deployer.copy()
    testdeployer["cloud"] = "AWS"
    assert ProjectTemplate.get("project", "master", testdeployer, config) is not None
    with pytest.raises(NotImplementedError):
        testdeployer["cloud"] = "GCP"
        ProjectTemplate.get("project", "master", testdeployer, config)
    with pytest.raises(NotImplementedError):
        testdeployer["cloud"] = "sdfsdfsdfsdf"
        ProjectTemplate.get("project", "master", testdeployer, config)


def test_aws(deployer, config, configfile):
    template = ProjectTemplate.aws("project", "master", deployer, config)

    assert len(template) == 1
    assert template[0]["aws"]["account-id"] == configfile["aws"].get("account")
    assert template[0]["aws"]["region"] == configfile["aws"].get("region")
    assert template[0]["aws"]["deployment-role"] == configfile["aws"].get(
        "deployment-role", ""
    )
    assert os.path.isfile(template[0]["location"])
    assert template[0]["template"]["name"] == ProjectTemplate.name(deployer, "project")


def test_aws_template(deployer, config, configfile):
    template = ProjectTemplate.aws("project", "master", deployer, config)
    assert 0 == call(f"cfn-lint {template[0]['location']}", shell=True)
