import json

import boto3

SNS_ERROR_SUBJECT = "[TemplateDeployerError] - A template failed to deploy"
SNS_ERROR_MESSAGE = "This templates hasn't been deployed:\n\n"

sns = boto3.client("sns")


def notify(sns_arn, message):
    sns.publish(
        TopicArn=sns_arn, Subject=SNS_ERROR_SUBJECT, Message=SNS_ERROR_MESSAGE + message
    )
    return


def handler(event, context):

    print(json.dumps(event, indent=4))

    if "NotifyOnFailure" in event and event["NotifyOnFailure"] != "":
        notify(event["NotifyOnFailure"], json.dumps(event, indent=4))
    else:
        print("No notification")

    return event
