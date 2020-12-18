import os

from cli.templates import SubscriptionDeployerTemplate


def test_name(deployer):
    assert (
        SubscriptionDeployerTemplate.name(deployer, "testsub")
        == "test-deployer-testsub-subscription"
    )


def test_aws(deployer, config, configfile):
    subscriptions = ["sdfsdf"]
    template = SubscriptionDeployerTemplate.aws(
        "testsub", subscriptions, deployer, config
    )

    assert len(template) == 1
    assert template[0]["aws"]["account-id"] == configfile["aws"].get("account")
    assert template[0]["aws"]["region"] == configfile["aws"].get("region")
    assert template[0]["aws"]["deployment-role"] == configfile["aws"].get(
        "deployment-role", ""
    )
    assert os.path.isfile(template[0]["location"])
    assert template[0]["template"]["name"] == SubscriptionDeployerTemplate.name(
        deployer, "testsub"
    )
    assert template[0]["template"]["parameters"]["subscription-name"] == "testsub"
    assert len(template[0]["template"]["subscriptions"]) == len(subscriptions)
