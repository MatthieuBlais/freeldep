import uuid

import boto3


class AWSClients:
    def __init__(self, assume_role_arn=""):
        self.s3 = boto3.client("s3")
        self.sns = boto3.client("sns")
        if assume_role_arn:
            sts = boto3.client("sts")
            role = sts.assume_role(
                RoleArn=assume_role_arn,
                RoleSessionName=uuid.uuid1().hex,
            )
            self.cloudformation = boto3.client(
                "cloudformation",
                aws_access_key_id=role["Credentials"]["AccessKeyId"],
                aws_secret_access_key=role["Credentials"]["SecretAccessKey"],
                aws_session_token=role["Credentials"]["SessionToken"],
            )
        else:
            self.cloudformation = boto3.client("cloudformation")
