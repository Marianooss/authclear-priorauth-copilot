"""
mcp_server/cache.py — Caching setup for MCP tools

Uses cachetools TTLCache for in-memory caching of external API responses.
"""

from __future__ import annotations

from cachetools import TTLCache
from mcp_server.config import settings


# Cache instances for each tool
ICD10_CACHE = TTLCache(
    maxsize=settings.cache_maxsize_default,
    ttl=settings.cache_ttl_icd10
)

RXNORM_CACHE = TTLCache(
    maxsize=settings.cache_maxsize_default,
    ttl=settings.cache_ttl_rxnorm
)

LOINC_CACHE = TTLCache(
    maxsize=settings.cache_maxsize_default,
    ttl=settings.cache_ttl_loinc
)

INTERACTION_CACHE = TTLCache(
    maxsize=settings.cache_maxsize_interactions,
    ttl=settings.cache_ttl_interactions
)


def cache_key(fn_name: str, *args) -> str:
    """
    Generate a cache key from function name and arguments.

    Args:
        fn_name: Name of the function
        *args: Function arguments

    Returns:
        Cache key string in format "fn_name:arg1:arg2:..."

    Example:
        >>> cache_key("resolve_icd10", "E11.9")
        "resolve_icd10:E11.9"
    """
    return f"{fn_name}:{':'.join(str(a) for a in args)}"
