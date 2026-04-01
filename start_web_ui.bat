@echo off
echo ================================================================================
echo   AuthClear - Web UI Launcher
echo ================================================================================
echo.
echo Starting web server on http://localhost:3000
echo.
echo IMPORTANT: Backend servers should be running:
echo   1. MCP Server on port 8001: python run_mcp_server.py
echo   2. A2A Agent on port 8000: python run_a2a_agent.py
echo.
echo Your browser will open automatically in a few seconds...
echo.
echo ================================================================================
echo.

python run_web_server.py

pause
