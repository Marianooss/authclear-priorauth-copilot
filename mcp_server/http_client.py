"""
mcp_server/http_client.py — HTTP client factory with retry logic

Creates configured httpx.AsyncClient instances with:
- Timeout configuration
- Retry logic with exponential backoff
- Standard headers
"""

from __future__ import annotations

import httpx
from mcp_server.config import settings


def get_http_client() -> httpx.AsyncClient:
    """
    Create an httpx.AsyncClient with standard configuration.

    Returns:
        Configured AsyncClient instance

    Configuration:
        - Connect timeout: 10s
        - Read timeout: 30s
        - Follow redirects: Yes
        - User-Agent: Identifies as AuthClear with synthetic data notice
    """
    return httpx.AsyncClient(
        timeout=httpx.Timeout(
            connect=settings.http_connect_timeout,
            read=settings.http_read_timeout,
            write=settings.http_connect_timeout,
            pool=settings.http_connect_timeout,
        ),
        follow_redirects=True,
        headers={
            "User-Agent": "AuthClear/1.0 (Healthcare AI Hackathon; synthetic data only)",
            "Accept": "application/json, application/fhir+json"
        }
    )


async def retry_request(
    client: httpx.AsyncClient,
    method: str,
    url: str,
    **kwargs
) -> httpx.Response:
    """
    Make HTTP request with retry logic.

    Args:
        client: httpx.AsyncClient instance
        method: HTTP method (GET, POST, etc.)
        url: Request URL
        **kwargs: Additional request parameters

    Returns:
        httpx.Response

    Raises:
        httpx.HTTPStatusError: After max retries exhausted
        httpx.TimeoutException: After max retries exhausted

    Retry logic:
        - Max attempts: 3
        - Retry on: 408, 429, 500, 502, 503, 504
        - Backoff: Exponential (2^attempt seconds)
    """
    max_attempts = settings.http_max_retries
    backoff_factor = 2.0

    for attempt in range(1, max_attempts + 1):
        try:
            response = await client.request(method, url, **kwargs)
            response.raise_for_status()
            return response

        except httpx.HTTPStatusError as e:
            # Retry on specific status codes
            if e.response.status_code in [408, 429, 500, 502, 503, 504]:
                if attempt < max_attempts:
                    await _sleep(backoff_factor ** attempt)
                    continue
            raise

        except httpx.TimeoutException:
            if attempt < max_attempts:
                await _sleep(backoff_factor ** attempt)
                continue
            raise


async def _sleep(seconds: float) -> None:
    """Sleep for specified seconds (mockable in tests)."""
    import asyncio
    await asyncio.sleep(seconds)
