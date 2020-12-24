class SubscriptionDeployerTemplate:
    """Create a service that can be used to be integrated with the core deployer"""

    @classmethod
    def name(cls, deployer, subscription):
        return f"{deployer['name']}-deployer-{subscription}-subscription"

    @classmethod
    def get(cls, subscription, subscription_list, deployer, config):
        cloud = deployer.get("cloud", None)
        if cloud == "AWS":
            return cls.aws(subscription, subscription_list, deployer, config)
        raise NotImplementedError("Unknown cloud")

    @classmethod
    def aws(cls, subscription, subscription_list, deployer, config):
        return [
            {
                "aws": {
                    "region": config.get("aws", "region", "ap-southeast-1"),
                    "account-id": config.get("aws", "account", None),
                    "deployment-role": config.get("aws", "deployment_role", ""),
                },
                "location": "./templates/aws/deployer-subscription.yaml",
                "template": {
                    "name": cls.name(deployer, subscription),
                    "parameters": {
                        "deployer-name": deployer["name"],
                        "subscription-name": subscription,
                    },
                    "subscriptions": subscription_list,
                },
                "functions": [],
            }
        ]
