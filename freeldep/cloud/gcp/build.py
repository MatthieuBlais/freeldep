import os


class CloudBuildHelper:
    @classmethod
    def is_cloudrun(cls):
        return (
            os.environ.get("PROJECT_ID", "") != ""
            and os.environ.get("BUILD_ID", "") != ""
        )

    @classmethod
    def get_project(cls):
        return os.environ["REPO_NAME"]

    @classmethod
    def get_branch(cls):
        return os.environ["BRANCH_NAME"]
