from __future__ import annotations

import secrets
from typing import Annotated, Optional
from urllib.parse import urlencode
from uuid import uuid4

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, Field

from app.core.config import settings
from app.core.deps import CurrentUser, get_current_user
from app.core.security import create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])

# In-memory OIDC state store (use Redis in production)
_oidc_states: dict[str, str] = {}


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


async def _fetch_oidc_config() -> dict:
    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.get(settings.oidc_discovery_url)
        response.raise_for_status()
        return response.json()


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

    oidc = await _fetch_oidc_config()
    state = secrets.token_urlsafe(32)
    _oidc_states[state] = "pending"

    params = {
        "client_id": settings.oidc_client_id,
        "response_type": "code",
        "scope": "openid email profile",
        "redirect_uri": settings.oidc_redirect_uri,
        "state": state,
    }
    auth_url = f"{oidc['authorization_endpoint']}?{urlencode(params)}"
    return RedirectResponse(auth_url)


@router.get("/callback")
async def sso_login_callback(
    code: Optional[str] = Query(default=None),
    state: Optional[str] = Query(default=None),
    error: Optional[str] = Query(default=None),
):
    if error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"SSO error: {error}")
    if not code or not state or state not in _oidc_states:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid OIDC callback")
    del _oidc_states[state]

    oidc = await _fetch_oidc_config()
    token_data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": settings.oidc_redirect_uri,
        "client_id": settings.oidc_client_id,
        "client_secret": settings.oidc_client_secret,
    }

    async with httpx.AsyncClient(timeout=15.0) as client:
        token_resp = await client.post(oidc["token_endpoint"], data=token_data)
        token_resp.raise_for_status()
        tokens = token_resp.json()

        userinfo = {}
        if "access_token" in tokens:
            ui_resp = await client.get(
                oidc["userinfo_endpoint"],
                headers={"Authorization": f"Bearer {tokens['access_token']}"},
            )
            if ui_resp.status_code == 200:
                userinfo = ui_resp.json()

    email = userinfo.get("email", "sso-user@campusos.edu")
    role = userinfo.get("role", "student")
    user_id = userinfo.get("sub", str(uuid4()))
    token = create_access_token(user_id, extra={"role": role, "email": email})

    frontend_url = settings.cors_origin_list[0] if settings.cors_origin_list else "http://localhost:3000"
    return RedirectResponse(f"{frontend_url}/login?token={token}")


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
