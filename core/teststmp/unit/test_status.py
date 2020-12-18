import status as deployer_status


def test_set_status():
    assert deployer_status.set_status(True) == "SUCCESS"
    assert deployer_status.set_status(False) == "FAIL"
    assert deployer_status.set_status(None) == "FAIL"
    assert deployer_status.set_status("sdfsdf") == "FAIL"
