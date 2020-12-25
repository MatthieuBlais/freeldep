import json

from utils import Clients
from utils import Deployer

clients = Clients.get()

CREATE_ACTIONS = ["UPDATE_STACK", "CREATE_OR_UPDATE_STACK", "CREATE_STACK"]
DELETE_ACTIONS = ["DELETE_STACK"]


def set_status(success):
    return "SUCCESS" if success and type(success) is bool else "FAIL"


def create_handler(cfn, event):
    status = cfn.status(event["TemplateName"])
    if status in cfn.CREATE_COMPLETE:
        event["Status"] = set_status(success=True)
    elif status in cfn.DEPLOY_FAILED:
        event["Status"] = set_status(success=False)
    else:
        event["Status"] = status


def delete_handler(deployer, event):
    if deployer.exists(event["TemplateName"]):
        status = deployer.status(event["TemplateName"])
        if status in deployer.DELETE_COMPLETE:
            event["Status"] = set_status(success=True)
        if status in deployer.DEPLOY_FAILED:
            event["Status"] = set_status(success=False)
        event["Status"] = status
    else:
        event["Status"] = set_status(success=True)


def handler(event, context):

    print(json.dumps(event, indent=4))

    deployer = Deployer.get(clients)

    if event["Action"] in CREATE_ACTIONS:
        create_handler(deployer, event)
    elif event["Action"] in DELETE_ACTIONS:
        delete_handler(deployer, event)

    return event
