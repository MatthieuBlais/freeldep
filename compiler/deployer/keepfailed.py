import json
import os
import uuid

import boto3
from utils import CloudFormation  # pylint: disable=import-error

if "ASSUME_ROLE_ARN" in os.environ:
    sts = boto3.client("sts")
    role = sts.assume_role(
        RoleArn=os.environ["ASSUME_ROLE_ARN"],
        RoleSessionName=uuid.uuid1().hex,
    )
    cloudformation = boto3.client(
        "cloudformation",
        aws_access_key_id=role["Credentials"]["AccessKeyId"],
        aws_secret_access_key=role["Credentials"]["SecretAccessKey"],
        aws_session_token=role["Credentials"]["SessionToken"],
    )
else:
    cloudformation = boto3.client("cloudformation")


def handler(event, context):

    print(json.dumps(event))

    cfn = CloudFormation(cloudformation, None)
    status = cfn.status(event["TemplateName"])

    if status == "ROLLBACK_COMPLETE":
        cfn.delete_stack(event["TemplateName"])

    return event
