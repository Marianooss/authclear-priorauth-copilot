#!/usr/bin/env python
"""
Run MCP Server with proper PYTHONPATH configuration
"""
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Now import and run the server
if __name__ == "__main__":
    from mcp_server.server import mcp
    from mcp_server.config import settings

    print(f"Starting MCP Server on port {settings.port_mcp}")
    print(f"Environment: {settings.environment}")
    print(f"Log level: {settings.log_level}")

    mcp.run(port=settings.port_mcp)
