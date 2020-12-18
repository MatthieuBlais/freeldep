import json

from utils import Clients
from utils import Deployer

clients = Clients.get()


def handler(event, context):
    """Delete existing stack if rollback"""

    print(json.dumps(event))

    deployer = Deployer.get(clients)
    status = deployer.status(event["TemplateName"])

    if status == "ROLLBACK_COMPLETE":
        deployer.delete_stack(event["TemplateName"])

    return event
