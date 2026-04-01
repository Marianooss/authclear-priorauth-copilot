"""
a2a_agent/task_store.py — In-memory task store with TTL

Thread-safe in-memory storage for tasks with automatic expiration.
"""

from __future__ import annotations

import asyncio
from datetime import datetime
from typing import Dict
import structlog
import uuid

from a2a_agent.models import Task, TaskState

log = structlog.get_logger()


class TaskStore:
    """
    In-memory task storage with TTL.

    Tasks are stored in a dict and automatically cleaned up after expiration.
    Thread-safe via asyncio.Lock.
    """

    def __init__(self):
        self._tasks: Dict[str, Task] = {}
        self._lock = asyncio.Lock()
        self._cleanup_task = None

    def create(self, task_id: str | None = None) -> Task:
        """
        Create a new task with generated ID.

        Args:
            task_id: Optional task ID (if None, generates UUID)

        Returns:
            Created Task
        """
        if task_id is None:
            task_id = f"task-{uuid.uuid4().hex[:12]}"

        # Note: Task input will be set by caller
        task = Task(
            id=task_id,
            state=TaskState.SUBMITTED,
            input=None  # Will be set by handler
        )

        log.info("task_created", task_id=task_id)
        return task

    async def store(self, task: Task) -> None:
        """
        Store or update a task.

        Args:
            task: Task to store
        """
        async with self._lock:
            task.updated_at = datetime.utcnow()
            self._tasks[task.id] = task
            log.debug("task_stored", task_id=task.id, state=task.state)

    async def get(self, task_id: str) -> Task | None:
        """
        Get a task by ID.

        Args:
            task_id: Task ID

        Returns:
            Task or None if not found
        """
        async with self._lock:
            return self._tasks.get(task_id)

    async def update(self, task: Task) -> None:
        """
        Update an existing task.

        Args:
            task: Task to update
        """
        await self.store(task)

    async def cancel(self, task_id: str) -> bool:
        """
        Cancel a task.

        Args:
            task_id: Task ID

        Returns:
            True if task was canceled, False if not found
        """
        async with self._lock:
            task = self._tasks.get(task_id)
            if task:
                task.state = TaskState.CANCELED
                task.updated_at = datetime.utcnow()
                log.info("task_canceled", task_id=task_id)
                return True
            return False

    async def delete(self, task_id: str) -> bool:
        """
        Delete a task from store.

        Args:
            task_id: Task ID

        Returns:
            True if deleted, False if not found
        """
        async with self._lock:
            if task_id in self._tasks:
                del self._tasks[task_id]
                log.debug("task_deleted", task_id=task_id)
                return True
            return False

    async def cleanup_expired(self) -> int:
        """
        Remove expired tasks from store.

        Returns:
            Number of tasks cleaned up
        """
        now = datetime.utcnow()
        expired_ids = []

        async with self._lock:
            for task_id, task in self._tasks.items():
                if task.expires_at < now:
                    expired_ids.append(task_id)

            for task_id in expired_ids:
                del self._tasks[task_id]

        if expired_ids:
            log.info("tasks_expired", count=len(expired_ids), task_ids=expired_ids)

        return len(expired_ids)

    async def start_cleanup_loop(self):
        """Start background cleanup loop."""
        log.info("cleanup_loop_started")
        while True:
            await asyncio.sleep(300)  # Run every 5 minutes
            await self.cleanup_expired()

    async def get_stats(self) -> dict:
        """
        Get task store statistics.

        Returns:
            Dictionary with stats
        """
        async with self._lock:
            total = len(self._tasks)
            by_state = {}
            for task in self._tasks.values():
                state = task.state.value
                by_state[state] = by_state.get(state, 0) + 1

            return {
                "total_tasks": total,
                "by_state": by_state
            }


# Global task store instance
task_store = TaskStore()
