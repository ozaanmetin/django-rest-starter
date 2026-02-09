"""HTTP Client exceptions."""


class HTTPRetryExhaustedError(Exception):
    """
    Raised when all retry attempts have been exhausted.

    Attributes:
        attempts: Number of attempts made
        last_exception: The last exception that caused the retry
    """

    def __init__(
        self,
        message: str,
        attempts: int,
        last_exception: Exception | None = None,
    ):
        self.attempts = attempts
        self.last_exception = last_exception
        super().__init__(message)
