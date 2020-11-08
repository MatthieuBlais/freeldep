import json
import os

import boto3

codebuild = boto3.client("codebuild")


def handler(event, context):

    print(json.dumps(event))

    codebuild.start_build(
        projectName=os.environ["PROJECT_NAME"],
        sourceTypeOverride="CODECOMMIT",
        sourceLocationOverride=(
            f"https://git-codecommit.{event['region']}.amazonaws.com/v1/repos/"
            f"{event['detail']['repositoryName']}"
        ),
        gitCloneDepthOverride=1,
        sourceVersion=event["detail"]["commitId"],
    )

    return event
