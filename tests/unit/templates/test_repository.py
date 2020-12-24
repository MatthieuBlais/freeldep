import os
from subprocess import call

import pytest

from freeldep.templates import CoreDeployerTemplate
from freeldep.templates import DeployerRepositoryTemplate
from freeldep.templates import InitializeDeployerTemplate


def test_name(deployer):
    assert DeployerRepositoryTemplate.name(deployer) == "test-deployer-repository-stack"


def test_nocloud(deployer, config):
    testdeployer = deployer.copy()
    testdeployer["cloud"] = "AWS"
    assert DeployerRepositoryTemplate.get(testdeployer, config) is not None
    with pytest.raises(NotImplementedError):
        testdeployer["cloud"] = "GCP"
        DeployerRepositoryTemplate.get(testdeployer, config)
    with pytest.raises(NotImplementedError):
        testdeployer["cloud"] = "sdfsdfsdfsdf"
        DeployerRepositoryTemplate.get(testdeployer, config)


def test_aws(deployer, config, configfile):
    template = DeployerRepositoryTemplate.aws(deployer, config)
    ref_template = InitializeDeployerTemplate.aws(deployer, config)
    core_template = CoreDeployerTemplate.aws(deployer, config)

    assert len(template) == 1
    assert template[0]["aws"]["account-id"] == configfile["aws"].get("account")
    assert template[0]["aws"]["region"] == configfile["aws"].get("region")
    assert template[0]["aws"]["deployment-role"] == configfile["aws"].get(
        "deployment-role", ""
    )
    assert os.path.isfile(template[0]["location"])
    assert template[0]["template"]["name"] == DeployerRepositoryTemplate.name(deployer)
    assert (
        template[0]["template"]["parameters"]["artifact-bucket"]
        == ref_template[0]["template"]["parameters"]["artifact-bucket"]
    )
    assert (
        template[0]["template"]["parameters"]["deployment-workflow"]
        == core_template[0]["template"]["parameters"]["deployment-workflow"]
    )


def test_aws_template(deployer, config, configfile):
    template = DeployerRepositoryTemplate.aws(deployer, config)
    assert 0 == call(f"cfn-lint {template[0]['location']}", shell=True)
