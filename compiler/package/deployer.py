import boto3
import os
import uuid
import json
from utils import CloudFormation
from utils import BadInputException
from utils import InternalErrorException

if "ASSUME_ROLE_ARN" in os.environ:
    sts = boto3.client('sts')
    role = sts.assume_role(
        RoleArn=os.environ['ASSUME_ROLE_ARN'],
        RoleSessionName=uuid.uuid1().hex,
    )
    cloudformation = boto3.client(
        'cloudformation', 
        aws_access_key_id=role['Credentials']['AccessKeyId'],
        aws_secret_access_key=role['Credentials']['SecretAccessKey'],
        aws_session_token=role['Credentials']['SessionToken']
    )
else:
    cloudformation = boto3.client('cloudformation')

s3 = boto3.client('s3')

def valid_deploy_event(event):
    if 'TemplateName' not in event:
        return False
    if 'TemplateLocation' not in event:
        return False
    if 'Action' not in event:
        return False
    if 'Parameters' not in event:
        return False
    return True

def get_error_message(event):
    return f"""Template deployer failed: {json.dumps(event)}"""

def deploy_template(event, context):

    print(json.dumps(event))

    if not valid_deploy_event(event):
        raise BadInputException('Event is not valid')

    cfn = CloudFormation(cloudformation, s3)
    success = cfn.deploy(event['TemplateName'], event['TemplateLocation'], event['Parameters'], event['Action'])

    if not success:
        raise InternalErrorException('Template not being deployed')

    event["ErrorMessage"] = get_error_message(event)

    return event


def status_template(event, context):

    cfn = CloudFormation(cloudformation, s3)

    if event['Action'] in ["UPDATE_STACK", "CREATE_OR_UPDATE_STACK", "CREATE_STACK"]:
        status = cfn.status(event['TemplateName'])
        if status in ['CREATE_COMPLETE', 'UPDATE_COMPLETE']:
            event['Status'] = 'SUCCESS'
        elif status in ['CREATE_FAILED', 'ROLLBACK_COMPLETE', 'UPDATE_ROLLBACK_COMPLETE']:
            event['Status'] = 'FAIL'
        else:
            event['Status'] = status
    else:
        if cfn.exists(event['TemplateName']):
            status = cfn.status(event['TemplateName'])
            if status in ['DELETE_COMPLETE']:
                event['Status'] = 'SUCCESS'
            if status in ['DELETE_FAILED', 'ROLLBACK_COMPLETE', 'UPDATE_ROLLBACK_COMPLETE']:
                event['Status'] = 'FAIL'
            event['Status'] = status
        else:
            event['Status'] = 'SUCCESS'
    
    print(json.dumps(event))

    return event


if __name__ == "__main__":
    event = {
        "TemplateName": 'dummy-test',
        "TemplateLocation": 's3://smlf-dataengineers-artifact-bucket/dummy.yaml',
        "Action": "DELETE_STACK",
        "Parameters": {
            "DummyParameter": "test"
        }
    }
    print(status_template(event, {}))
