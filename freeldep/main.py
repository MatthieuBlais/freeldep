import logging

import click

from freeldep.config import ConfigParser
from freeldep.modules import cleanup
from freeldep.modules import create
from freeldep.modules import deploy
from freeldep.modules import show


class Cli(object):
    def __init__(self, aws_profile=None, verbose=0, config_file="./cli/config.ini"):
        logging.basicConfig(
            format="%(asctime)s - %(message)s", level=self._get_logging_level(verbose)
        )
        self.config = ConfigParser(config_file)
        self.name = self.config.get("cli", "name", "Freeldep")
        self.version = self.config.get("cli", "version")
        self.description = self.config.get("cli", "description")
        self.aws_profile = aws_profile

    def require_cloud_access(self):
        if self.aws_profile is None:
            raise RuntimeError("Please set AWS_PROFILE to deploy resources")

    def _get_logging_level(self, verbose):
        if verbose < 1:
            return logging.WARNING
        if verbose == 1:
            return logging.INFO
        return logging.DEBUG


@click.group()
@click.option("--aws-profile", envvar="AWS_PROFILE", default=None)
@click.option("-v", "--verbose", count=True, default=0)
@click.option("--config-file", envvar="FREELDEP_CONFIG", default="./cli/config.ini")
@click.pass_context
def cli(ctx, aws_profile, verbose, config_file):
    """Infrastructure as Code deployment CLI"""
    ctx.obj = Cli(aws_profile, verbose, config_file)


@cli.command()
@click.pass_context
def version(ctx):
    click.echo(f"{ctx.obj.name} CLI")
    click.echo(f"Version: {ctx.obj.version}")


cli.add_command(create.create)
cli.add_command(show.show)
cli.add_command(deploy.deploy)
cli.add_command(cleanup.cleanup)
