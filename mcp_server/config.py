"""
mcp_server/config.py — MCP Server configuration

Uses pydantic-settings to load configuration from environment variables.
"""

from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """MCP Server configuration loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",  # Ignore extra fields from .env
    )

    # Server
    port_mcp: int = 8001

    # External APIs
    nlm_api_key: str = ""  # Optional — higher rate limits for NLM APIs
    hapi_fhir_base: str = "https://hapi.fhir.org/baseR4"

    # HTTP Client
    http_connect_timeout: float = 10.0
    http_read_timeout: float = 30.0
    http_max_retries: int = 3

    # Logging
    log_level: str = "INFO"
    environment: str = "development"

    # Cache TTLs (seconds)
    cache_ttl_icd10: int = 3600       # 1 hour - codes are stable
    cache_ttl_rxnorm: int = 3600      # 1 hour
    cache_ttl_loinc: int = 3600       # 1 hour
    cache_ttl_interactions: int = 300  # 5 minutes - more dynamic

    # Cache sizes
    cache_maxsize_default: int = 1000
    cache_maxsize_interactions: int = 500


# Global settings instance
settings = Settings()
