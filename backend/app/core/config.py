from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    port: int = 8000
    database_url: str = "postgresql+asyncpg://campusos:campusos@localhost:5432/campusos"
    redis_url: str = "redis://localhost:6379/0"
    jwt_secret: str = "change-me-in-production"
    cors_origins: str = "http://localhost:3000"
    environment: str = "development"
    openai_api_key: str = ""
    llm_provider: str = "openai"
    llm_model: str = "gpt-4o-mini"

    # LLM usage limits (plan tiers resolved via tenant slug or DEFAULT_UNIVERSITY_PLAN)
    default_university_plan: str = "starter"
    default_university_slug: str = "demo-university"
    usage_hard_cap_daily_llm_calls: int = 100_000

    # SSO / OIDC (configure when IdP credentials are available)
    oidc_client_id: str = ""
    oidc_client_secret: str = ""
    oidc_discovery_url: str = ""
    oidc_redirect_uri: str = "http://localhost:8000/api/v1/auth/callback"
    auth_dev_login_enabled: bool = True

    # Email (SMTP)
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from: str = "noreply@campusos.edu"

    # SMS (Twilio)
    twilio_account_sid: str = ""
    twilio_auth_token: str = ""
    twilio_from_number: str = ""

    # Webhooks
    teams_webhook_url: str = ""
    slack_webhook_url: str = ""

    # Neo4j (optional graph backend)
    neo4j_uri: str = ""
    neo4j_user: str = "neo4j"
    neo4j_password: str = ""

    # Worker
    celery_enabled: bool = False

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def sso_configured(self) -> bool:
        return bool(self.oidc_client_id and self.oidc_discovery_url)

    @property
    def smtp_configured(self) -> bool:
        return bool(self.smtp_host and self.smtp_from)

    @property
    def twilio_configured(self) -> bool:
        return bool(self.twilio_account_sid and self.twilio_auth_token and self.twilio_from_number)

    @property
    def neo4j_configured(self) -> bool:
        return bool(self.neo4j_uri and self.neo4j_password)


settings = Settings()
