import os
import subprocess
import uuid


class CfnStackValidation:
    @classmethod
    def validate_config(cls, config):
        """Validate section of the stack config"""
        if "aws" not in config:
            raise KeyError("aws is required in a stack definition")
        else:
            cls._validate_aws_config(config["aws"])

        if "location" not in config:
            raise KeyError("location is required in a stack definition")
        elif not cls._file_exists(os.path.expanduser(config["location"])):
            raise FileNotFoundError(f"Template {config['location']} does not exist")

        if "template" not in config:
            raise KeyError("template is required in a stack definition")
        else:
            cls._validate_template_config(config["template"])

        if "functions" in config:
            cls._validate_lambda_config(config["functions"])

    @classmethod
    def validate_stack(cls, template, tmp_location=f"/tmp/{uuid.uuid1().hex}.yaml"):
        """Validate CFN stack with CFNLINT"""
        with open(tmp_location, "w+") as f:
            f.write(template)
        try:
            subprocess.check_output(
                f"cfn-lint {tmp_location}".split(" "), stderr=subprocess.STDOUT
            )
        except subprocess.CalledProcessError:
            raise RuntimeError("Your CFN stack is not valid")
        os.remove(tmp_location)

    @classmethod
    def _validate_aws_config(cls, config):
        """Validate section of the stack config"""
        if type(config) != dict:
            raise ValueError("aws must be a dict")
        if "region" not in config:
            raise KeyError("aws.region is required in stack definition")
        if "account-id" not in config:
            raise KeyError("aws.account-id is required in stack definition")
        if type(config["region"]) != str:
            raise ValueError("aws.region must be a string")
        if (
            type(config["account-id"]) != str
            or len(str(config["account-id"])) != 12
            or len([x for x in config["account-id"] if not x.isdigit()])
        ):
            raise ValueError("aws.account-id must be a 12 digit string")

    @classmethod
    def _validate_template_config(cls, config):
        """Validate section of the stack config"""
        if type(config) != dict:
            raise ValueError("template must be a dict")
        if "name" not in config:
            raise KeyError("template.name is required in stack definition")
        if type(config["name"]) != str:
            raise ValueError("template.name must be a string")
        if "parameters" in config and type(config["parameters"]) != dict:
            raise ValueError("template.parameters must be a dict")

    @classmethod
    def _validate_lambda_config(cls, config):
        """Validate section of the stack config"""
        for lambd in config:
            if "name" not in lambd:
                raise KeyError("Lambdas must have a name")
            if "location" not in lambd:
                raise KeyError("Lambdas must have a location")
            if "template-attribute" not in lambd:
                raise KeyError("Lambdas must have a template-attribute")
            if "bucket" not in lambd:
                raise KeyError("Lambdas must have a artifact bucket location")
            if (
                type(lambd["name"]) != str
                or type(lambd["template-attribute"]) != str
                or type(lambd["bucket"]) != str
            ):
                raise ValueError(
                    "One of these parameters is not a string: name, template-attribute, bucket"
                )
            if not os.path.isdir(lambd["location"]):
                raise ValueError("Lambda package is not found")

    @classmethod
    def _file_exists(cls, file_path):
        """Check if a file exists"""
        return os.path.exists(os.path.expanduser(file_path))
