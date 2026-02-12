from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "budget-platform"
    app_env: str = "dev"
    log_level: str = "INFO"
    log_file: str = "logs/app.log"
    database_url: str = "sqlite:///./budget.db"
    rabbitmq_enabled: bool = False
    rabbitmq_url: str = "amqp://guest:guest@localhost:5672/"
    api_base_url: str = "http://127.0.0.1:8000"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
