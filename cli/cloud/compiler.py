import json
import logging

from cli.cloud.aws.stack import CfnStack

AWS_CLOUD = "aws"
GCP_CLOUD = "gcp"


class Compiler:
    @classmethod
    def build_template(
        cls,
        deployer,
        templates,
        cloud=AWS_CLOUD,
        wait=True,
        dryrun=False,
        output_folder=None,
    ):

        for template in templates:
            logging.info(json.dumps(template, indent=4))
            stack = cls.get_stack(cloud, template, deployer)
            stack.read_template()
            stack.prepare_packages()
            stack.render_template()
            stack.validate_template()
            stack.deploy(wait=wait, dryrun=dryrun, output_folder=output_folder)

    @classmethod
    def cleanup(
        cls,
        deployer,
        templates,
        cloud=AWS_CLOUD,
        wait=True,
        dryrun=False,
        output_folder=None,
    ):
        for template in templates:
            logging.info(json.dumps(template, indent=4))
            stack = cls.get_stack(cloud, template, deployer)
            stack.cleanup(wait=wait, dryrun=dryrun, output_folder=output_folder)

    @classmethod
    def trigger_deployment(
        cls,
        deployer,
        templates,
        cloud=AWS_CLOUD,
        wait=True,
        dryrun=False,
        output_folder=None,
    ):
        for template in templates:
            logging.info(json.dumps(template, indent=4))
            stack = cls.get_stack(cloud, template, deployer)
            stack.read_template()
            stack.prepare_packages()
            stack.render_template()
            stack.validate_template()
            stack.trigger_deployment(dryrun=dryrun, output_folder=output_folder)

    @classmethod
    def get_stack(cls, cloud, template, deployer):
        if cloud == AWS_CLOUD:
            return CfnStack(template, deployer)
        return CfnStack(template, deployer)
