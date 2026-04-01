#!/usr/bin/env python
"""
Run A2A Agent with proper PYTHONPATH configuration
"""
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Now import and run the agent
if __name__ == "__main__":
    import uvicorn
    from a2a_agent.config import settings

    print(f"Starting A2A Agent on port {settings.port_agent}")
    print(f"MCP Server URL: {settings.mcp_server_url}")
    print(f"Environment: {settings.environment}")
    print(f"Log level: {settings.log_level}")

    uvicorn.run(
        "a2a_agent.main:app",
        host="0.0.0.0",
        port=settings.port_agent,
        log_level=settings.log_level.lower(),
        reload=settings.environment == "development",
    )
