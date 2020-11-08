import json
import cfnlint.core
import boto3
import yaml
import uuid
import os
from utils import BadTemplateException

s3 = boto3.client("s3", region_name=os.environ['AWS_REGION'])

def parse_s3_url(s3_url):
    url = s3_url.split("/")
    return url[2], "/".join(url[3:])

def download_template(s3, bucket, key):
    try:
        filename = f"/tmp/{uuid.uuid1().hex}.yaml"
        s3.download_file(bucket, key, filename)
        return filename
    except Exception:
        raise

def run_checks(template_name):
    template = cfnlint.decode.cfn_yaml.load(template_name)
    cfnlint.core.configure_logging(None)
    rules = cfnlint.core.get_rules([], [], [], [], False, [])
    return cfnlint.core.run_checks(
        template_name,
        template,
        rules,
        [os.environ['AWS_REGION']]
    )

def handler(event, context):

    print(json.dumps(event, indent=4))

    bucket, key = parse_s3_url(event['TemplateLocation'])
    filename = download_template(s3, bucket, key)
    checks = run_checks(filename)

    event["Valid"] = len(checks) == 0
    if len(checks) > 0:
        for err in checks:
            print(err)
        event["Error"] = {
            "Code": "BadTemplateException",
            "Cause": checks
        }
        raise BadTemplateException(json.dumps(event["Error"]))
    
    return event


if __name__ == "__main__":
    event = {
        "TemplateName": "smlf-dataengineering-cfn-deployer-service",
        "TemplateLocation": "s3://smlf-dataengineering-deployer-artifact-bucket//templates/smlf-dataengineering-cfn-deployer-service/20201102_1633_2518c3da1d2911eb89e30242ac110002.yaml",
        "Action": "CREATE_OR_UPDATE_STACK",
        "Test": False,
        "NotifyOnFailure": "",
        "Parameters": {
            "DeployerCodebuildServiceName": "smlf-dataengineering-template-deployer-service",
            "DeployerArtifactBucket": "smlf-dataengineering-deployer-artifact-bucket",
            "DeployerStateArn": "arn:aws:states:ap-southeast-1:908177370303:stateMachine:smlf-dataengineering-cfn-deployer",
            "DeployerTriggerLambdaName": "smlf-dataengineering-deployer-trigger-service"
        }
    }
    handler(event, {})