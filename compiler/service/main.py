from jinja2 import Template # pylint: disable=import-error
import yaml
import sys
import uuid
from datetime import datetime
import zipfile
import os
from os.path import basename
import boto3
import time
import botocore
import json

CONFIG_FILENAME = "./config.yaml"
COMPILED_TEMPLATE = "./bin/compiled-template.yaml"

s3 = boto3.client('s3')
sfn = boto3.client('stepfunctions')

def read_yaml(path):
    with open(path, 'r') as stream:
        return yaml.safe_load(stream)

def read_txt(path):
    with open(path, 'r') as stream:
        return stream.read()

def render(tmplt, properties):
    tm = Template(tmplt)
    return tm.render(**properties)

def package_lambda(local_path, filename):
    zipf = zipfile.ZipFile(filename, "w", zipfile.ZIP_DEFLATED)
    for root, _, files in os.walk(local_path):
        for f in files:
            zipf.write(os.path.join(root, f), basename(f))

def upload_package(bucket, key, filename):
    with open(filename, 'rb') as fin:
        s3.put_object(Bucket=bucket, Key=key, Body=fin.read())
    os.remove(filename)

def generate_lambda_key(lambdas, properties):
    for i in range(len(lambdas)):
        uname = datetime.now().strftime(lambdas[i]['name']+'_'+"%Y%m%d_%H%M_"+uuid.uuid1().hex+".zip")
        properties[lambdas[i]['template-attribute']] = properties[lambdas[i]['template-attribute']] + uname
        lambdas[i]['filename'] = uname
        lambdas[i]['key'] = properties[lambdas[i]['template-attribute']]
    return properties, lambdas

def upload_template(template_name, template):
    name = datetime.now().strftime("%Y%m%d_%H%M_"+uuid.uuid1().hex+".yaml")
    key = f"/templates/{template_name}/{name}"
    s3.put_object(Bucket=os.environ['ARTIFACTS_BUCKET'], Key=key, Body=template)
    return f"s3://{os.environ['ARTIFACTS_BUCKET']}/{key}"

def trigger_deploy(stack_name, template_location, action, parameters={}):
    execution_id = stack_name + "-" + uuid.uuid1().hex
    sfn.start_execution(
        stateMachineArn=os.environ['DEPLOYER_STATE_MACHINE_ARN'],
        name=execution_id,
        input=json.dumps({
            "TemplateName": stack_name,
            "TemplateLocation": template_location,
            "Action": action.upper(),
            "Parameters": {
                "".join([x.title() for x in key.split('-')]): val for key, val in parameters.items()
            }
        })
    )
    return execution_id
    
    



if __name__ == "__main__":
    
    print(f"Reading config file: {CONFIG_FILENAME}")
    config = read_yaml(CONFIG_FILENAME)

    for stack in config:
        template = read_txt(stack['location'])

        parameters, lambdas = generate_lambda_key(stack['lambdas'], stack['template'])

        properties = {
            "AwsRegion": stack['aws']['region'],
            "AwsAccountId": stack['aws']['account-id'],
        }
        if 'deployment-role' in stack['aws']:
            properties['AwsDeploymentRole'] = stack['aws']['deployment-role']
        for param, val in parameters.items():
            properties["".join(x.title() for x in param.split("-"))] = val

        print(f"Generating template: {stack['location']}")
        template = render(template, properties)
        template_location = upload_template(parameters['name'], template)

        print(f"Packaging Lambdas")
        for lam in lambdas:
            package_lambda(lam['location'],  lam['filename'])
            upload_package(lam['bucket'], lam['key'], lam['filename'])

        print(f"Triggering deployment: {parameters['name']}")
        exec_id = trigger_deploy(parameters['name'], template_location, stack['action'], parameters['parameters'])
        print(f"Execution id: {exec_id}")