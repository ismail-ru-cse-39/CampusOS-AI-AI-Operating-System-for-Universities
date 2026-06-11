"""Celery worker stub for T-030 — replace with real task queue when Redis is available."""

from __future__ import annotations

import logging
from typing import Any, Callable

logger = logging.getLogger(__name__)


def enqueue_task(task_name: str, payload: dict[str, Any]) -> dict[str, Any]:
    """Synchronous stub — logs task instead of dispatching to Redis/Celery."""
    logger.info("worker_stub task=%s payload_keys=%s", task_name, list(payload.keys()))
    return {
        "task_id": f"stub-{task_name}",
        "status": "queued_stub",
        "message": "Configure Redis/Celery worker for async execution (T-030)",
    }


def register_task(name: str, handler: Callable[..., Any]) -> None:
    logger.debug("worker_stub registered task=%s", name)
