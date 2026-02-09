"""
HTTP Clients with retry support.
"""

import asyncio
import logging
import random
import time
from typing import Any

import httpx

from .config import HTTPClientConfig
from .exceptions import HTTPRetryExhaustedError

logger = logging.getLogger(__name__)


def _calculate_backoff(attempt: int, min_wait: float, max_wait: float, exp_base: float) -> float:
    """Calculate backoff with exponential increase and jitter."""
    exp_wait = min_wait * (exp_base**attempt)
    return random.uniform(0, min(exp_wait, max_wait))  # nosec B311 - not for crypto


class HTTPClient:
    """
    Synchronous HTTP client with retry support.
    """

    def __init__(self, config: HTTPClientConfig | None = None):
        self.config = config or HTTPClientConfig()
        self._client: httpx.Client | None = None

    @property
    def client(self) -> httpx.Client:
        if self._client is None or self._client.is_closed:
            self._client = httpx.Client(  # nosec B113 - timeout is configured
                base_url=self.config.base_url or "",
                timeout=httpx.Timeout(self.config.timeout_seconds, connect=self.config.connect_timeout_seconds),
                headers=self.config.default_headers,
                follow_redirects=self.config.follow_redirects,
                verify=self.config.verify_ssl,
            )
        return self._client

    def __enter__(self):
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()

    def close(self) -> None:
        if self._client and not self._client.is_closed:
            self._client.close()
            self._client = None

    def request(self, method: str, url: str, **kwargs: Any) -> httpx.Response:
        """Make an HTTP request with retry support."""
        retry = self.config.retry
        last_exc: Exception | None = None

        for attempt in range(retry.max_attempts):
            try:
                response = self.client.request(method, url, **kwargs)
                response.raise_for_status()
                return response

            except httpx.HTTPStatusError as e:
                # Don't retry if not in retryable status codes
                if e.response.status_code not in retry.retry_on_status_codes:
                    raise
                last_exc = e

            except (httpx.TimeoutException, httpx.ConnectError) as e:
                last_exc = e

            except httpx.RequestError:
                raise  # Not retryable

            # Last attempt failed
            if attempt + 1 >= retry.max_attempts:
                break

            backoff = _calculate_backoff(
                attempt, retry.min_wait_seconds, retry.max_wait_seconds, retry.exponential_base
            )
            logger.warning(f"Retrying {method} {url}, attempt {attempt + 1}, backoff {backoff:.2f} seconds")
            time.sleep(backoff)

        raise HTTPRetryExhaustedError(
            f"All {retry.max_attempts} attempts exhausted for {method} {url}",
            attempts=retry.max_attempts,
            last_exception=last_exc,
        )

    def get(self, url: str, **kwargs: Any):
        return self.request("GET", url, **kwargs)

    def post(self, url: str, **kwargs: Any):
        return self.request("POST", url, **kwargs)

    def put(self, url: str, **kwargs: Any):
        return self.request("PUT", url, **kwargs)

    def patch(self, url: str, **kwargs: Any):
        return self.request("PATCH", url, **kwargs)

    def delete(self, url: str, **kwargs: Any):
        return self.request("DELETE", url, **kwargs)


class AsyncHTTPClient:
    """
    Asynchronous HTTP client with retry support.
    """

    def __init__(self, config: HTTPClientConfig | None = None):
        self.config = config or HTTPClientConfig()
        self._client: httpx.AsyncClient | None = None

    @property
    def client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(  # nosec B113 - timeout is configured
                base_url=self.config.base_url or "",
                timeout=httpx.Timeout(self.config.timeout_seconds, connect=self.config.connect_timeout_seconds),
                headers=self.config.default_headers,
                follow_redirects=self.config.follow_redirects,
                verify=self.config.verify_ssl,
                http2=self.config.http2,
            )
        return self._client

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args: Any):
        await self.close()

    async def close(self) -> None:
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None

    async def request(self, method: str, url: str, **kwargs: Any) -> httpx.Response:
        """Make an async HTTP request with retry support."""
        retry = self.config.retry
        last_exc: Exception | None = None

        for attempt in range(retry.max_attempts):
            try:
                response = await self.client.request(method, url, **kwargs)
                response.raise_for_status()
                return response

            except httpx.HTTPStatusError as e:
                if e.response.status_code not in retry.retry_on_status_codes:
                    raise
                last_exc = e

            except (httpx.TimeoutException, httpx.ConnectError) as e:
                last_exc = e

            except httpx.RequestError:
                raise

            if attempt + 1 >= retry.max_attempts:
                break

            backoff = _calculate_backoff(
                attempt, retry.min_wait_seconds, retry.max_wait_seconds, retry.exponential_base
            )
            logger.warning("Retrying", extra={"method": method, "url": url, "attempt": attempt + 1, "backoff": backoff})
            await asyncio.sleep(backoff)

        raise HTTPRetryExhaustedError(
            f"All {retry.max_attempts} attempts exhausted for {method} {url}",
            attempts=retry.max_attempts,
            last_exception=last_exc,
        )

    async def get(self, url: str, **kwargs: Any):
        return await self.request("GET", url, **kwargs)

    async def post(self, url: str, **kwargs: Any):
        return await self.request("POST", url, **kwargs)

    async def put(self, url: str, **kwargs: Any):
        return await self.request("PUT", url, **kwargs)

    async def patch(self, url: str, **kwargs: Any):
        return await self.request("PATCH", url, **kwargs)

    async def delete(self, url: str, **kwargs: Any):
        return await self.request("DELETE", url, **kwargs)
