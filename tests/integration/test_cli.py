import json
import os
from subprocess import call

from click.testing import CliRunner

from freeldep.main import cli
from freeldep.modules.utils import delete_deployer
from freeldep.modules.utils import load_deployer
from freeldep.modules.utils import save_deployer


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
    os.environ["AWS_PROFILE"] = "pytest"
    os.environ["AWS_DEFAULT_REGION"] = "ap-southeast-1"
    os.environ["PYTEST"] = "true"
    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "create",
            "deployer",
            "testt",
            "--cloud",
            "AWS",
            "--dryrun",
            "--output-location",
            "out/",
        ],
    )
    assert result.exit_code == 0
    assert os.path.isfile("out/testt-deployer-initialization-stack.config.yaml")
    assert os.path.isfile("out/testt-deployer-initialization-stack.yaml")
    returncall = call(
        "cfn-lint out/testt-deployer-initialization-stack.yaml", shell=True
    )
    assert returncall == 0
    os.environ["AWS_PROFILE"] = "pytest"
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
    os.environ["AWS_PROFILE"] = "pytest"
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
    os.environ["AWS_PROFILE"] = "pytest"
    result = runner.invoke(
        cli,
        [
            "deploy",
            "project",
            "--deployer",
            "testt",
            "--project",
            "mytest",
            "--stack-file",
            "examples/config.yaml",
            "--dryrun",
            "--output-location",
            "out/",
        ],
    )
    assert result.exit_code == 0
    os.environ[
        "CODEBUILD_SOURCE_REPO_URL"
    ] = "https://git-codecommit.ap-southeast-1.amazonaws.com/v1/repos/de-testproj"
    os.environ["ARTIFACTS_BUCKET"] = "testbucket"
    os.environ["DEPLOYER_STATE_MACHINE_ARN"] = "mytestworkiflow"
    os.environ["AWS_PROFILE"] = "pytest"
    result = runner.invoke(
        cli,
        [
            "deploy",
            "project",
            "--deployer",
            "testt",
            "--project",
            "de-testproj",
            "--stack-file",
            "examples/config.yaml",
            "--dryrun",
            "--output-location",
            "out/",
        ],
    )
    assert result.exit_code == 0


def test_create_others(deployer, config, aws_credentials):
    os.environ["FREELDEP_CONFIG"] = CONFIG_SAMPLE
    os.environ["AWS_PROFILE"] = "pytest"
    os.environ["AWS_DEFAULT_REGION"] = "ap-southeast-1"
    os.environ["PYTEST"] = "true"
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
    os.environ["AWS_PROFILE"] = "pytest"
    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "create",
            "project",
            "testproj",
            "--deployer",
            "testt",
            "--dryrun",
            "--output-location",
            "out/",
        ],
    )
    assert returncall == 0
    assert result.exit_code == 0
    assert os.path.isfile("out/testt-deployer-project-testproj.config.yaml")
    assert os.path.isfile("out/testt-deployer-project-testproj.yaml")
    returncall = call("cfn-lint out/testt-deployer-project-testproj.yaml", shell=True)
    assert returncall == 0
    os.environ["AWS_PROFILE"] = "pytest"
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


def test_cleanup_others(deployer, config):
    os.environ["FREELDEP_CONFIG"] = CONFIG_SAMPLE
    os.environ["AWS_PROFILE"] = "pytest"
    os.environ["AWS_DEFAULT_REGION"] = "ap-southeast-1"
    os.environ["PYTEST"] = "true"
    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "cleanup",
            "subscription",
            "testt-deployer-test",
            "--deployer",
            "testt",
            "--dryrun",
        ],
    )
    assert result.exit_code == 0
    depl = load_deployer(config, "testt")
    assert "testt-deployer-test" not in depl["subscriptions"]
    os.environ["AWS_PROFILE"] = "pytest"
    result = runner.invoke(
        cli,
        ["cleanup", "subscription", "asdasdsda", "--deployer", "testt", "--dryrun"],
    )
    assert result.exit_code != 0
    os.environ["AWS_PROFILE"] = "pytest"
    result = runner.invoke(
        cli,
        ["cleanup", "subscription", "asdasdsda", "--deployer", "asdasdasd", "--dryrun"],
    )
    assert result.exit_code != 0
    os.environ["AWS_PROFILE"] = "pytest"
    result = runner.invoke(
        cli,
        ["cleanup", "project", "testproj", "--deployer", "testt", "--dryrun"],
    )
    assert result.exit_code == 0
    depl = load_deployer(config, "testt")
    assert "project" not in depl or "testproj" not in depl["project"]
    os.environ["AWS_PROFILE"] = "pytest"
    result = runner.invoke(
        cli,
        ["cleanup", "project", "asdasdasd", "--deployer", "jhghgjghj", "--dryrun"],
    )
    assert result.exit_code != 0
    os.environ["AWS_PROFILE"] = "pytest"
    result = runner.invoke(
        cli,
        ["cleanup", "repository", "--deployer", "testt", "--dryrun"],
    )
    assert result.exit_code == 0
    depl = load_deployer(config, "testt")
    print(depl)
    assert "repository" not in depl
    os.environ["AWS_PROFILE"] = "pytest"
    result = runner.invoke(
        cli,
        ["cleanup", "repository", "--deployer", "asdasdasd", "--dryrun"],
    )
    assert result.exit_code != 0


def test_cleanup():
    os.environ["FREELDEP_CONFIG"] = CONFIG_SAMPLE
    os.environ["AWS_PROFILE"] = "pytest"
    os.environ["AWS_DEFAULT_REGION"] = "ap-southeast-1"
    os.environ["PYTEST"] = "true"
    runner = CliRunner()
    os.environ["CODEBUILD_SOURCE_REPO_URL"] = ""
    os.environ["AWS_PROFILE"] = "pytest"
    result = runner.invoke(
        cli,
        ["cleanup", "core", "--deployer", "testt", "--dryrun"],
    )
    assert result.exit_code == 0
    os.environ["AWS_PROFILE"] = "pytest"
    result = runner.invoke(
        cli,
        ["cleanup", "service", "--deployer", "testt", "--dryrun"],
    )
    assert result.exit_code == 0
    os.environ["AWS_PROFILE"] = "pytest"
    result = runner.invoke(
        cli,
        ["cleanup", "deployer", "dsadasd", "--confirm"],
    )
    assert result.exit_code != 0
    os.environ["AWS_PROFILE"] = "pytest"
    result = runner.invoke(
        cli,
        ["cleanup", "deployer", "testt"],
    )
    assert result.exit_code != 0
    os.environ["AWS_PROFILE"] = "pytest"
    result = runner.invoke(
        cli,
        ["cleanup", "deployer", "testt", "--confirm"],
    )
    assert result.exit_code == 0
    os.environ["AWS_PROFILE"] = "pytest"
    result = runner.invoke(
        cli,
        ["cleanup", "core", "--deployer", "testt", "--dryrun"],
    )
    assert result.exit_code != 0
    os.environ["AWS_PROFILE"] = "pytest"
    result = runner.invoke(
        cli,
        ["cleanup", "service", "--deployer", "testt", "--dryrun"],
    )
    assert result.exit_code != 0
