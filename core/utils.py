import os

from cloud.aws.client import AWSClients
from cloud.aws.deployer import CloudFormation
from cloud.aws.subscription import SNS


class Clients:
    @classmethod
    def get(cls):
        if os.environ.get("AWS_LAMBDA_FUNCTION_NAME", ""):
            return AWSClients()
        raise NotImplementedError("utils.Clients")


class Deployer:
    @classmethod
    def get(cls, clients):
        if os.environ.get("AWS_LAMBDA_FUNCTION_NAME", ""):
            return CloudFormation(clients)
        raise NotImplementedError("utils.Clients")


class Subscription:
    @classmethod
    def publish(cls, clients, topic, subject, message):
        if os.environ.get("AWS_LAMBDA_FUNCTION_NAME", ""):
            return SNS.publish(clients, topic, subject, message)
        raise NotImplementedError("utils.Subscription")


class BadInputException(Exception):
    def __init__(self, message):
        super().__init__(message)


class InternalErrorException(Exception):
    def __init__(self, message):
        super().__init__(message)


class BadTemplateException(Exception):
    def __init__(self, message):
        super().__init__(message)
