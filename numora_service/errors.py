class ServiceError(Exception):
    """A bounded public error, never a database exception or generated content."""

    def __init__(self, code, status=409):
        self.code, self.status = code, status
        super().__init__(code)
