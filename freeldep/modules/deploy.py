import os

import click

from freeldep.cloud import Compiler
from freeldep.cloud.aws.build import CodebuildHelper
from freeldep.modules.utils import execute_script
from freeldep.modules.utils import file_exists
from freeldep.modules.utils import get_workflow_id
from freeldep.modules.utils import load_deployer
from freeldep.modules.utils import read_yaml
from freeldep.modules.utils import save_deployer
from freeldep.templates import CoreDeployerTemplate
from freeldep.templates import ServiceDeployerTemplate


@click.group()
@click.pass_obj
def deploy(ctx):
    """Deploy deployer"""
    pass


@deploy.command()
@click.option("--deployer", required=True, help="Name of your deployer")
@click.option("--wait/--no-wait", default=True, help="Wait for completion")
@click.option(
    "--dryrun/--no-dryrun",
    default=False,
    help="If enable, does not really create a resource",
)
@click.option(
    "--output-location",
    default=None,
    help="If dryrun enable, save the artifacts to this location",
)
@click.pass_context
def core(ctx, deployer, wait, dryrun, output_location):
    """Deploy core step function"""
    ctx.obj.require_cloud_access()
    config = ctx.obj.config
    deployer = load_deployer(config, deployer)
    if deployer is None:
        raise click.BadParameter(f"Deployer {deployer} does not exist")
    Compiler.build_template(
        deployer,
        CoreDeployerTemplate.get(deployer, config),
        wait=wait,
        dryrun=dryrun,
        output_folder=output_location,
    )
    deployer["deployment-workflow"] = f"{deployer['name']}-deployer-core"
    deployer["account"] = config.get("aws", "account", None)
    save_deployer(deployer, config)


@deploy.command()
@click.option("--deployer", required=True, help="Name of your deployer")
@click.option("--wait/--no-wait", default=True, help="Wait for completion")
@click.option(
    "--dryrun/--no-dryrun",
    default=False,
    help="If enable, does not really create a resource",
)
@click.option(
    "--output-location",
    default=None,
    help="If dryrun enable, save the artifacts to this location",
)
@click.pass_context
def service(ctx, deployer, wait, dryrun, output_location):
    """Create a service for other codecommit repositories"""
    ctx.obj.require_cloud_access()
    config = ctx.obj.config
    deployer = load_deployer(config, deployer)
    if deployer is None:
        raise click.BadParameter(f"Deployer {deployer} does not exist")
    Compiler.build_template(
        deployer,
        ServiceDeployerTemplate.get(deployer, config),
        wait=wait,
        dryrun=dryrun,
        output_folder=output_location,
    )
    deployer["codebuild-service"] = f"{deployer['name']}-deployer-service"
    deployer["service-trigger"] = f"{deployer['name']}-deployer-service-trigger"
    deployer["service-role"] = f"{deployer['name']}-deployer-service-role"
    save_deployer(deployer, config)


@deploy.command()
@click.option("--deployer", default=None, help="Name of your deployer")
@click.option("--project", default=None, help="Project name")
@click.option("--stack-file", required=True, help="Path of your templates to deploy")
@click.option(
    "--package-script",
    default="./bin/package.sh",
    help="Bash script to execute before deploying",
)
@click.option(
    "--dryrun/--no-dryrun",
    default=False,
    help="If enable, does not really create a resource",
)
@click.option(
    "--output-location",
    default=None,
    help="If dryrun enable, save the artifacts to this location",
)
@click.pass_context
def project(
    ctx, deployer, project, stack_file, package_script, dryrun, output_location
):
    """Deploy a project build"""
    ctx.obj.require_cloud_access()
    config = ctx.obj.config
    if not CodebuildHelper.is_codebuild():
        if deployer is None:
            raise click.UsageError("You must specify a deployer")
        deployer = load_deployer(config, deployer)
        if deployer is None:
            raise click.BadParameter(f"Deployer {deployer} does not exist")
        if "deployment-workflow" not in deployer:
            raise click.UsageError("Your deployer doesn't have a deployment workflow")
        deployer["deployment-workflow-id"] = get_workflow_id(
            deployer["deployment-workflow"], config
        )
        deployer["project"] = project
    else:
        deployer = {
            "artifact": os.environ["ARTIFACTS_BUCKET"],
            "deployment-workflow-id": os.environ["DEPLOYER_STATE_MACHINE_ARN"],
            "project": CodebuildHelper.get_project(),
        }
    deploy_project(
        deployer, project, stack_file, package_script, dryrun, output_location
    )


def deploy_project(
    deployer,
    project,
    stack_file,
    package_script="./bin/package.sh",
    dryrun=False,
    output_location=None,
):
    if not file_exists(stack_file):
        raise FileNotFoundError("No stack to deploy")
    stacks = read_yaml(stack_file)

    if file_exists(package_script) and not execute_script(package_script):
        raise RuntimeError("Packge script failed")

    Compiler.trigger_deployment(
        deployer, stacks, dryrun=dryrun, output_folder=output_location
    )
