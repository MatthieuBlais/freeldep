import click

from freeldep.cloud import Compiler
from freeldep.modules.utils import delete_deployer
from freeldep.modules.utils import load_deployer
from freeldep.modules.utils import save_deployer
from freeldep.templates import CoreDeployerTemplate
from freeldep.templates import DeployerRepositoryTemplate
from freeldep.templates import ProjectTemplate
from freeldep.templates import ServiceDeployerTemplate
from freeldep.templates import SubscriptionDeployerTemplate


@click.group()
@click.pass_obj
def cleanup(ctx):
    """Delete CFN stacks"""
    pass


# PROJECT
# REPO


@cleanup.command()
@click.option("--deployer", required=True, help="Name of your deployer")
@click.option("--wait/--no-wait", default=False, help="Wait for cleanup completion")
@click.option(
    "--dryrun/--no-dryrun",
    default=False,
    help="If enable, does not really create a resource",
)
@click.pass_context
def core(ctx, deployer, wait, dryrun):
    """Deploy core step function"""
    ctx.obj.require_cloud_access()
    config = ctx.obj.config
    deployer = load_deployer(config, deployer)
    if deployer is None:
        raise click.BadParameter(f"Deployer {deployer} does not exist")
    Compiler.cleanup(
        deployer, CoreDeployerTemplate.get(deployer, config), wait=wait, dryrun=dryrun
    )
    del deployer["deployment-workflow"]
    save_deployer(deployer, config)


@cleanup.command()
@click.option("--deployer", required=True, help="Name of your deployer")
@click.option("--wait/--no-wait", default=False, help="Wait for cleanup completion")
@click.option(
    "--dryrun/--no-dryrun",
    default=False,
    help="If enable, does not really create a resource",
)
@click.pass_context
def service(ctx, deployer, wait, dryrun):
    """Deploy core step function"""
    ctx.obj.require_cloud_access()
    config = ctx.obj.config
    deployer = load_deployer(config, deployer)
    if deployer is None:
        raise click.BadParameter(f"Deployer {deployer} does not exist")

    Compiler.cleanup(
        deployer,
        ServiceDeployerTemplate.get(deployer, config),
        wait=wait,
        dryrun=dryrun,
    )
    del deployer["codebuild-service"]
    del deployer["service-trigger"]
    del deployer["service-role"]
    save_deployer(deployer, config)


@cleanup.command()
@click.argument("name")
@click.option("--deployer", required=True, help="Name of your deployer")
@click.option("--wait/--no-wait", default=False, help="Wait for cleanup completion")
@click.option(
    "--dryrun/--no-dryrun",
    default=False,
    help="If enable, does not really create a resource",
)
@click.pass_context
def subscription(ctx, name, deployer, wait, dryrun):
    """Deploy core step function"""
    ctx.obj.require_cloud_access()
    config = ctx.obj.config
    deployer = load_deployer(config, deployer)
    if deployer is None:
        raise click.BadParameter(f"Deployer {deployer} does not exist")
    if "subscriptions" not in deployer or name not in deployer["subscriptions"]:
        raise click.BadParameter(f"Subscription {name} does not exists")
    Compiler.cleanup(
        deployer,
        SubscriptionDeployerTemplate.get(name, [], deployer, config),
        wait=wait,
        dryrun=dryrun,
    )
    deployer["subscriptions"] = [x for x in deployer["subscriptions"] if x != name]
    save_deployer(deployer, config)


@cleanup.command()
@click.argument("name")
@click.option("--deployer", required=True, help="Name of your deployer")
@click.option("--wait/--no-wait", default=True, help="Wait for cleanup completion")
@click.option(
    "--dryrun/--no-dryrun",
    default=False,
    help="If enable, does not really create a resource",
)
@click.pass_context
def project(ctx, name, deployer, wait, dryrun):
    """Remove the CICD integration from existing project. Does not delete the repository."""
    ctx.obj.require_cloud_access()
    config = ctx.obj.config
    deployer = load_deployer(config, deployer)
    if deployer is None:
        raise click.BadParameter(f"Deployer {deployer} does not exist")
    template = ProjectTemplate.get(name, "", deployer, config)
    template[0]["template"]["parameters"]["cleanup"] = "true"
    Compiler.cleanup(deployer, template, wait=wait, dryrun=dryrun)


@cleanup.command()
@click.option("--deployer", required=True, help="Name of your deployer")
@click.option("--wait/--no-wait", default=True, help="Wait for cleanup completion")
@click.option(
    "--dryrun/--no-dryrun",
    default=False,
    help="If enable, does not really create a resource",
)
@click.pass_context
def repository(ctx, deployer, wait, dryrun):
    """Remove the CICD integration of your deployer repository. Does not delete the repository"""
    ctx.obj.require_cloud_access()
    config = ctx.obj.config
    deployer = load_deployer(config, deployer)
    if deployer is None:
        raise click.BadParameter(f"Deployer {deployer} does not exist")
    template = DeployerRepositoryTemplate.get(deployer, config)
    template[0]["template"]["parameters"]["cleanup"] = "true"
    Compiler.cleanup(deployer, template, wait=wait, dryrun=dryrun)
    del deployer["repository"]
    save_deployer(deployer, config)


@cleanup.command()
@click.argument("name")
@click.option(
    "--confirm/--no-confirm",
    default=False,
    help="Confirm you want to delete your configuration file",
)
@click.pass_context
def deployer(ctx, name, confirm):
    """Delete deployer configuration. Does not delete the repository"""
    config = ctx.obj.config
    deployer = load_deployer(config, name)
    if deployer is None:
        raise click.BadParameter(f"Deployer {name} does not exist")
    if confirm:
        delete_deployer(config, name)
    else:
        raise click.UsageError(
            "Add the flag --confirm to confirm you want to delete your deployer"
        )
