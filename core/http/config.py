"""
HTTP Client configuration.
"""

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class RetryConfig:
    """
    Configuration for retry behavior.

    Attributes:
        max_attempts: Maximum number of retry attempts (including initial request)
        min_wait_seconds: Minimum wait time between retries
        max_wait_seconds: Maximum wait time between retries
        exponential_base: Base for exponential backoff calculation
        retry_on_status_codes: HTTP status codes that should trigger a retry
    """

    max_attempts: int = 3
    min_wait_seconds: float = 0.5
    max_wait_seconds: float = 10.0
    exponential_base: float = 2.0
    retry_on_status_codes: tuple[int, ...] = (429, 500, 502, 503, 504)

    def __post_init__(self) -> None:
        if self.max_attempts < 1:
            raise ValueError("max_attempts must be at least 1")
        if self.min_wait_seconds < 0:
            raise ValueError("min_wait_seconds must be non-negative")
        if self.max_wait_seconds < self.min_wait_seconds:
            raise ValueError("max_wait_seconds must be >= min_wait_seconds")

    @classmethod
    def no_retry(cls):
        """Create a config with retries disabled."""
        return cls(max_attempts=1)

    @classmethod
    def aggressive(cls):
        """Create a config with aggressive retry settings."""
        return cls(
            max_attempts=5,
            min_wait_seconds=0.1,
            max_wait_seconds=2.0,
        )


@dataclass(frozen=True, slots=True)
class HTTPClientConfig:
    """
    Configuration for HTTP client.

    Attributes:
        base_url: Base URL for all requests (optional)
        timeout_seconds: Default timeout for requests
        connect_timeout_seconds: Timeout for establishing connections
        default_headers: Headers to include in all requests
        retry: Retry configuration
        follow_redirects: Whether to follow HTTP redirects
        verify_ssl: Whether to verify SSL certificates
    """

    base_url: str | None = None
    timeout_seconds: float = 30.0
    connect_timeout_seconds: float = 10.0
    default_headers: dict[str, str] = field(default_factory=dict)
    retry: RetryConfig = field(default_factory=RetryConfig)
    follow_redirects: bool = True
    verify_ssl: bool = True

    def __post_init__(self) -> None:
        if self.timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")
        if self.connect_timeout_seconds <= 0:
            raise ValueError("connect_timeout_seconds must be positive")
