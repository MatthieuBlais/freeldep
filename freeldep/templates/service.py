class ServiceDeployerTemplate:
    """Create a service that can be used to be integrated with the core deployer"""

    @classmethod
    def name(cls, deployer):
        return f"{deployer['name']}-deployer-service-stack"

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
                "location": "./templates/aws/deployer-service.yaml",
                "template": {
                    "name": cls.name(deployer),
                    "parameters": {
                        "deployer": deployer["name"],
                        "codebuild-service": f"{deployer['name']}-deployer-service",
                        "service-trigger": f"{deployer['name']}-deployer-service-trigger",
                        "artifact-bucket": deployer["artifact"],
                        "deployment-workflow": f"{deployer['name']}-deployer-core",
                    },
                    "lambda-code-key": f"packages/{deployer['name']}-deployer-service-stack/",
                },
                "functions": [
                    {
                        "name": "package",
                        "location": "./service/",
                        "template-attribute": "lambda-code-key",
                        "bucket": deployer["artifact"],
                    }
                ],
            }
        ]
