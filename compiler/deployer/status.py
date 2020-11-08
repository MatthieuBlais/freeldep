import boto3
import os
import uuid
import json
from utils import CloudFormation
from utils import BadInputException
from utils import InternalErrorException

CREATE_ACTIONS = ["UPDATE_STACK", "CREATE_OR_UPDATE_STACK", "CREATE_STACK"]
DELETE_ACTIONS = ['DELETE_STACK']

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

def set_status(success):
    return 'SUCCESS' if success else 'FAIL'

def handler(event, context):

    print(json.dumps(event, indent=4))

    cfn = CloudFormation(cloudformation, None)

    if event['Action'] in CREATE_ACTIONS:
        status = cfn.status(event['TemplateName'])
        if status in cfn.CREATE_COMPLETE:
            event['Status'] = set_status(success=True)
        elif status in cfn.DEPLOY_FAILED:
            event['Status'] = set_status(success=False)
        else:
            event['Status'] = status
    elif event['Action'] in DELETE_ACTIONS:
        if cfn.exists(event['TemplateName']):
            status = cfn.status(event['TemplateName'])
            if status in cfn.DELETE_COMPLETE:
                event['Status'] = set_status(success=True)
            if status in cfn.DEPLOY_FAILED:
                event['Status'] = set_status(success=False)
            event['Status'] = status
        else:
            event['Status'] = set_status(success=True)
    
    return event


if __name__ == "__main__":
    event = {
        "TemplateName": "smlf-dataengineering-cfn-deployer-service",
        "TemplateLocation": "s3://smlf-dataengineering-deployer-artifact-bucket//templates/smlf-dataengineering-cfn-deployer-service/20201102_1633_2518c3da1d2911eb89e30242ac110002.yaml",
        "Action": "CREATE_OR_UPDATE_STACK",
        "Parameters": {
            "DeployerCodebuildServiceName": "smlf-dataengineering-template-deployer-service",
            "DeployerArtifactBucket": "smlf-dataengineering-deployer-artifact-bucket",
            "DeployerStateArn": "arn:aws:states:ap-southeast-1:908177370303:stateMachine:smlf-dataengineering-cfn-deployer",
            "DeployerTriggerLambdaName": "smlf-dataengineering-deployer-trigger-service"
        }
    }
    print(handler(event, {}))
