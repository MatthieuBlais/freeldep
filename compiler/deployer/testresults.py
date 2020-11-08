import json
import os

import boto3
import cfnlint.core
from utils import BadTemplateException  # pylint: disable=import-error

s3 = boto3.client("s3", region_name=os.environ["AWS_REGION"])


def parse_s3_url(s3_url):
    url = s3_url.split("/")
    bucket = url[2]
    template_key = "/".join(url[3:])
    return bucket, ".".join(template_key.split(".")[:-1]) + "_test/output.json"


def download_results(s3, bucket, key):
    try:
        obj = s3.get_object(Bucket=bucket, Key=key)
        return json.load(obj["Body"])
    except Exception:
        raise


def run_checks(template_name):
    template = cfnlint.decode.cfn_yaml.load(template_name)
    cfnlint.core.configure_logging(None)
    rules = cfnlint.core.get_rules([], [], [], [], False, [])
    return cfnlint.core.run_checks(
        template_name, template, rules, [os.environ["AWS_REGION"]]
    )


def handler(event, context):

    print(json.dumps(event, indent=4))

    bucket, key = parse_s3_url(event["TemplateLocation"])

    test_results = download_results(s3, bucket, key)

    event["Valid"] = test_results["Success"]
    if not test_results["Success"]:
        event["Error"] = {
            "Code": "BadTemplateException",
            "Cause": (
                f"Template didn't pass the tests. "
                f"Download full report here: {test_results['TestOutputLocation']}"
            ),
        }
        raise BadTemplateException(json.dumps(event["Error"]))

    return event
