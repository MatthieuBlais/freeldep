import botocore


class CloudFormation:
    """Deploys CloudFormation templates to AWS"""

    CREATE_COMPLETE = ["CREATE_COMPLETE", "UPDATE_COMPLETE"]
    DEPLOY_FAILED = [
        "DELETE_FAILED",
        "CREATE_FAILED",
        "ROLLBACK_COMPLETE",
        "UPDATE_ROLLBACK_COMPLETE",
    ]
    DELETE_COMPLETE = ["DELETE_COMPLETE"]

    def __init__(self, clients):
        self.cloudformation = clients.cloudformation
        self.s3 = clients.s3

    def deploy(self, stack_name, template_path, parameters, action):
        """Deploy or update a cloud formation template
        :param stack_name: name of the cfn stack
        :param template_path: s3 path to the Yaml template
        :param parameters: dictionary of parameters for the cfn stack
        """
        try:
            if (
                action == "UPDATE_STACK" or action == "CREATE_OR_UPDATE_STACK"
            ) and self.exists(stack_name):
                self._update_cfn_stack(stack_name, template_path, parameters)
            elif action == "CREATE_STACK" or action == "CREATE_OR_UPDATE_STACK":
                self._create_cfn_stack(stack_name, template_path, parameters)
            elif action == "DELETE_STACK":
                self.delete_stack(stack_name)
            return True
        except Exception:
            raise

    def delete_stack(self, stack_name):
        """Delete a cloudformation template
        :param stack_name: name of the cfn stack
        :param wait: bool, wait for stack to be completely removed.
        """
        try:
            if self.exists(stack_name):
                print(f"-> Deleting stack {stack_name}")
                self.cloudformation.delete_stack(StackName=stack_name)
                return True
        except Exception:
            raise

    def status(self, stack_name):
        """Get the status of a deployment
        :param stack_name: name of the cfn stack
        """
        try:
            return self._get_stack(stack_name)["StackStatus"]
        except Exception:
            raise

    def exists(self, stack_name):
        """Check if a cfn stack exists
        :param stack_name: name of the cfn stack
        """
        try:
            self.cloudformation.describe_stacks(StackName=stack_name)
            return True
        except Exception:
            return False

    def _create_cfn_stack(self, stack_name, template_path, parameters):
        """Create the cfn template using the aws client
        :param stack_name: name of the cfn stack
        :param template_path: path to the Yaml template
        :param parameters: dictionary of parameters for the cfn stack
        """
        try:
            print(f"-> Creating stack {stack_name}")
            self.cloudformation.create_stack(
                StackName=stack_name,
                TemplateBody=self._read_template(template_path),
                Capabilities=["CAPABILITY_IAM", "CAPABILITY_NAMED_IAM"],
                Parameters=[
                    {"ParameterKey": key, "ParameterValue": parameters[key]}
                    for key in parameters.keys()
                ],
            )
        except Exception:
            raise

    def _update_cfn_stack(self, stack_name, template_path, parameters):
        """Update a cfn template using aws client
        :param stack_name: name of the cfn stack
        :param template_path: path to the Yaml template
        :param parameters: dictionary of parameters for the cfn stack
        """
        try:
            print(f"-> Updating stack {stack_name}")
            self.cloudformation.update_stack(
                StackName=stack_name,
                TemplateBody=self._read_template(template_path),
                Capabilities=["CAPABILITY_IAM", "CAPABILITY_NAMED_IAM"],
                Parameters=[
                    {"ParameterKey": key, "ParameterValue": parameters[key]}
                    for key in parameters.keys()
                ],
            )
        except botocore.exceptions.ClientError as error:
            if (
                error.response["Error"]["Code"] == "ValidationError"
                and error.response["Error"]["Message"]
                == "No updates are to be performed."
            ):
                print(error.response["Error"]["Message"])
                return False

    def _get_stack(self, stack_name):
        """Get a cfn stack status
        :param stack_name: name of the cfn stack
        """
        try:
            response = self.cloudformation.describe_stacks(StackName=stack_name)
            return response["Stacks"][0]
        except Exception:
            raise

    def _read_template(self, template_path):
        bucket = template_path.split("/")[2]
        key = "/".join(template_path.split("/")[3:])
        try:
            return self.s3.get_object(Bucket=bucket, Key=key)["Body"].read().decode()
        except Exception:
            raise
