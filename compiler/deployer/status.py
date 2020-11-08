import json
import os
import uuid

import boto3
from utils import CloudFormation  # pylint: disable=import-error

CREATE_ACTIONS = ["UPDATE_STACK", "CREATE_OR_UPDATE_STACK", "CREATE_STACK"]
DELETE_ACTIONS = ["DELETE_STACK"]

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


def set_status(success):
    return "SUCCESS" if success else "FAIL"


def handler(event, context):

    print(json.dumps(event, indent=4))

    cfn = CloudFormation(cloudformation, None)

    if event["Action"] in CREATE_ACTIONS:
        status = cfn.status(event["TemplateName"])
        if status in cfn.CREATE_COMPLETE:
            event["Status"] = set_status(success=True)
        elif status in cfn.DEPLOY_FAILED:
            event["Status"] = set_status(success=False)
        else:
            event["Status"] = status
    elif event["Action"] in DELETE_ACTIONS:
        if cfn.exists(event["TemplateName"]):
            status = cfn.status(event["TemplateName"])
            if status in cfn.DELETE_COMPLETE:
                event["Status"] = set_status(success=True)
            if status in cfn.DEPLOY_FAILED:
                event["Status"] = set_status(success=False)
            event["Status"] = status
        else:
            event["Status"] = set_status(success=True)

    return event
