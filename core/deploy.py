import json

from utils import BadInputException
from utils import Clients
from utils import Deployer
from utils import InternalErrorException

clients = Clients.get()

REQUIRED_EVENT_PARAMS = ["TemplateName", "TemplateLocation", "Action", "Parameters"]


def valid_event(event):
    """Confirm all required parameters are available"""
    return len(REQUIRED_EVENT_PARAMS) == len(
        [x for x in event if x in REQUIRED_EVENT_PARAMS]
    )


def get_error_message(event):
    return f"""Template deployer failed: {json.dumps(event)}"""


def handler(event, context):
    """Create CFN stack"""

    print(json.dumps(event))

    if not valid_event(event):
        raise BadInputException("Event is not valid")

    deployer = Deployer.get(clients)
    success = deployer.deploy(
        event["TemplateName"],
        event["TemplateLocation"],
        event["Parameters"],
        event["Action"],
    )

    if not success:
        err = get_error_message(event)
        event["Error"] = {"Code": "InternalError", "Cause": err}
        raise InternalErrorException(err)

    return event
