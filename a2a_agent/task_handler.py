"""
a2a_agent/task_handler.py — Task request handler

Handles POST /tasks/send - validates input, manages task lifecycle,
triggers orchestrator.
"""

from __future__ import annotations

import json
import structlog

from a2a_agent.models import (
    SendTaskRequest,
    SendTaskResponse,
    Task,
    TaskInput,
    TaskState,
    TaskMessage,
)
from a2a_agent.task_store import task_store
from a2a_agent.orchestrator import run_prior_auth_orchestration
from a2a_agent.tools.mcp_client import MCPClient
from a2a_agent.config import settings

log = structlog.get_logger()


async def handle_send_task(request: SendTaskRequest) -> SendTaskResponse:
    """
    Handle POST /tasks/send request.

    Flow:
        1. If request.id is None → create new task
        2. If request.id exists → retrieve and continue existing task
        3. Parse task input from message content
        4. Trigger orchestrator
        5. Store updated task
        6. Return response

    Args:
        request: SendTaskRequest with message

    Returns:
        SendTaskResponse with updated task

    Raises:
        ValueError: If task input is invalid
        RuntimeError: If orchestration fails
    """
    log.info("handle_send_task", task_id=request.id, has_id=request.id is not None)

    # Get or create task
    if request.id:
        # Continue existing task
        task = await task_store.get(request.id)
        if not task:
            raise ValueError(f"Task not found: {request.id}")
        log.info("task_continued", task_id=task.id, state=task.state)
    else:
        # Create new task
        task = task_store.create()
        log.info("task_created", task_id=task.id)

    # Append message to task history
    task.messages.append(request.message)

    # Parse task input from message content
    try:
        if task.input is None:
            # First message - parse input
            content = request.message.content
            input_data = json.loads(content)
            task.input = TaskInput(**input_data)
            log.info("task_input_parsed", task_id=task.id, requested_item=task.input.requested_item)
        else:
            # Continuation - update additional context
            content = request.message.content
            if isinstance(content, str) and content.strip():
                if not task.input.additional_context:
                    task.input.additional_context = content
                else:
                    task.input.additional_context += f"\n\n{content}"
    except json.JSONDecodeError as e:
        log.error("input_parse_failed", task_id=task.id, error=str(e))
        task.state = TaskState.FAILED
        task.error = f"Invalid JSON in message content: {str(e)}"
        await task_store.store(task)
        return SendTaskResponse(task=task)
    except Exception as e:
        log.error("input_validation_failed", task_id=task.id, error=str(e))
        task.state = TaskState.FAILED
        task.error = f"Input validation error: {str(e)}"
        await task_store.store(task)
        return SendTaskResponse(task=task)

    # Update state to WORKING
    task.state = TaskState.WORKING
    await task_store.store(task)

    # Run orchestrator
    try:
        async with MCPClient(settings.mcp_server_url) as mcp:
            task = await run_prior_auth_orchestration(task, mcp)
    except Exception as e:
        log.error("orchestration_error", task_id=task.id, error=str(e), exc_info=True)
        task.state = TaskState.FAILED
        task.error = f"Orchestration failed: {str(e)}"

    # Store final task state
    await task_store.store(task)

    # Generate agent response message
    if task.state == TaskState.COMPLETED and task.result:
        response_content = f"Prior authorization draft completed.\n\nConfidence: {task.result.confidence_level.value} ({task.result.confidence_score:.0%})\n\nMissing items: {len(task.result.missing_items)}"
        task.messages.append(
            TaskMessage(
                role="agent",
                content=response_content,
            )
        )
    elif task.state == TaskState.FAILED:
        task.messages.append(
            TaskMessage(
                role="agent",
                content=f"Task failed: {task.error}",
            )
        )

    # Update task one more time with messages
    await task_store.store(task)

    log.info("task_handled", task_id=task.id, final_state=task.state)

    return SendTaskResponse(task=task)
