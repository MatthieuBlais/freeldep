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

def handler(event, context):

    print(json.dumps(event))

    cfn = CloudFormation(cloudformation, None)
    status = cfn.status(event['TemplateName'])

    if status == 'ROLLBACK_COMPLETE':
        cfn.delete_stack(event['TemplateName'])

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
