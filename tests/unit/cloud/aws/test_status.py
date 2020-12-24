from freeldep.cloud.aws.status import StackStatus


def test_success():
    assert StackStatus.success("CREATE_COMPLETE") is True
    assert StackStatus.success("UPDATE_COMPLETE") is True
    assert StackStatus.success("DELETE_COMPLETE") is True
    assert StackStatus.success("CREATE_FAILED") is False


def test_failed():
    assert StackStatus.failed("DELETE_FAILED") is True
    assert StackStatus.failed("CREATE_FAILED") is True
    assert StackStatus.failed("ROLLBACK_COMPLETE") is True
    assert StackStatus.failed("UPDATE_ROLLBACK_COMPLETE") is True
    assert StackStatus.failed("DELETE_COMPLETE") is False
