import os

import pytest

from freeldep.templates import SubscriptionDeployerTemplate


def test_name(deployer):
    assert (
        SubscriptionDeployerTemplate.name(deployer, "testsub")
        == "test-deployer-testsub-subscription"
    )


def test_nocloud(deployer, config):
    subscriptions = ["sdfsdf"]
    testdeployer = deployer.copy()
    testdeployer["cloud"] = "AWS"
    assert (
        SubscriptionDeployerTemplate.get("testsub", subscriptions, testdeployer, config)
        is not None
    )
    with pytest.raises(NotImplementedError):
        testdeployer["cloud"] = "GCP"
        SubscriptionDeployerTemplate.get("testsub", subscriptions, testdeployer, config)
    with pytest.raises(NotImplementedError):
        testdeployer["cloud"] = "sdfsdfsdfsdf"
        SubscriptionDeployerTemplate.get("testsub", subscriptions, testdeployer, config)


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
