import boto3
import os
import uuid
import json
from utils import CloudFormation
from utils import BadInputException
from utils import InternalErrorException

SNS_ERROR_SUBJECT = "[TemplateDeployerError] - A template failed to deploy"
SNS_ERROR_MESSAGE = "This templates hasn't been deployed:\n\n"

sns = boto3.client('sns')

def notify(sns_arn, message):
    sns.publish(
        TopicArn=sns_arn,
        Subject=SNS_ERROR_SUBJECT,
        Message=SNS_ERROR_MESSAGE+message
    )
    return

def handler(event, context):

    print(json.dumps(event, indent=4))

    if 'NotifyOnFailure' in event and event['NotifyOnFailure'] != '':
        notify(event['NotifyOnFailure'], json.dumps(event, indent=4))
    else:
        print('No notification')

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
