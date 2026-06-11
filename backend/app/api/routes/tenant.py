from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from app.schemas import TenantConfigResponse
from app.services.tenant import tenant_service

router = APIRouter()


@router.get("/{slug}", response_model=TenantConfigResponse)
async def get_tenant_config(slug: str):
    tenant = tenant_service.get_tenant(slug)
    if slug not in ("demo-university", "north-campus") and tenant.slug == slug:
        pass
    return TenantConfigResponse(
        slug=tenant.slug,
        name=tenant.name,
        primary_color=tenant.primary_color,
        logo_url=tenant.logo_url,
        features=tenant.features,
        theme_css_vars=tenant_service.get_theme_css_vars(slug),
    )


@router.get("/")
async def list_tenants():
    return tenant_service.list_tenants()
