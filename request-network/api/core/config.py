import os
from pydantic_settings import BaseSettings
from pydantic import RedisDsn, AnyHttpUrl, PostgresDsn, model_validator
from typing import Optional, Any


class Settings(BaseSettings):
    PROJECT_NAME: str = "Request Network API"
    API_V1_STR: str = "/api/v1"

    # --- Database Settings ---
    DATABASE_URL: str = "sqlite+aiosqlite:///./test.db"

    # Secret key for JWT
    SECRET_KEY: str = "change-this-secret-key"
    LOG_LEVEL: str = "INFO"

    # Redis URL (for Celery stats)
    REDIS_URL: str = "redis://localhost:6379/0"

    # Elasticsearch URL for monitoring
    # ELASTICSEARCH_URL: AnyHttpUrl = "http://elasticsearch:9200" # Not used in Request Network
    
    # CORS
    BACKEND_CORS_ORIGINS: list[str] = ["http://localhost:3001"]

    class Config:
        env_file = ".env.test" if os.getenv("TESTING") else ".env"
        env_file_encoding = 'utf-8'
        extra = 'ignore'


settings = Settings()