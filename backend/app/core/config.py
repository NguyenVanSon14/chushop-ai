from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "ChủShop AI"
    api_v1_prefix: str = "/api/v1"
    database_url: str = "postgresql+psycopg://chushop:chushop@localhost:5432/chushop"
    secret_key: str = Field(min_length=32)
    access_token_expire_minutes: int = 60
    backend_cors_origins: list[str] = ["http://localhost:3000"]

    llm_provider: str = "mock"
    llm_api_key: str | None = None
    llm_model: str = "gpt-4o-mini"
    llm_base_url: str | None = None

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @field_validator("backend_cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: object) -> object:
        if isinstance(value, str) and not value.startswith("["):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()
