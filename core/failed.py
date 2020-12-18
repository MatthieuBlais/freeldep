import json

from utils import Clients
from utils import Subscription

clients = Clients()

ERROR_SUBJECT = "[TemplateDeployerError] - A template failed to deploy"
ERROR_MESSAGE = "This templates hasn't been deployed:\n\n"


def notify(topic, message):
    Subscription.publish(clients, topic, ERROR_SUBJECT, ERROR_MESSAGE + message)
    return


def handler(event, context):

    print(json.dumps(event, indent=4))

    if event.get("NotifyOnFailure", "") != "":
        notify(event["NotifyOnFailure"], json.dumps(event, indent=4))
    else:
        print("No notification")

    return event
