import json
import re
from random import randint

import click

from freeldep.cloud import Compiler
from freeldep.modules.utils import load_deployer
from freeldep.modules.utils import save_deployer
from freeldep.modules.utils import shorten_expr
from freeldep.modules.utils import valid_expr
from freeldep.templates import DeployerRepositoryTemplate
from freeldep.templates import InitializeDeployerTemplate
from freeldep.templates import ProjectTemplate
from freeldep.templates import SubscriptionDeployerTemplate


@click.group()
@click.pass_obj
def create(ctx):
    """Create new deployer"""
    pass


@create.command()
@click.argument("name")
@click.option(
    "--cloud",
    required=True,
    type=click.Choice(["AWS", "GCP"], case_sensitive=False),
    help="AWS or GCP cloud deployment",
)
@click.option(
    "--artifact-bucket",
    default=None,
    help="A bucket to store deployment artifacts will be automatically created using your"
    "deployer name. Use this option to overwrite default name.",
)
@click.option(
    "--registry-table",
    default=None,
    help="A registry table will be created to monitor deployment. Use this option to "
    "overwrite default name. Available for AWS only",
)
@click.option("--wait/--no-wait", default=True, help="Wait for cleanup completion")
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
def deployer(
    ctx, name, cloud, artifact_bucket, registry_table, wait, dryrun, output_location
):
    """Create artifact bucket and registry table. Initialize your deployer"""
    ctx.obj.require_cloud_access()
    cloud = cloud.upper()

    name = validate_name(name)
    artifact_bucket = validate_bucket(name, artifact_bucket)
    registry_table = validate_registry(name, registry_table) if cloud == "AWS" else None

    deployer = {
        "name": name,
        "cloud": cloud,
        "artifact": artifact_bucket,
        "registry": registry_table,
    }
    click.echo(json.dumps(deployer))

    config = ctx.obj.config
    Compiler.build_template(
        deployer,
        InitializeDeployerTemplate.get(cloud, deployer, config),
        cloud=cloud,
        wait=wait,
        dryrun=dryrun,
        output_folder=output_location,
    )

    save_deployer(deployer, config)


@create.command()
@click.argument("name")
@click.option("--deployer", required=True, help="Name of your deployer")
@click.option(
    "--emails",
    required=True,
    help="Comma delimited list of email addresses to send failed deployment notifications to",
)
@click.option("--wait/--no-wait", default=True, help="Wait for cleanup completion")
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
def subscription(ctx, name, deployer, emails, wait, dryrun, output_location):
    """Create a subscription and subscribe email addresses to it"""
    ctx.obj.require_cloud_access()
    config = ctx.obj.config
    deployer = load_deployer(config, deployer)
    if deployer is None:
        raise click.BadParameter(f"Deployer {deployer} does not exist")
    if deployer.get("cloud", "").upper() == "GCP":
        raise RuntimeError("Subscriptions are not available for GCP")

    name = validate_name(name)
    emails = validate_emails(emails)
    if len(emails) == 0:
        raise click.BadParameter("There is no valid email address")

    Compiler.build_template(
        deployer,
        SubscriptionDeployerTemplate.get(name, emails, deployer, config),
        wait=wait,
        dryrun=dryrun,
        output_folder=output_location,
    )

    if "subscriptions" not in deployer:
        deployer["subscriptions"] = []
    deployer["subscriptions"].append(f"{deployer['name']}-deployer-{name}")

    save_deployer(deployer, config)


@create.command()
@click.option("--deployer", required=True, help="Name of your deployer")
@click.option("--wait/--no-wait", default=True, help="Wait for cleanup completion")
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
def repository(ctx, deployer, wait, dryrun, output_location):
    """Create a repository with CI/CD to update core functionalities of your deployer"""
    ctx.obj.require_cloud_access()
    config = ctx.obj.config
    deployer = load_deployer(config, deployer)
    if deployer is None:
        raise click.BadParameter(f"Deployer {deployer} does not exist")

    Compiler.build_template(
        deployer,
        DeployerRepositoryTemplate.get(deployer, config),
        wait=wait,
        dryrun=dryrun,
        output_folder=output_location,
    )

    deployer["repository"] = f"{deployer['name']}-deployer"

    save_deployer(deployer, config)


@create.command()
@click.argument("name")
@click.option("--deployer", required=True, help="Name of your deployer")
@click.option(
    "--branches", default="master,staging,dev", help="Branches triggering builds"
)
@click.option("--wait/--no-wait", default=True, help="Wait for cleanup completion")
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
def project(ctx, name, deployer, branches, wait, dryrun, output_location):
    """Create a new repository with CI/CD using a deployer"""
    ctx.obj.require_cloud_access()
    config = ctx.obj.config
    deployer = load_deployer(config, deployer)
    if deployer is None:
        raise click.BadParameter(f"Deployer {deployer} does not exist")

    name = validate_name(name)
    branches = branches.strip()
    if "service-trigger" not in deployer or "service-role" not in deployer:
        raise click.UsageError("Create a deployer service to be able to create project")

    Compiler.build_template(
        deployer,
        ProjectTemplate.get(name, branches, deployer, config),
        wait=wait,
        dryrun=dryrun,
        output_folder=output_location,
    )

    if "projects" not in deployer:
        deployer["projects"] = []
    deployer["projects"].append(name)

    save_deployer(deployer, config)


def validate_name(name):
    valid_expr("Name", name, "^[A-Za-z-]*$")
    return shorten_expr(name, 30).lower()


def validate_bucket(deployer_name, bucket):
    if bucket:
        valid_expr("Artifact bucket", bucket, "^[A-Za-z-]*$")
        return bucket
    else:
        return (
            deployer_name + "-deployer-artifact-bucket-" + str(randint(100000, 999999))
        )


def validate_registry(deployer_name, registry):
    if registry:
        valid_expr("Registry table", registry, "^[A-Za-z0-9-]*$")
        return shorten_expr(registry, 100).lower()
    else:
        return deployer_name + "-deployer-deployment-registry"


def validate_emails(emails):
    emails = emails.split(",")
    regex = r"^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,6}$"
    out = []
    for email in emails:
        if re.search(regex, email):
            out.append(email)
    return out
