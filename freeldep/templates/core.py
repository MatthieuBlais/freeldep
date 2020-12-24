class CoreDeployerTemplate:
    """Create the core functionalities of the deployer with the workflow deployer"""

    @classmethod
    def name(cls, deployer):
        return f"{deployer['name']}-deployer-core-stack"

    @classmethod
    def get(cls, deployer, config):
        cloud = deployer.get("cloud", None)
        if cloud == "AWS":
            return cls.aws(deployer, config)
        raise NotImplementedError("Unknown cloud")

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
                "functions": [
                    {
                        "name": "package",
                        "location": "./core/",
                        "template-attribute": "lambda-code-key",
                        "bucket": deployer["artifact"],
                    }
                ],
            }
        ]
