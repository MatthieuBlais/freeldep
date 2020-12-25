import os

from click.testing import CliRunner

from freeldep.main import cli


CONFIG_SAMPLE = "./tests/data/config.ini"


def test_create_stack_missing_deployer(deployer, config):
    os.environ["FREELDEP_CONFIG"] = CONFIG_SAMPLE
    os.environ["AWS_PROFILE"] = "pytest"
    os.environ["AWS_DEFAULT_REGION"] = "ap-southeast-1"
    os.environ["PYTEST"] = "true"
    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "deploy",
            "core",
            "--deployer",
            "missing",
            "--dryrun",
            "--output-location",
            "out/",
        ],
    )
    assert result.exit_code != 0
    os.environ["AWS_PROFILE"] = "pytest"
    result = runner.invoke(
        cli,
        [
            "deploy",
            "service",
            "--deployer",
            "missing",
            "--dryrun",
            "--output-location",
            "out/",
        ],
    )
    assert result.exit_code != 0


def test_deploy_project_errors():
    os.environ["FREELDEP_CONFIG"] = CONFIG_SAMPLE
    os.environ["AWS_PROFILE"] = "pytest"
    os.environ["AWS_DEFAULT_REGION"] = "ap-southeast-1"
    os.environ["PYTEST"] = "true"
    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "deploy",
            "project",
            "--deployer",
            "testt",
            "--project",
            "missing",
            "--stack-file",
            "examples/config.yaml",
            "--dryrun",
            "--output-location",
            "out/",
        ],
    )
    assert result.exit_code != 0
    os.environ["FREELDEP_CONFIG"] = CONFIG_SAMPLE
    os.environ["AWS_PROFILE"] = "pytest"
    os.environ["AWS_DEFAULT_REGION"] = "ap-southeast-1"
    os.environ["PYTEST"] = "true"
    result = runner.invoke(
        cli,
        [
            "deploy",
            "project",
            "--project",
            "missing",
            "--stack-file",
            "examples/config.yaml",
            "--dryrun",
            "--output-location",
            "out/",
        ],
    )
    assert result.exit_code != 0


def test_deploy_project_without_core():
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
            "testwithoutcore",
            "--cloud",
            "AWS",
            "--dryrun",
            "--output-location",
            "out/",
        ],
    )
    assert result.exit_code == 0
    os.environ["FREELDEP_CONFIG"] = CONFIG_SAMPLE
    os.environ["AWS_PROFILE"] = "pytest"
    os.environ["AWS_DEFAULT_REGION"] = "ap-southeast-1"
    os.environ["PYTEST"] = "true"
    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "deploy",
            "project",
            "--deployer",
            "testwithoutcore",
            "--project",
            "test",
            "--stack-file",
            "examples/config.yaml",
            "--dryrun",
            "--output-location",
            "out/",
        ],
    )
    assert result.exit_code != 0
    os.environ["AWS_PROFILE"] = "pytest"
    result = runner.invoke(
        cli,
        ["cleanup", "deployer", "testwithoutcore", "--confirm"],
    )
    assert result.exit_code == 0


def test_create_others_with_errors(deployer, config, aws_credentials):
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
            "testingerrors",
            "--cloud",
            "AWS",
            "--dryrun",
            "--output-location",
            "out/",
        ],
    )
    assert result.exit_code == 0
    os.environ["AWS_PROFILE"] = "pytest"
    result = runner.invoke(
        cli,
        [
            "create",
            "subscription",
            "test",
            "--emails",
            "test@gmial.com",
            "--deployer",
            "doesntexist",
            "--dryrun",
            "--output-location",
            "out/",
        ],
    )
    assert result.exit_code != 0
    os.environ["AWS_PROFILE"] = "pytest"
    result = runner.invoke(
        cli,
        [
            "create",
            "subscription",
            "test",
            "--emails",
            "dfsdfdssdf",
            "--deployer",
            "testingerrors",
            "--dryrun",
            "--output-location",
            "out/",
        ],
    )
    assert result.exit_code != 0
    os.environ["AWS_PROFILE"] = "pytest"
    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "create",
            "project",
            "testproj",
            "--deployer",
            "sdfsdfsdfds",
            "--dryrun",
            "--output-location",
            "out/",
        ],
    )
    assert result.exit_code != 0
    os.environ["AWS_PROFILE"] = "pytest"
    result = runner.invoke(
        cli,
        [
            "create",
            "project",
            "testproj",
            "--deployer",
            "testingerrors",
            "--dryrun",
            "--output-location",
            "out/",
        ],
    )
    assert result.exit_code != 0
    os.environ["AWS_PROFILE"] = "pytest"
    result = runner.invoke(
        cli,
        ["cleanup", "deployer", "testingerrors", "--confirm"],
    )
    assert result.exit_code == 0
    os.environ["AWS_PROFILE"] = "pytest"
    result = runner.invoke(
        cli,
        [
            "create",
            "deployer",
            "testingerrorstwo",
            "--cloud",
            "GCP",
            "--dryrun",
            "--output-location",
            "out/",
        ],
    )
    assert result.exit_code == 0
    os.environ["AWS_PROFILE"] = "pytest"
    result = runner.invoke(
        cli,
        [
            "create",
            "subscription",
            "test",
            "--emails",
            "dfsdfdssdf",
            "--deployer",
            "testingerrorstwo",
            "--dryrun",
            "--output-location",
            "out/",
        ],
    )
    assert result.exit_code != 0
    os.environ["AWS_PROFILE"] = "pytest"
    result = runner.invoke(
        cli,
        ["cleanup", "deployer", "testingerrorstwo", "--confirm"],
    )
    assert result.exit_code == 0


def test_create_repository_error(deployer, config, aws_credentials):
    os.environ["FREELDEP_CONFIG"] = CONFIG_SAMPLE
    os.environ["AWS_PROFILE"] = "pytest"
    os.environ["AWS_DEFAULT_REGION"] = "ap-southeast-1"
    os.environ["PYTEST"] = "true"
    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "create",
            "repository",
            "--deployer",
            "doesntwsief",
            "--dryrun",
            "--output-location",
            "out/",
        ],
    )
    assert result.exit_code != 0
