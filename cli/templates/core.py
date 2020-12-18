class CoreDeployerTemplate:
    """Create the core functionalities of the deployer with the workflow deployer"""

    @classmethod
    def name(cls, deployer):
        return f"{deployer['name']}-deployer-core-stack"

    @classmethod
    def aws(cls, deployer, config):
        return [
            {
                "aws": {
                    "region": config.get("aws", "region", "ap-southeast-1"),
                    "account-id": config.get("aws", "account", None),
                    "deployment-role": config.get("aws", "deployment_role", ""),
                },
                "location": "./templates/aws/deployer-core.yaml",
                "template": {
                    "name": cls.name(deployer),
                    "parameters": {
                        "stack-prefix": deployer["name"],
                        "registry-table": deployer["registry"],
                        "artifact-bucket": deployer["artifact"],
                        "deployment-workflow": f"{deployer['name']}-deployer-core",
                    },
                    "lambda-code-key": f"packages/{deployer['name']}-deployer-core-stack/",
                },
                "lambdas": [
                    {
                        "name": "package",
                        "location": "./core/",
                        "template-attribute": "lambda-code-key",
                        "bucket": deployer["artifact"],
                    }
                ],
            }
        ]
