"""
a2a_agent/claude_client.py — Unified Claude client for Anthropic API + AWS Bedrock

Provides a unified interface for calling Claude via either:
- Anthropic API (direct)
- AWS Bedrock (boto3)

Usage:
    client = get_claude_client()
    response = await client.create_message(...)
"""

from __future__ import annotations

import json
import structlog
from typing import Any

from a2a_agent.config import settings

log = structlog.get_logger()


class ClaudeClient:
    """Unified Claude client interface."""

    async def create_message(
        self,
        model: str,
        max_tokens: int,
        temperature: float,
        system: str,
        tools: list[dict],
        messages: list[dict],
    ) -> dict:
        """
        Create a message using Claude API.

        Args:
            model: Model ID
            max_tokens: Max tokens in response
            temperature: Sampling temperature
            system: System prompt
            tools: Tool definitions
            messages: Conversation messages

        Returns:
            Response dict with content, stop_reason, etc.
        """
        raise NotImplementedError()


class AnthropicClient(ClaudeClient):
    """Anthropic API client."""

    def __init__(self):
        from anthropic import AsyncAnthropic
        self.client = AsyncAnthropic(api_key=settings.anthropic_api_key)

    async def create_message(
        self,
        model: str,
        max_tokens: int,
        temperature: float,
        system: str,
        tools: list[dict],
        messages: list[dict],
    ) -> Any:
        """Call Anthropic API."""
        response = await self.client.messages.create(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system,
            tools=tools,
            messages=messages,
        )
        return response


class BedrockClient(ClaudeClient):
    """AWS Bedrock client."""

    def __init__(self):
        import boto3

        # Build boto3 client kwargs
        client_kwargs = {"region_name": settings.aws_region}

        # Add explicit credentials if provided in .env and not empty/None
        if (settings.aws_access_key_id and
            settings.aws_secret_access_key and
            settings.aws_access_key_id.strip() and
            settings.aws_secret_access_key.strip()):
            client_kwargs["aws_access_key_id"] = settings.aws_access_key_id
            client_kwargs["aws_secret_access_key"] = settings.aws_secret_access_key
            log.info("using_explicit_aws_credentials_from_env")
        else:
            log.info("using_default_aws_credentials", region=settings.aws_region)

        self.client = boto3.client("bedrock-runtime", **client_kwargs)
        self.model_id = settings.aws_bedrock_model

    async def create_message(
        self,
        model: str,
        max_tokens: int,
        temperature: float,
        system: str,
        tools: list[dict],
        messages: list[dict],
    ) -> BedrockResponse:
        """Call AWS Bedrock."""
        # Build Bedrock request body
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max_tokens,
            "temperature": temperature,
            "system": system,
            "messages": messages,
        }

        if tools:
            body["tools"] = tools

        log.debug("bedrock_request", model_id=self.model_id, messages_count=len(messages))

        # Call Bedrock (sync - boto3 doesn't have async yet)
        import asyncio
        response = await asyncio.to_thread(
            self.client.invoke_model,
            modelId=self.model_id,
            body=json.dumps(body),
        )

        # Parse response
        response_body = json.loads(response["body"].read())

        log.debug("bedrock_response", stop_reason=response_body.get("stop_reason"))

        # Wrap in BedrockResponse to match Anthropic API interface
        return BedrockResponse(response_body)


class BedrockResponse:
    """Wrapper to make Bedrock response compatible with Anthropic API response."""

    def __init__(self, body: dict):
        self._body = body

    @property
    def content(self) -> list:
        """Get content blocks."""
        return [ContentBlock(block) for block in self._body.get("content", [])]

    @property
    def stop_reason(self) -> str:
        """Get stop reason."""
        return self._body.get("stop_reason", "end_turn")

    @property
    def usage(self) -> dict:
        """Get usage stats."""
        return self._body.get("usage", {})


class ContentBlock:
    """Wrapper for content blocks."""

    def __init__(self, block: dict):
        self._block = block

    @property
    def type(self) -> str:
        return self._block.get("type")

    @property
    def text(self) -> str | None:
        return self._block.get("text")

    @property
    def name(self) -> str | None:
        """Tool name (for tool_use blocks)."""
        return self._block.get("name")

    @property
    def input(self) -> dict | None:
        """Tool input (for tool_use blocks)."""
        return self._block.get("input")

    @property
    def id(self) -> str | None:
        """Tool use ID (for tool_use blocks)."""
        return self._block.get("id")


def get_claude_client() -> ClaudeClient:
    """
    Get Claude client based on configuration.

    Returns:
        AnthropicClient or BedrockClient based on settings.claude_provider
    """
    provider = settings.claude_provider.lower()

    if provider == "bedrock":
        log.info("initializing_bedrock_client", region=settings.aws_region, model=settings.aws_bedrock_model)
        return BedrockClient()
    elif provider == "anthropic":
        log.info("initializing_anthropic_client", model=settings.claude_model)
        return AnthropicClient()
    else:
        raise ValueError(f"Unknown claude_provider: {provider}. Must be 'anthropic' or 'bedrock'")
