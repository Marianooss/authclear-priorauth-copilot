"""
a2a_agent/main.py — FastAPI entrypoint for A2A Agent

Registers all routes, configures lifespan, exposes AgentCard.
"""

from __future__ import annotations

from contextlib import asynccontextmanager
import structlog
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from a2a_agent.config import settings
from a2a_agent.models import SendTaskRequest, SendTaskResponse, Task
from a2a_agent.task_store import task_store
from a2a_agent.task_handler import handle_send_task
from a2a_agent.agent_card import get_agent_card

# Configure structured logging
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
        if settings.environment == "production"
        else structlog.dev.ConsoleRenderer(),
    ]
)

log = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup/shutdown.

    Startup:
        - Start task store cleanup loop

    Shutdown:
        - Clean up resources
    """
    log.info("agent_starting", environment=settings.environment, port=settings.port_agent)

    # Start background task cleanup
    import asyncio

    cleanup_task = asyncio.create_task(task_store.start_cleanup_loop())

    yield

    log.info("agent_shutting_down")
    cleanup_task.cancel()


# Create FastAPI app
app = FastAPI(
    title="AuthClear Prior Auth Copilot",
    description="A2A agent for prior authorization generation with human-in-the-loop",
    version="1.0.0",
    lifespan=lifespan,
)

# Add CORS middleware for Prompt Opinion marketplace
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for hackathon/marketplace
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── ROUTES ──────────────────────────────────────────────────────────────────


@app.get("/.well-known/agent.json")
async def agent_card():
    """
    Get AgentCard.

    Returns A2A AgentCard JSON describing agent capabilities.
    Required by A2A protocol.
    """
    return get_agent_card()


@app.post("/tasks/send", response_model=SendTaskResponse)
async def send_task(request: SendTaskRequest):
    """
    Send a task to the agent.

    Submit a new prior auth task or continue an existing one.

    Args:
        request: SendTaskRequest with message and optional task_id

    Returns:
        SendTaskResponse with task status and result
    """
    try:
        response = await handle_send_task(request)
        return response
    except ValueError as e:
        log.error("send_task_validation_error", error=str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        log.error("send_task_error", error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/tasks/{task_id}", response_model=Task)
async def get_task(task_id: str):
    """
    Get task status and result.

    Args:
        task_id: Task ID

    Returns:
        Task object with current state and result
    """
    task = await task_store.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task not found: {task_id}")
    return task


@app.post("/tasks/{task_id}/cancel")
async def cancel_task(task_id: str):
    """
    Cancel a task.

    Args:
        task_id: Task ID

    Returns:
        Success message
    """
    success = await task_store.cancel(task_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Task not found: {task_id}")
    return {"status": "canceled", "task_id": task_id}


@app.get("/health")
async def health_check():
    """
    Health check endpoint for Railway deployment.

    Returns:
        Status and stats
    """
    stats = await task_store.get_stats()
    return {
        "status": "ok",
        "service": "authclear-agent",
        "version": "1.0.0",
        "environment": settings.environment,
        "task_store": stats,
    }


@app.get("/")
async def root():
    """Root endpoint with agent info."""
    return {
        "service": "AuthClear Prior Auth Copilot",
        "version": "1.0.0",
        "agent_card": "/.well-known/agent.json",
        "docs": "/docs",
    }


# ── ERROR HANDLERS ──────────────────────────────────────────────────────────


@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Handle 404 errors."""
    return JSONResponse(
        status_code=404, content={"error": "Not found", "detail": str(exc.detail)}
    )


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """Handle 500 errors."""
    log.error("internal_server_error", error=str(exc), exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": "An unexpected error occurred"},
    )


# ── MAIN ────────────────────────────────────────────────────────────────────


if __name__ == "__main__":
    import uvicorn

    log.info("starting_agent_server", port=settings.port_agent)
    uvicorn.run(
        "a2a_agent.main:app",
        host="0.0.0.0",
        port=settings.port_agent,
        log_level=settings.log_level.lower(),
        reload=settings.environment == "development",
    )
