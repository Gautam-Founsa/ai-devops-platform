from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "AI DevOps Platform"
    environment: str = "development"
    api_v1_prefix: str = "/api/v1"
    frontend_origin: str = "http://localhost:3000"

    database_url: str = Field(
        default="postgresql+asyncpg://ai_devops:ai_devops@postgres:5432/ai_devops"
    )
    redis_url: str = "redis://redis:6379/0"

    jwt_secret_key: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    ollama_base_url: str = "http://ollama:11434"
    ollama_model: str = "llama3.1"
    ai_provider: str = "mock"


@lru_cache
def get_settings() -> Settings:
    return Settings()

