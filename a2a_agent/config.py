"""
a2a_agent/config.py — A2A Agent configuration

Uses pydantic-settings to load configuration from environment variables.
"""

from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """A2A Agent configuration loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",  # Ignore extra fields from .env
    )

    # Claude Provider (anthropic or bedrock)
    claude_provider: str = "anthropic"  # "anthropic" or "bedrock"

    # Anthropic API (if using anthropic provider)
    anthropic_api_key: str = ""

    # AWS Bedrock (if using bedrock provider)
    aws_region: str = "us-east-1"
    aws_access_key_id: str | None = None  # Optional if using ~/.aws/credentials
    aws_secret_access_key: str | None = None  # Optional if using ~/.aws/credentials
    aws_bedrock_model: str = "anthropic.claude-sonnet-4-20250514-v1:0"

    # Server
    port_agent: int = 8000

    # MCP Server
    mcp_server_url: str = "http://localhost:8001"

    # FHIR
    hapi_fhir_base: str = "https://hapi.fhir.org/baseR4"

    # HTTP Client
    http_connect_timeout: float = 10.0
    http_read_timeout: float = 30.0
    http_max_retries: int = 3

    # Task Store
    task_ttl_hours: int = 24
    max_concurrent_tasks: int = 10

    # Claude API
    claude_model: str = "claude-sonnet-4-20250514"
    claude_max_tokens: int = 4096
    claude_temperature: float = 0.0

    # Orchestrator
    max_tool_iterations: int = 10
    orchestrator_timeout: float = 60.0

    # Logging
    log_level: str = "INFO"
    environment: str = "development"


# Global settings instance
settings = Settings()
