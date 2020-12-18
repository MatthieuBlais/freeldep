import json
import os
from subprocess import call

from click.testing import CliRunner

from cli.main import cli
from cli.modules.utils import delete_deployer
from cli.modules.utils import load_deployer
from cli.modules.utils import save_deployer


CONFIG_SAMPLE = "./tests/data/config.ini"


def test_show_configs(deployer, config):
    os.environ["FREELDEP_CONFIG"] = CONFIG_SAMPLE
    runner = CliRunner()
    result = runner.invoke(cli, ["show", "configs"])
    assert result.exit_code == 0
    save_deployer(deployer, config)
    result = runner.invoke(cli, ["show", "configs"])
    assert "test" in result.output.strip()
    delete_deployer(config, "test")


def test_show_config(deployer, config):
    os.environ["FREELDEP_CONFIG"] = CONFIG_SAMPLE
    delete_deployer(config, "test")
    runner = CliRunner()
    result = runner.invoke(cli, ["show", "config", "test"])
    assert result.exit_code != 0
    save_deployer(deployer, config)
    result = runner.invoke(cli, ["show", "config", "test"])
    assert result.exit_code == 0
    assert json.loads(result.output)["name"] == "test"
    delete_deployer(config, "test")


def test_create_stack(deployer, config):
    os.environ["FREELDEP_CONFIG"] = CONFIG_SAMPLE
    runner = CliRunner()
    result = runner.invoke(
        cli, ["create", "deployer", "testt", "--dryrun", "--output-location", "out/"]
    )
    assert result.exit_code == 0
    assert os.path.isfile("out/testt-deployer-initialization-stack.config.yaml")
    assert os.path.isfile("out/testt-deployer-initialization-stack.yaml")
    returncall = call(
        "cfn-lint out/testt-deployer-initialization-stack.yaml", shell=True
    )
    assert returncall == 0
    result = runner.invoke(
        cli,
        [
            "deploy",
            "core",
            "--deployer",
            "testt",
            "--dryrun",
            "--output-location",
            "out/",
        ],
    )
    assert result.exit_code == 0
    assert os.path.isfile("out/testt-deployer-core-stack.config.yaml")
    assert os.path.isfile("out/testt-deployer-core-stack.config.yaml")
    returncall = call("cfn-lint out/testt-deployer-core-stack.yaml", shell=True)
    assert returncall == 0
    result = runner.invoke(
        cli,
        [
            "deploy",
            "service",
            "--deployer",
            "testt",
            "--dryrun",
            "--output-location",
            "out/",
        ],
    )
    assert result.exit_code == 0
    assert os.path.isfile("out/testt-deployer-service-stack.config.yaml")
    assert os.path.isfile("out/testt-deployer-service-stack.yaml")
    returncall = call("cfn-lint out/testt-deployer-service-stack.yaml", shell=True)
    assert returncall == 0


def test_create_others(deployer, config):
    os.environ["FREELDEP_CONFIG"] = CONFIG_SAMPLE
    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "create",
            "subscription",
            "test",
            "--emails",
            "test@gmial.com",
            "--deployer",
            "testt",
            "--dryrun",
            "--output-location",
            "out/",
        ],
    )
    assert result.exit_code == 0
    assert os.path.isfile("out/testt-deployer-test-subscription.config.yaml")
    assert os.path.isfile("out/testt-deployer-test-subscription.yaml")
    returncall = call("cfn-lint out/testt-deployer-test-subscription.yaml", shell=True)
    assert returncall == 0
    depl = load_deployer(config, "testt")
    assert "testt-deployer-test" in depl["subscriptions"]
    result = runner.invoke(
        cli,
        [
            "create",
            "repository",
            "--deployer",
            "testt",
            "--dryrun",
            "--output-location",
            "out/",
        ],
    )
    assert result.exit_code == 0
    assert os.path.isfile("out/testt-deployer-repository-stack.config.yaml")
    assert os.path.isfile("out/testt-deployer-repository-stack.yaml")
    returncall = call("cfn-lint out/testt-deployer-repository-stack.yaml", shell=True)
    assert returncall == 0
    result = runner.invoke(
        cli,
        [
            "create",
            "project",
            "test",
            "--deployer",
            "testt",
            "--dryrun",
            "--output-location",
            "out/",
        ],
    )
    assert result.exit_code == 0
    assert os.path.isfile("out/testt-deployer-project-test.config.yaml")
    assert os.path.isfile("out/testt-deployer-project-test.yaml")
    returncall = call("cfn-lint out/testt-deployer-project-test.yaml", shell=True)
    assert returncall == 0
    depl = load_deployer(config, "testt")
    assert "test" in depl["projects"]
