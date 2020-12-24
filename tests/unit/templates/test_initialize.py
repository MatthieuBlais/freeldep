import os
from subprocess import call

import pytest

from freeldep.templates import InitializeDeployerTemplate


def test_name(deployer):
    assert (
        InitializeDeployerTemplate.name(deployer)
        == "test-deployer-initialization-stack"
    )


def test_nocloud(deployer, config):
    testdeployer = deployer.copy()
    assert InitializeDeployerTemplate.get("AWS", testdeployer, config) is not None
    assert InitializeDeployerTemplate.get("GCP", testdeployer, config) is not None
    with pytest.raises(NotImplementedError):
        InitializeDeployerTemplate.get("sdsd", testdeployer, config)


def test_aws(deployer, config, configfile):
    template = InitializeDeployerTemplate.aws(deployer, config)

    assert len(template) == 1
    assert template[0]["aws"]["account-id"] == configfile["aws"].get("account")
    assert template[0]["aws"]["region"] == configfile["aws"].get("region")
    assert template[0]["aws"]["deployment-role"] == configfile["aws"].get(
        "deployment-role", ""
    )
    assert os.path.isfile(template[0]["location"])
    assert template[0]["template"]["name"] == InitializeDeployerTemplate.name(deployer)
    assert (
        template[0]["template"]["parameters"]["registry-table"] == deployer["registry"]
    )
    assert (
        template[0]["template"]["parameters"]["artifact-bucket"] == deployer["artifact"]
    )


def test_aws_template(deployer, config, configfile):
    template = InitializeDeployerTemplate.aws(deployer, config)
    assert 0 == call(f"cfn-lint {template[0]['location']}", shell=True)
