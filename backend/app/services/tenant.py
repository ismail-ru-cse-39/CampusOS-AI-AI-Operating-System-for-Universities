from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class TenantBranding:
    slug: str
    name: str
    primary_color: str = "#2563eb"
    secondary_color: str = "#1e40af"
    logo_url: str | None = None
    tagline: str = "The AI Operating System for Higher Education"
    support_email: str = "support@campusos.edu"
    plan: str = "starter"
    features: dict[str, bool] = field(default_factory=dict)


DEFAULT_TENANTS: dict[str, TenantBranding] = {
    "demo-university": TenantBranding(
        slug="demo-university",
        name="Demo University",
        primary_color="#2563eb",
        tagline="Excellence in Education",
        plan="professional",
        features={"chat": True, "dashboard": True, "voice": False, "graph": True},
    ),
    "north-campus": TenantBranding(
        slug="north-campus",
        name="North Campus Institute",
        primary_color="#059669",
        tagline="Innovation Starts Here",
        plan="starter",
        features={"chat": True, "dashboard": True, "voice": False, "graph": False},
    ),
}


class TenantService:
    """Multi-tenant branding and config isolation."""

    def get_tenant(self, slug: str) -> TenantBranding:
        return DEFAULT_TENANTS.get(
            slug,
            TenantBranding(slug=slug, name=slug.replace("-", " ").title()),
        )

    def list_tenants(self) -> list[dict[str, Any]]:
        return [
            {
                "slug": t.slug,
                "name": t.name,
                "primary_color": t.primary_color,
                "logo_url": t.logo_url,
                "plan": t.plan,
                "features": t.features,
            }
            for t in DEFAULT_TENANTS.values()
        ]

    def get_theme_css_vars(self, slug: str) -> dict[str, str]:
        tenant = self.get_tenant(slug)
        return {
            "--primary": tenant.primary_color,
            "--secondary": tenant.secondary_color,
        }


tenant_service = TenantService()
