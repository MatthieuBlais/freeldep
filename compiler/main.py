import os
import uuid
import zipfile
from datetime import datetime
from os.path import basename

import boto3
import botocore
import yaml
from jinja2 import Template  # pylint: disable=import-error

CONFIG_FILENAME = "config.yaml"
COMPILED_TEMPLATE = "compiled-template.yaml"

s3 = boto3.client("s3")
cloudformation = boto3.client("cloudformation")


def read_yaml(path):
    with open(path, "r") as stream:
        return yaml.safe_load(stream)


def read_txt(path):
    with open(path, "r") as stream:
        return stream.read()


def render(tmplt, properties):
    tm = Template(tmplt)
    return tm.render(**properties)


def package_lambda(local_path, filename):
    zipf = zipfile.ZipFile(filename, "w", zipfile.ZIP_DEFLATED)
    for root, _, files in os.walk(local_path):
        for f in files:
            zipf.write(os.path.join(root, f), basename(f))


def upload_package(bucket, key, filename):
    with open(filename, "rb") as fin:
        s3.put_object(Bucket=bucket, Key=key, Body=fin.read())
    os.remove(filename)


def generate_lambda_key(lambdas, properties):
    for i in range(len(lambdas)):
        uname = datetime.now().strftime(
            lambdas[i]["name"] + "_" + "%Y%m%d_%H%M_" + uuid.uuid1().hex + ".zip"
        )
        properties[lambdas[i]["template-attribute"]] = (
            properties[lambdas[i]["template-attribute"]] + uname
        )
        lambdas[i]["filename"] = uname
        lambdas[i]["key"] = properties[lambdas[i]["template-attribute"]]
    return properties, lambdas


def create_stack(stack_name, template, parameters={}):
    parameters = [
        {
            "ParameterKey": "".join([x.title() for x in key.split("-")]),
            "ParameterValue": val,
        }
        for key, val in parameters.items()
    ]
    try:
        _ = cloudformation.describe_stacks(StackName=stack_name)
        cloudformation.update_stack(
            StackName=stack_name,
            TemplateBody=template,
            Capabilities=["CAPABILITY_IAM", "CAPABILITY_NAMED_IAM"],
            Parameters=parameters,
        )
        return True
    except botocore.exceptions.ClientError as error:
        if (
            error.response["Error"]["Code"] == "ValidationError"
            and error.response["Error"]["Message"] == "No updates are to be performed."
        ):
            print(error.response["Error"]["Message"])
            return False
        if (
            error.response["Error"]["Code"] == "ValidationError"
            and error.response["Error"]["Message"]
            == f"Stack with id {stack_name} does not exist"
        ):
            cloudformation.create_stack(
                StackName=stack_name,
                TemplateBody=template,
                Capabilities=["CAPABILITY_IAM", "CAPABILITY_NAMED_IAM"],
                Parameters=parameters,
            )
            return True
        raise


if __name__ == "__main__":

    print(f"Reading config file: {CONFIG_FILENAME}")
    config = read_yaml(CONFIG_FILENAME)

    for stack in config:
        template = read_txt(stack["location"])

        parameters, lambdas = generate_lambda_key(stack["lambdas"], stack["template"])

        properties = {
            "AwsRegion": stack["aws"]["region"],
            "AwsAccountId": stack["aws"]["account-id"],
        }
        if "deployment-role" in stack["aws"]:
            properties["AwsDeploymentRole"] = stack["aws"]["deployment-role"]
        for param, val in parameters.items():
            properties["".join(x.title() for x in param.split("-"))] = val

        print(f"Generating template: {stack['location']}")
        template = render(template, properties)
        # with open(COMPILED_TEMPLATE, "w+") as f:
        #     f.write(template)

        print("Packaging Lambdas")
        for lam in lambdas:
            package_lambda(lam["location"], lam["filename"])
            upload_package(lam["bucket"], lam["key"], lam["filename"])

        print(f"Triggering deployment: {parameters['name']}")
        success = create_stack(parameters["name"], template, parameters["parameters"])

        if success:
            print("Done: check cfn for deployment monitoring")
