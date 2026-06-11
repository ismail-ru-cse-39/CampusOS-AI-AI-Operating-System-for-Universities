from __future__ import annotations

from dataclasses import dataclass
from typing import Annotated, Optional
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.rbac import UserRole, has_permission
from app.core.security import decode_access_token
from app.db.session import get_db

bearer_scheme = HTTPBearer(auto_error=False)

DbSession = Annotated[AsyncSession, Depends(get_db)]


@dataclass
class CurrentUser:
    id: Optional[UUID]
    email: str | None
    role: UserRole


def _role_from_claims(claims: dict) -> UserRole:
    raw = str(claims.get("role", "student")).lower()
    try:
        return UserRole(raw)
    except ValueError:
        return UserRole.STUDENT


async def get_current_user_optional(
    credentials: Annotated[Optional[HTTPAuthorizationCredentials], Depends(bearer_scheme)],
) -> Optional[CurrentUser]:
    if credentials is None:
        return None
    try:
        claims = decode_access_token(credentials.credentials)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        ) from exc
    sub = claims.get("sub")
    user_id = UUID(sub) if sub else None
    return CurrentUser(
        id=user_id,
        email=claims.get("email"),
        role=_role_from_claims(claims),
    )


async def get_current_user(
    user: Annotated[Optional[CurrentUser], Depends(get_current_user_optional)],
) -> CurrentUser:
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    return user


def require_permission(permission: str):
    async def _checker(user: Annotated[CurrentUser, Depends(get_current_user)]) -> CurrentUser:
        if not has_permission(user.role, permission):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        return user

    return _checker
