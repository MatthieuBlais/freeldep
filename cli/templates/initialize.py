class InitializeDeployerTemplate:
    """Initialize a deployer with an artifact bucket and a registry table"""

    @classmethod
    def name(cls, deployer):
        return f"{deployer['name']}-deployer-initialization-stack"

    @classmethod
    def aws(cls, deployer, config):
        return [
            {
                "aws": {
                    "region": config.get("aws", "region", "ap-southeast-1"),
                    "account-id": config.get("aws", "account", None),
                    "deployment-role": config.get("aws", "deployment_role", ""),
                },
                "location": "./templates/aws/deployer-initialize.yaml",
                "template": {
                    "name": cls.name(deployer),
                    "parameters": {
                        "artifact-bucket": deployer["artifact"],
                        "registry-table": deployer["registry"],
                    },
                },
                "lambdas": [],
            }
        ]
