import json
import logging
import os
import time
import uuid
from datetime import datetime

import boto3
import botocore
import yaml

from freeldep.cloud.aws.status import StackStatus
from freeldep.cloud.aws.validate import CfnStackValidation
from freeldep.cloud.stack import CloudStack


class CfnStack(CloudStack):
    """CFN Stack: Read template, Inject parameters, Build lambdas and upload"""

    def __init__(self, config, deployer):
        super().__init__(config, deployer)
        CfnStackValidation.validate_config(config)

    def validate_template(self):
        """Validate CFN template with CFNLINT"""
        if self.render_template is None:
            self.render_template()
        CfnStackValidation.validate_stack(self.rendered_template)

    def deploy(self, wait=False, dryrun=False, output_folder=None):
        """Package Lambda functions, deploy CFN template and wait if needed"""
        self.package_lambdas(dryrun=dryrun, output_folder=output_folder)
        self.create_stack(dryrun=dryrun, output_folder=output_folder)
        if wait and not dryrun:
            self.wait_completion(wait)

    def package_lambdas(self, dryrun=False, output_folder=None, s3_client=None):
        """Package Lambda function into a zip file and upload to S3"""
        s3 = self._boto_client("s3", s3_client)
        bucket = self.deployer["artifact"]
        for lambd in self.config["functions"]:
            filename = (
                lambd["filename"]
                if output_folder is None
                else output_folder + lambd["filename"]
            )
            self._compress_folder(lambd["location"], filename)
            key = self.config["template"][lambd["template-attribute"]]
            if not dryrun:
                self._upload_object(s3, bucket, key, open(filename, "rb").read())
                os.remove(filename)

    def create_stack(
        self, dryrun=False, output_folder=None, cloudformation_client=None
    ):
        """Deploy CFN template"""
        cfn_parameters = self._format_template_parameters(
            self.config["template"].get("parameters", {})
        )
        cloudformation = self._boto_client("cloudformation", cloudformation_client)
        cfn_name = self.config["template"]["name"]
        if dryrun:
            filename = cfn_name if output_folder is None else output_folder + cfn_name
            self._write_txt(self.rendered_template, filename + ".yaml")
            self._write_yaml(cfn_parameters, filename + ".config.yaml")
            return
        try:
            _ = cloudformation.describe_stacks(StackName=cfn_name)
            cloudformation.update_stack(
                StackName=cfn_name,
                TemplateBody=self.rendered_template,
                Capabilities=["CAPABILITY_IAM", "CAPABILITY_NAMED_IAM"],
                Parameters=cfn_parameters,
            )
            return True
        except botocore.exceptions.ClientError as error:
            if (
                error.response["Error"]["Code"] == "ValidationError"
                and error.response["Error"]["Message"]
                == "No updates are to be performed."
            ):
                logging.error(error.response["Error"]["Message"])
                return False
            if (
                error.response["Error"]["Code"] == "ValidationError"
                and error.response["Error"]["Message"]
                == f"Stack with id {cfn_name} does not exist"
            ):
                cloudformation.create_stack(
                    StackName=cfn_name,
                    TemplateBody=self.rendered_template,
                    Capabilities=["CAPABILITY_IAM", "CAPABILITY_NAMED_IAM"],
                    Parameters=cfn_parameters,
                )
                return True
            raise

    def wait_completion(self, wait, cloudformation_client=None):
        """Wait for a stack to be deployed"""
        waiting = wait
        cloudformation = self._boto_client("cloudformation", cloudformation_client)
        while waiting:
            stack = cloudformation.describe_stacks(
                StackName=self.config["template"]["name"]
            )
            status = stack["Stacks"][0]["StackStatus"]
            if StackStatus.success(status):
                logging.info(f"Status: {status}")
                waiting = False
            elif StackStatus.failed(status):
                raise RuntimeError(f"Status: {status}")
            time.sleep(10)
            logging.info(f"Checking status of stack {self.config['template']['name']}")

    def cleanup(
        self, wait, dryrun=False, output_folder=None, cloudformation_client=None
    ):
        """Delete existing stack"""
        waiting = wait
        cloudformation = self._boto_client("cloudformation", cloudformation_client)
        stack_name = self.config["template"]["name"]
        if not self._stack_exists(cloudformation, stack_name):
            return False, "Stack does not exist"
        if dryrun:
            return True
        cloudformation.delete_stack(StackName=stack_name)
        while waiting:
            try:
                stack = cloudformation.describe_stacks(StackName=stack_name)
                status = stack["Stacks"][0]["StackStatus"]
                if StackStatus.success(status):
                    logging.info(f"Status: {status}")
                    waiting = False
                elif StackStatus.failed(status):
                    raise RuntimeError(f"Status: {status}")
                time.sleep(10)
                logging.info(f"Checking status of stack {stack_name}")
            except Exception:
                return True

    def trigger_deployment(self, dryrun=False, output_folder=None):
        if (
            "artifact" not in self.deployer
            or "deployment-workflow-id" not in self.deployer
        ):
            raise RuntimeError("No deployment workflow")
        if not dryrun:
            template_location = self._upload_template()
            sfn = self._boto_client("stepfunctions")
            execution_id = self.config["template"]["name"] + "-" + uuid.uuid1().hex
            sfn.start_execution(
                stateMachineArn=self.deployer["deployment-workflow-id"],
                name=execution_id,
                input=json.dumps(
                    {
                        "TemplateName": self.config["template"]["name"],
                        "DeploymentTimestamp": str(int(time.time())),
                        "TemplateLocation": template_location,
                        "Action": self.config.get(
                            "action", "create_or_update_stack"
                        ).upper(),
                        "Test": self._configure_tests(template_location),
                        "Valid": True,
                        "KeepFailed": self.config.get("cleanup", False),
                        "NotifyOnFailure": self.config.get("subscription", ""),
                        "Parameters": {
                            "".join([x.title() for x in key.split("-")]): val
                            for key, val in self.config["template"]
                            .get("parameters", {})
                            .items()
                        },
                    }
                ),
            )

    def _format_template_parameters(self, parameters):
        """Format parmeters camel case"""
        return [
            {
                "ParameterKey": "".join([x.title() for x in key.split("-")]),
                "ParameterValue": val,
            }
            for key, val in parameters.items()
        ]

    def _format_config(self):
        conf = {
            "AwsRegion": self.config["aws"]["region"],
            "AwsAccountId": self.config["aws"]["account-id"],
        }
        if "deployment-role" in self.config["aws"]:
            conf["AwsDeploymentRole"] = self.config["aws"]["deployment-role"]
        for param, val in self.config["template"].items():
            conf["".join(x.title() for x in param.split("-"))] = val
        if "parameters" in self.config["template"]:
            for param, val in self.config["template"]["parameters"].items():
                conf["".join(x.title() for x in param.split("-"))] = val
        return conf

    def _boto_client(self, service, client=None):
        """Assume deployment role if any, else get client"""
        if os.environ.get("PYTEST", ""):
            if os.environ.get("AWS_PROFILE", ""):
                del os.environ["AWS_PROFILE"]
            return boto3.client(
                service, aws_secret_access_key="NONE", aws_access_key_id="NONE"
            )
        if client:
            return client
        if self.config["aws"].get("deployment-role", ""):
            sts = boto3.client("sts", region_name=self.config["aws"]["region"])
            creds = sts.assume_role(
                RoleArn=self.config["aws"]["deployment-role"], RoleSessionName="tmp"
            )
            return boto3.client(
                service,
                aws_secret_access_key=creds["Credentials"]["SecretAccessKey"],
                aws_access_key_id=creds["Credentials"]["AccessKeyId"],
                aws_session_token=creds["Credentials"]["SessionToken"],
            )
        return boto3.client(service, region_name="ap-southeast-1")

    def _upload_object(self, s3, bucket, key, content):
        """Upload object to S3"""
        s3.put_object(Bucket=bucket, Key=key, Body=content)

    def _upload_template(self):
        """Upload a project CFN template to S3"""
        s3 = self._boto_client("s3")
        name = datetime.now().strftime("%Y%m%d_%H%M%S" + ".yaml")
        key = f"templates/{self.deployer['project']}/{self.config['template']['name']}/{name}"
        s3.put_object(
            Bucket=self.deployer["artifact"], Key=key, Body=self.rendered_template
        )
        return f"s3://{self.deployer['artifact']}/{key}"

    def _configure_tests(self, template_location):
        """Upload taskcat config file to artifact bucket"""
        if "test" not in self.config or not self._file_exists(self.config["test"]):
            return ""
        taskcat = self._read_yaml(self.config["test"])
        taskcat["project"]["s3_bucket"] = self.deployer["artifact"]
        taskcat["project"]["name"] = f"{self.deployer['project']}-tests"
        taskcat["tests"]["default"]["template"], key = template_location.split("/")[-1]
        s3 = self._boto_client("s3")
        s3.put_object(
            Bucket=self.deployer["artifact"], Key=key, Body=yaml.dump(taskcat)
        )
        return f"s3://{self.deployer['artifact']}/{key}"

    def _format_test_template_location(self, location):
        template = location.split("/")[-1]
        key = "/".join(location.split("/")[3:-1]) + "/_tests/" + location.split("/")[-1]
        return template, key

    def _file_exists(self, file_path):
        """Check if a file exists"""
        return os.path.exists(os.path.expanduser(file_path))

    def _read_yaml(self, filename):
        """Read a YAML file"""
        with open(filename, "r") as stream:
            return yaml.safe_load(stream)

    def _stack_exists(self, cloudformation, stack_name):
        """Check if a CFN stack exists or not"""
        try:
            cloudformation.describe_stacks(StackName=stack_name)
            return True
        except Exception:
            return False
