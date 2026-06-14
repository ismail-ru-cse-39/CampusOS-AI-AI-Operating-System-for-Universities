from __future__ import annotations

import hashlib
import logging
import time
from dataclasses import dataclass
from datetime import date
from typing import Any, Optional

from app.core.config import settings

logger = logging.getLogger(__name__)

CACHE_TTL_SECONDS = 3600


class UsageLimitExceeded(Exception):
    """Raised when a university or user exceeds their LLM usage allowance."""

    def __init__(self, message: str, limit_type: str = "daily_llm_calls"):
        super().__init__(message)
        self.limit_type = limit_type


@dataclass(frozen=True)
class PlanLimits:
    daily_llm_calls: int
    max_tokens_per_call: int
    llm_synthesis_enabled: bool
    real_embeddings_enabled: bool


PLAN_LIMITS: dict[str, PlanLimits] = {
    "free": PlanLimits(
        daily_llm_calls=0,
        max_tokens_per_call=0,
        llm_synthesis_enabled=False,
        real_embeddings_enabled=False,
    ),
    "starter": PlanLimits(
        daily_llm_calls=500,
        max_tokens_per_call=1000,
        llm_synthesis_enabled=True,
        real_embeddings_enabled=True,
    ),
    "professional": PlanLimits(
        daily_llm_calls=5000,
        max_tokens_per_call=2000,
        llm_synthesis_enabled=True,
        real_embeddings_enabled=True,
    ),
    "enterprise": PlanLimits(
        daily_llm_calls=50000,
        max_tokens_per_call=4000,
        llm_synthesis_enabled=True,
        real_embeddings_enabled=True,
    ),
}

# Per-role daily LLM call caps (effective = min(plan limit, role cap)).
ROLE_DAILY_LLM_CAPS: dict[str, int] = {
    "student": 50,
    "faculty": 200,
    "admin": 500,
    "admissions": 100,
    "career_services": 100,
    "executive": 150,
}


@dataclass
class EffectiveLimits:
    plan: str
    role: str
    daily_llm_calls_university: int
    daily_llm_calls_user: int
    max_tokens_per_call: int
    llm_synthesis_enabled: bool
    real_embeddings_enabled: bool


@dataclass
class LLMUsageContext:
    university_id: str
    user_role: str
    plan: str
    user_id: Optional[str] = None


def _today() -> str:
    return date.today().isoformat()


def _calls_key(university_id: str, user_id: str, day: str) -> str:
    return f"usage:{university_id}:{user_id}:{day}:llm_calls"


def _university_calls_key(university_id: str, day: str) -> str:
    return f"usage:{university_id}:{day}:llm_calls"


def _tokens_key(university_id: str, day: str) -> str:
    return f"usage:{university_id}:{day}:tokens"


def _cache_key(prefix: str, raw: str) -> str:
    digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    return f"cache:{prefix}:{digest}"


class _InMemoryStore:
    def __init__(self) -> None:
        self.counters: dict[str, int] = {}
        self.cache: dict[str, tuple[Any, float]] = {}

    def get_int(self, key: str) -> int:
        return self.counters.get(key, 0)

    def incr(self, key: str, amount: int = 1) -> int:
        value = self.counters.get(key, 0) + amount
        self.counters[key] = value
        return value

    def cache_get(self, key: str) -> Any | None:
        entry = self.cache.get(key)
        if entry is None:
            return None
        value, expires_at = entry
        if time.time() > expires_at:
            del self.cache[key]
            return None
        return value

    def cache_set(self, key: str, value: Any, ttl: int = CACHE_TTL_SECONDS) -> None:
        self.cache[key] = (value, time.time() + ttl)

    def reset(self) -> None:
        self.counters.clear()
        self.cache.clear()


