from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import RedisDsn, AnyHttpUrl, PostgresDsn
from typing import Optional, Any
from pathlib import Path


class Settings(BaseSettings):
    PROJECT_NAME: str = "Request Network API"
    API_V1_STR: str = "/api/v1"

    # --- Database Settings ---
    DB_USER: str = "requser"
    DB_PASSWORD: str = "reqpassword123"
    DB_HOST: str = "postgres-request"
    DB_PORT: int = 5432
    DB_NAME: str = "request_network_db"

    # Secret key for JWT
    SECRET_KEY: str = "change-this-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    LOG_LEVEL: str = "INFO"
    DB_ECHO_LOG: bool = False

    # Redis URL (for Celery stats)
    REDIS_URL: RedisDsn = "redis://redis-request:6379/0"

    # Elasticsearch URL for monitoring
    # ELASTICSEARCH_URL: AnyHttpUrl = "http://elasticsearch:9200" # Not used in Request Network
    
    # Celery Configuration
    CELERY_BROKER_URL: str = "redis://redis-request:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://redis-request:6379/1"
    
    # Import/Export directories
    IMPORT_DIR: str = "/app/imports"
    EXPORT_DIR: str = "/app/exports"
    
    # CORS
    BACKEND_CORS_ORIGINS: list[str] = ["http://localhost:3001"]

    model_config = SettingsConfigDict(
        env_file="/app/.env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


settings = Settings()