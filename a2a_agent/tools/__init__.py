"""
a2a_agent/tools — Agent tool implementations

Exports FHIR parser and MCP client.
"""

from a2a_agent.tools.fhir_reader import parse_fhir_bundle, FHIRParseError
from a2a_agent.tools.mcp_client import MCPClient

__all__ = [
    "parse_fhir_reader",
    "FHIRParseError",
    "MCPClient",
]
