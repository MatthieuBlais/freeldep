import json
import os
import uuid

import boto3
from utils import BadInputException  # pylint: disable=import-error
from utils import CloudFormation  # pylint: disable=import-error
from utils import InternalErrorException  # pylint: disable=import-error

REQUIRED_EVENT_PARAMS = ["TemplateName", "TemplateLocation", "Action", "Parameters"]

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

s3 = boto3.client("s3")


def valid_event(event):
    return len(REQUIRED_EVENT_PARAMS) == [
        x for x in event if x in REQUIRED_EVENT_PARAMS
    ]


def get_error_message(event):
    return f"""Template deployer failed: {json.dumps(event)}"""


def handler(event, context):

    print(json.dumps(event))

    if not valid_event(event):
        raise BadInputException("Event is not valid")

    cfn = CloudFormation(cloudformation, s3)
    success = cfn.deploy(
        event["TemplateName"],
        event["TemplateLocation"],
        event["Parameters"],
        event["Action"],
    )

    if not success:
        err = get_error_message(event)
        event["Error"] = {"Code": "InternalError", "Cause": err}
        raise InternalErrorException(err)

    return event
