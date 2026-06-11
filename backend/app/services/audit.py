from __future__ import annotations

import logging
from typing import Any, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


async def log_audit(
    db: AsyncSession,
    *,
    action: str,
    resource: str,
    user_id: Optional[UUID] = None,
    details: Optional[dict[str, Any]] = None,
) -> None:
    """Persist an audit log entry; falls back to structured logging if DB/model write fails."""
    payload = details or {}
    try:
        from app.models import AuditLog

        entry = AuditLog(
            user_id=user_id,
            action=action,
            resource=resource,
            details=payload,
        )
        db.add(entry)
        await db.commit()
    except Exception:
        await db.rollback()
        logger.info(
            "audit_event action=%s resource=%s user_id=%s details=%s",
            action,
            resource,
            user_id,
            payload,
        )
