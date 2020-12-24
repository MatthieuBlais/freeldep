import os

import pytest

from freeldep.templates import CoreDeployerTemplate
from freeldep.templates import InitializeDeployerTemplate
from freeldep.templates import ServiceDeployerTemplate


def test_name(deployer):
    assert ServiceDeployerTemplate.name(deployer) == "test-deployer-service-stack"


def test_nocloud(deployer, config):
    testdeployer = deployer.copy()
    testdeployer["cloud"] = "AWS"
    assert ServiceDeployerTemplate.get(testdeployer, config) is not None
    with pytest.raises(NotImplementedError):
        testdeployer["cloud"] = "GCP"
        ServiceDeployerTemplate.get(testdeployer, config)
    with pytest.raises(NotImplementedError):
        testdeployer["cloud"] = "sdfsdfsdfsdf"
        ServiceDeployerTemplate.get(testdeployer, config)


def test_aws(deployer, config, configfile):
    template = ServiceDeployerTemplate.aws(deployer, config)
    ref_template = InitializeDeployerTemplate.aws(deployer, config)

    assert len(template) == 1
    assert template[0]["aws"]["account-id"] == configfile["aws"].get("account")
    assert template[0]["aws"]["region"] == configfile["aws"].get("region")
    assert template[0]["aws"]["deployment-role"] == configfile["aws"].get(
        "deployment-role", ""
    )
    assert os.path.isfile(template[0]["location"])
    assert template[0]["template"]["name"] == ServiceDeployerTemplate.name(deployer)
    assert (
        template[0]["template"]["parameters"]["artifact-bucket"]
        == ref_template[0]["template"]["parameters"]["artifact-bucket"]
    )
    assert (
        template[0]["template"]["parameters"]["deployment-workflow"]
        == CoreDeployerTemplate.aws(deployer, config)[0]["template"]["parameters"][
            "deployment-workflow"
        ]
    )
    assert (
        template[0]["template"]["lambda-code-key"]
        == f"packages/{deployer['name']}-deployer-service-stack/"
    )
    assert len(template[0]["functions"]) == 1
    assert os.path.isdir(template[0]["functions"][0]["location"])
