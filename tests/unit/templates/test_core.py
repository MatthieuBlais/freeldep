import os

from cli.templates import CoreDeployerTemplate
from cli.templates import InitializeDeployerTemplate


def test_name(deployer):
    assert CoreDeployerTemplate.name(deployer) == "test-deployer-core-stack"


def test_aws(deployer, config, configfile):
    template = CoreDeployerTemplate.aws(deployer, config)
    ref_template = InitializeDeployerTemplate.aws(deployer, config)

    assert len(template) == 1
    assert template[0]["aws"]["account-id"] == configfile["aws"].get("account")
    assert template[0]["aws"]["region"] == configfile["aws"].get("region")
    assert template[0]["aws"]["deployment-role"] == configfile["aws"].get(
        "deployment-role", ""
    )
    assert os.path.isfile(template[0]["location"])
    assert template[0]["template"]["name"] == CoreDeployerTemplate.name(deployer)
    assert (
        template[0]["template"]["parameters"]["registry-table"]
        == ref_template[0]["template"]["parameters"]["registry-table"]
    )
    assert (
        template[0]["template"]["parameters"]["artifact-bucket"]
        == ref_template[0]["template"]["parameters"]["artifact-bucket"]
    )
    assert (
        template[0]["template"]["parameters"]["deployment-workflow"]
        == f"{deployer['name']}-deployer-core"
    )
    assert (
        template[0]["template"]["lambda-code-key"]
        == f"packages/{deployer['name']}-deployer-core-stack/"
    )
    assert len(template[0]["lambdas"]) == 1
    assert os.path.isdir(template[0]["lambdas"][0]["location"])
