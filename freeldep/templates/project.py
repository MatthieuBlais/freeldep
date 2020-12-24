class ProjectTemplate:
    @classmethod
    def name(cls, deployer, project):
        return f"{deployer['name']}-deployer-project-{project}"

    @classmethod
    def get(cls, project, branches, deployer, config):
        cloud = deployer.get("cloud", None)
        if cloud == "AWS":
            return cls.aws(project, branches, deployer, config)
        raise NotImplementedError("Unknown cloud")

    @classmethod
    def aws(cls, project, branches, deployer, config):
        return [
            {
                "aws": {
                    "region": config.get("aws", "region", "ap-southeast-1"),
                    "account-id": config.get("aws", "account", None),
                    "deployment-role": config.get("aws", "deployment_role", ""),
                },
                "location": "./templates/aws/deployer-project.yaml",
                "template": {
                    "name": cls.name(deployer, project),
                    "parameters": {
                        "project": project,
                        "deployer": deployer["name"],
                        "branches": branches,
                        "service-trigger": f"{deployer['service-trigger']}",
                        "deployer-service-role": f"{deployer['service-role']}",
                    },
                },
                "functions": [],
            }
        ]
