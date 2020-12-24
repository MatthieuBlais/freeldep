import os
import uuid
import zipfile
from datetime import datetime

import yaml
from jinja2 import Template  # pylint: disable=import-error


class CloudStack(object):
    def __init__(self, config, deployer):
        self.config = config
        self.deployer = deployer
        self.template = None
        self.rendered_template = None

        if "functions" not in self.config:
            self.config["functions"] = []

        if "gcloud" not in self.config:
            self.config["gcloud"] = []

    def read_template(self):
        """Import template"""
        with open(self.config["location"], "r") as stream:
            self.template = stream.read()

    def prepare_packages(self):
        """Prepare Function packages and update stack parameters"""
        for idx, function in enumerate(self.config["functions"]):
            uname = datetime.now().strftime(
                function["name"] + "_" + "%Y%m%d_%H%M_" + uuid.uuid1().hex + ".zip"
            )
            self.config["template"][function["template-attribute"]] = (
                self.config["template"][function["template-attribute"]] + uname
            )
            self.config["functions"][idx]["filename"] = uname
            self.config["functions"][idx]["key"] = self.config["template"][
                function["template-attribute"]
            ]

    def render_template(self):
        """Inject Jinja parameters into template"""
        template_properties = self._format_config()
        if self.template is None:
            self.read_template()
        tm = Template(self.template)
        self.rendered_template = tm.render(**template_properties)

    def _compress_folder(self, location, filename):
        """Compress a folder"""
        rootlen = len(location)
        zipf = zipfile.ZipFile(filename, "w", zipfile.ZIP_DEFLATED)
        for root, _, files in os.walk(location):
            for f in files:
                fn = os.path.join(root, f)
                zipf.write(fn, fn[rootlen:])
        zipf.close()
        return filename

    def _write_yaml(self, obj, filename):
        """Write a YAML file"""
        with open(filename, "w+") as stream:
            yaml.dump(obj, stream)

    def _write_txt(self, obj, filename):
        """Write a TXT file"""
        with open(filename, "w+") as stream:
            stream.write(obj)

    def validate_template(self):
        raise NotImplementedError("cli.cloud.stack.validate_template()")

    def deploy(self, wait=False, dryrun=False, output_folder=None):
        raise NotImplementedError("cli.cloud.stack.deploy()")

    def package_functions(self, dryrun=False, output_folder=None, gs_client=None):
        raise NotImplementedError("cli.cloud.stack.package_functions()")

    def deploy_template(self, dryrun=False, output_folder=None):
        raise NotImplementedError("cli.cloud.stack.deploy_template()")

    def cleanup(self, wait=True, dryrun=False, output_folder=None):
        raise NotImplementedError("cli.cloud.stack.cleanup()")

    def trigger_deployment(self, dryrun=False, output_folder=None):
        raise NotImplementedError("cli.cloud.stack.trigger_deployment()")

    def _format_config(self):
        raise NotImplementedError("cli.cloud.stack._format_config()")
