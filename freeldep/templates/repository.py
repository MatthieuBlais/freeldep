class DeployerRepositoryTemplate:
    """Create a repository for continuous integration of deployer"""

    @classmethod
    def name(cls, deployer):
        return f"{deployer['name']}-deployer-repository-stack"

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
                "location": "./templates/aws/deployer-repository.yaml",
                "template": {
                    "name": cls.name(deployer),
                    "parameters": {
                        "repository": f"{deployer['name']}-deployer",
                        "repository-codebuild": f"{deployer['name']}-deployer"
                        "-continuous-integration",
                        "artifact-bucket": deployer["artifact"],
                        "deployment-workflow": f"{deployer['name']}-deployer-core",
                    },
                },
                "functions": [],
            }
        ]
