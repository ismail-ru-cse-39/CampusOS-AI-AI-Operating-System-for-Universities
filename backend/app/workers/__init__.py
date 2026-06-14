"""Background task queue — Celery when Redis is available, synchronous stub otherwise."""

from __future__ import annotations

import logging
from typing import Any, Callable

from app.core.config import settings

logger = logging.getLogger(__name__)

_celery_app = None
_task_handlers: dict[str, Callable[..., Any]] = {}


def _get_celery():
    global _celery_app
    if _celery_app is not None:
        return _celery_app
    if not settings.celery_enabled:
        return None
    try:
        from celery import Celery

        app = Celery("campusos", broker=settings.redis_url, backend=settings.redis_url)
        app.conf.task_serializer = "json"
        app.conf.result_serializer = "json"
        app.conf.accept_content = ["json"]
        _celery_app = app
        return app
    except Exception as exc:
        logger.warning("celery_init_failed error=%s — falling back to stub", exc)
        return None


def register_task(name: str, handler: Callable[..., Any]) -> None:
    _task_handlers[name] = handler
    celery = _get_celery()
    if celery is not None:
        celery.task(name=name)(handler)
    logger.debug("worker registered task=%s celery=%s", name, celery is not None)


def enqueue_task(task_name: str, payload: dict[str, Any]) -> dict[str, Any]:
    handler = _task_handlers.get(task_name)
    celery = _get_celery()

    if celery is not None and handler is not None:
        result = celery.send_task(task_name, kwargs=payload)
        return {
            "task_id": result.id,
            "status": "queued",
            "message": "Task dispatched to Celery worker",
        }

    if handler is not None:
        try:
            result = handler(**payload)
            return {
                "task_id": f"sync-{task_name}",
                "status": "completed",
                "result": result,
                "message": "Executed synchronously (Celery not enabled)",
            }
        except Exception as exc:
            logger.error("sync_task_failed task=%s error=%s", task_name, exc)
            return {"task_id": f"sync-{task_name}", "status": "failed", "error": str(exc)}

    logger.info("worker_stub task=%s payload_keys=%s", task_name, list(payload.keys()))
    return {
        "task_id": f"stub-{task_name}",
        "status": "queued_stub",
        "message": "Set CELERY_ENABLED=true and run a Celery worker for async execution",
    }
