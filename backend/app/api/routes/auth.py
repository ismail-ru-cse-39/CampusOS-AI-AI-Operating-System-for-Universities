from __future__ import annotations

from typing import Annotated, Optional
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from app.core.config import settings
from app.core.deps import CurrentUser, get_current_user
from app.core.security import create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])


class DevTokenRequest(BaseModel):
    email: str = Field(default="demo.student@campusos.edu")
    role: str = Field(default="student")
    user_id: Optional[str] = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class AuthStatusResponse(BaseModel):
    sso_configured: bool
    dev_login_enabled: bool
    message: str


class MeResponse(BaseModel):
    user_id: Optional[str]
    email: Optional[str]
    role: str


@router.get("/status", response_model=AuthStatusResponse)
async def auth_status() -> AuthStatusResponse:
    if settings.sso_configured:
        msg = "SSO is configured; use /auth/login to start the OIDC flow."
    else:
        msg = "SSO not configured. Use dev token endpoint in development or configure OIDC env vars."
    return AuthStatusResponse(
        sso_configured=settings.sso_configured,
        dev_login_enabled=settings.auth_dev_login_enabled and settings.environment == "development",
        message=msg,
    )


@router.get("/login")
async def sso_login_start():
    if not settings.sso_configured:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="SSO is not configured. Set OIDC_CLIENT_ID and OIDC_DISCOVERY_URL.",
        )
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="OIDC authorization redirect is not wired yet (requires IdP credentials and callback handler).",
    )


@router.get("/callback")
async def sso_login_callback():
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="OIDC callback handler pending IdP configuration.",
    )


@router.post("/dev-token", response_model=TokenResponse)
async def dev_token(body: DevTokenRequest) -> TokenResponse:
    if settings.environment != "development" or not settings.auth_dev_login_enabled:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Dev login is disabled")
    user_id = body.user_id or str(uuid4())
    token = create_access_token(
        user_id,
        extra={"role": body.role, "email": body.email},
    )
    return TokenResponse(access_token=token)


@router.get("/me", response_model=MeResponse)
async def auth_me(user: Annotated[CurrentUser, Depends(get_current_user)]) -> MeResponse:  # type: ignore[assignment]
    return MeResponse(
        user_id=str(user.id) if user.id else None,
        email=user.email,
        role=user.role.value,
    )


@router.post("/logout")
async def logout() -> dict[str, str]:
    return {"status": "ok", "message": "Client should discard the JWT (stateless logout)."}
