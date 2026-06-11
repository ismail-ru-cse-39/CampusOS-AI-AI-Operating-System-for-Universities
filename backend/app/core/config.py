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

    # SSO / OIDC (configure when IdP credentials are available)
    oidc_client_id: str = ""
    oidc_client_secret: str = ""
    oidc_discovery_url: str = ""
    oidc_redirect_uri: str = "http://localhost:8000/api/v1/auth/callback"
    auth_dev_login_enabled: bool = True

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def sso_configured(self) -> bool:
        return bool(self.oidc_client_id and self.oidc_discovery_url)


settings = Settings()
