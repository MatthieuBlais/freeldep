class StackStatus:
    @classmethod
    def success(cls, status):
        return status in ["CREATE_COMPLETE", "UPDATE_COMPLETE", "DELETE_COMPLETE"]

    @classmethod
    def failed(cls, status):
        return status in [
            "DELETE_FAILED",
            "CREATE_FAILED",
            "ROLLBACK_COMPLETE",
            "UPDATE_ROLLBACK_COMPLETE",
        ]
