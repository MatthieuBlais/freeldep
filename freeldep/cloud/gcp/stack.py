import json
import os
import subprocess

import yaml
from google.cloud import storage  # pylint: disable=import-error

from freeldep.cloud.gcp.validate import DeploymentManagerValidation
from freeldep.cloud.stack import CloudStack


class DeploymentManagerTemplate(CloudStack):
    """Deployment Template: Read template, Inject parameters, Build functions and upload"""

    def __init__(self, config, deployer):
        super().__init__(config, deployer)
        DeploymentManagerValidation.validate_config(config)

    def _format_config(self):
        conf = {
            "GcpZone": self.config["gcp"]["zone"],
            "GcpProject": self.config["gcp"]["project"],
            "GcpAccount": self.config["gcp"]["account-id"],
        }
        for param, val in self.config["template"].items():
            conf["".join(x.title() for x in param.split("-"))] = val
        if "parameters" in self.config["template"]:
            for param, val in self.config["template"]["parameters"].items():
                conf["".join(x.title() for x in param.split("-"))] = val
        return conf

    def validate_template(self):
        """Validate template: How to do with GCP? #TODO"""
        if self.render_template is None:
            self.render_template()
        pass

    def deploy(self, wait=False, dryrun=False, output_folder=None):
        """Package Functions, deploy template"""
        self.package_functions(dryrun=dryrun, output_folder=output_folder)
        return self.deploy_template(dryrun=dryrun, output_folder=output_folder)

    def package_functions(self, dryrun=False, output_folder=None, gs_client=None):
        """Package Function into a zip file and upload to GS"""
        gs = storage.Client() if gs_client is None else gs_client
        bucket = gs.bucket(self.deployer["artifact"])
        for function in self.config["functions"]:
            filename = (
                function["filename"]
                if output_folder is None
                else output_folder + function["filename"]
            )
            self._compress_folder(function["location"], filename)
            key = self.config["template"][function["template-attribute"]]
            if not dryrun:
                self._upload_object(bucket, key, open(filename, "rb").read())
                os.remove(filename)

    def deploy_template(self, dryrun=False, output_folder=None):
        """Deploy template"""
        template, gcloud_commands = self._parse_template_commands()
        if template != "":
            template_name = self.config["template"]["name"]
            filename = (
                template_name
                if output_folder is None
                else output_folder + template_name
            )
            self._write_txt(template, filename + ".yaml")
            if dryrun:
                return
            status = self._get_deployment_status(template_name)
            action = "update" if status == "DONE" else "create"
            if not self._gcp_deploy(action, template_name, filename + ".yaml"):
                return False
        if len(gcloud_commands) > 0:
            for com in gcloud_commands:
                if not self._gcp_execute(com):
                    return False
        return True

    def cleanup(self, wait=True, dryrun=False, output_folder=None):
        """Delete existing stack"""
        template_name = self.config["template"]["name"]
        if self._get_deployment_status(template_name) != "DONE":
            return False, "Stack does not exist"
        if dryrun:
            return True
        return self._gcp_cleanup(template_name)

    def trigger_deployment(self, dryrun=False, output_folder=None):
        action = self.config.get("action", "create_or_update_stack").upper()
        if action == "DELETE_STACK":
            self.cleanup(dryrun=dryrun, output_folder=output_folder)
        else:
            success = self.deploy(self, dryrun=dryrun, output_folder=output_folder)
            if not success:
                if self.config.get("cleanup", False):
                    self.cleanup(dryrun=dryrun, output_folder=output_folder)
                raise RuntimeError("Deployment failed")

    def _parse_template_commands(self):
        parsed_template = yaml.safe_load(self.rendered_template)
        template = parsed_template.get("template", "")
        if template != "":
            template = yaml.dump(template)
        return template, parsed_template.get("gcloud", [])

    def _upload_object(self, bucket, key, content):
        """Upload object to GS"""
        bucket.blob(key).upload_from_string(content)

    def _get_deployment_status(self, template_name):
        """Get a deployment status
        :param deployment_name: name of the deployment stack
        """
        try:
            deployment = subprocess.check_output(
                [
                    "gcloud",
                    "deployment-manager",
                    "deployments",
                    "describe",
                    template_name,
                    "--format",
                    "json",
                ],
                stderr=subprocess.DEVNULL,
            )
            deployment = json.loads(deployment)
            return deployment["deployment"]["operation"]["status"]
        except subprocess.CalledProcessError:
            return "FAILED"

    def _gcp_deploy(self, command, template_name, template_path):
        try:
            subprocess.check_output(
                [
                    "gcloud",
                    "deployment-manager",
                    "deployments",
                    command,
                    template_name,
                    "--config",
                    template_path,
                ]
            )
            return True
        except subprocess.CalledProcessError:
            return False

    def _gcp_cleanup(self, template_name):
        """Delete a template
        :param template_name: name of the deployment
        """
        try:
            subprocess.check_output(
                [
                    "gcloud",
                    "deployment-manager",
                    "deployments",
                    "delete",
                    template_name,
                    "--quiet",
                ]
            )
            return True
        except subprocess.CalledProcessError:
            return False

    def _gcp_execute(self, command):
        """Get a deployment status
        :param deployment_name: name of the deployment stack
        """
        try:
            subprocess.check_output(command.split(" "))
            return True
        except subprocess.CalledProcessError:
            return False