class UsageLimitService:
    """Plan-tier and role-based LLM usage limits with Redis or in-memory counters."""

    def __init__(self) -> None:
        self._memory = _InMemoryStore()
        self._redis: Any | None = None
        self._redis_checked = False

    def _redis_client(self) -> Any | None:
        if self._redis_checked:
            return self._redis
        self._redis_checked = True
        if not settings.redis_url:
            return None
        try:
            import redis

            client = redis.from_url(settings.redis_url, decode_responses=True)
            client.ping()
            self._redis = client
            logger.info("Usage counters using Redis at %s", settings.redis_url)
        except Exception as exc:
            logger.debug("Redis unavailable for usage limits, using in-memory store: %s", exc)
            self._redis = None
        return self._redis

    def reset_counters(self) -> None:
        """Clear in-memory counters (for tests)."""
        self._memory.reset()

    def resolve_plan(self, plan: Optional[str] = None, university_slug: Optional[str] = None) -> str:
        if plan:
            normalized = plan.lower().strip()
            if normalized in PLAN_LIMITS:
                return normalized
        if university_slug:
            from app.services.tenant import tenant_service

            tenant = tenant_service.get_tenant(university_slug)
            if tenant.plan in PLAN_LIMITS:
                return tenant.plan
        default = settings.default_university_plan.lower().strip()
        return default if default in PLAN_LIMITS else "starter"

    def get_effective_limits(self, plan: str, role: str) -> EffectiveLimits:
        normalized_plan = self.resolve_plan(plan)
        normalized_role = role.lower().strip()
        base = PLAN_LIMITS[normalized_plan]
        role_cap = ROLE_DAILY_LLM_CAPS.get(normalized_role, base.daily_llm_calls)
        university_cap = min(base.daily_llm_calls, settings.usage_hard_cap_daily_llm_calls)
        user_cap = min(university_cap, role_cap)
        return EffectiveLimits(
            plan=normalized_plan,
            role=normalized_role,
            daily_llm_calls_university=university_cap,
            daily_llm_calls_user=user_cap,
            max_tokens_per_call=base.max_tokens_per_call,
            llm_synthesis_enabled=base.llm_synthesis_enabled,
            real_embeddings_enabled=base.real_embeddings_enabled,
        )

    def _get_counter(self, key: str) -> int:
        client = self._redis_client()
        if client is not None:
            try:
                value = client.get(key)
                return int(value) if value is not None else 0
            except Exception as exc:
                logger.warning("Redis get failed for %s: %s", key, exc)
        return self._memory.get_int(key)

    def _incr_counter(self, key: str, amount: int = 1) -> int:
        client = self._redis_client()
        if client is not None:
            try:
                return int(client.incrby(key, amount))
            except Exception as exc:
                logger.warning("Redis incr failed for %s: %s", key, exc)
        return self._memory.incr(key, amount)

    def get_usage_snapshot(
        self,
        university_id: str,
        user_id: Optional[str],
        plan: str,
        role: str,
    ) -> dict[str, Any]:
        limits = self.get_effective_limits(plan, role)
        day = _today()
        uid = user_id or "anonymous"
        return {
            "plan": limits.plan,
            "role": limits.role,
            "university_calls_today": self._get_counter(_university_calls_key(university_id, day)),
            "user_calls_today": self._get_counter(_calls_key(university_id, uid, day)),
            "tokens_today": self._get_counter(_tokens_key(university_id, day)),
            "limits": {
                "daily_llm_calls_university": limits.daily_llm_calls_university,
                "daily_llm_calls_user": limits.daily_llm_calls_user,
                "max_tokens_per_call": limits.max_tokens_per_call,
                "llm_synthesis_enabled": limits.llm_synthesis_enabled,
                "real_embeddings_enabled": limits.real_embeddings_enabled,
            },
        }

    def check_can_make_llm_call(self, context: LLMUsageContext) -> EffectiveLimits:
        limits = self.get_effective_limits(context.plan, context.user_role)
        if limits.daily_llm_calls_university <= 0:
            raise UsageLimitExceeded(
                "LLM usage is not available on the free plan. Upgrade to enable AI responses.",
                limit_type="plan",
            )

        day = _today()
        uid = context.user_id or "anonymous"
        university_calls = self._get_counter(_university_calls_key(context.university_id, day))
        user_calls = self._get_counter(_calls_key(context.university_id, uid, day))

        if university_calls >= limits.daily_llm_calls_university:
            raise UsageLimitExceeded(
                f"Daily LLM call limit reached for this university "
                f"({limits.daily_llm_calls_university}/day). Try again tomorrow.",
                limit_type="university_daily",
            )
        if user_calls >= limits.daily_llm_calls_user:
            raise UsageLimitExceeded(
                f"Daily LLM call limit reached for your role "
                f"({limits.daily_llm_calls_user}/day). Try again tomorrow.",
                limit_type="user_daily",
            )
        return limits

    def record_llm_usage(
        self,
        context: LLMUsageContext,
        tokens_used: int = 0,
    ) -> None:
        day = _today()
        uid = context.user_id or "anonymous"
        self._incr_counter(_calls_key(context.university_id, uid, day))
        self._incr_counter(_university_calls_key(context.university_id, day))
        if tokens_used > 0:
            self._incr_counter(_tokens_key(context.university_id, day), tokens_used)

    def cache_get(self, prefix: str, raw_key: str) -> Any | None:
        key = _cache_key(prefix, raw_key)
        client = self._redis_client()
        if client is not None:
            try:
                import json

                payload = client.get(key)
                if payload is not None:
                    return json.loads(payload)
            except Exception as exc:
                logger.debug("Redis cache get failed: %s", exc)
        return self._memory.cache_get(key)

    def cache_set(self, prefix: str, raw_key: str, value: Any, ttl: int = CACHE_TTL_SECONDS) -> None:
        key = _cache_key(prefix, raw_key)
        client = self._redis_client()
        if client is not None:
            try:
                import json

                client.setex(key, ttl, json.dumps(value))
                return
            except Exception as exc:
                logger.debug("Redis cache set failed: %s", exc)
        self._memory.cache_set(key, value, ttl)


usage_limit_service = UsageLimitService()
