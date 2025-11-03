import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import RedisDsn, AnyHttpUrl, PostgresDsn, model_validator
from typing import Optional, Any


class Settings(BaseSettings):
    """Application settings loaded from environment variables or a .env file."""

    # Application metadata
    PROJECT_NAME: str = "Request Network API"
    API_V1_STR: str = "/api/v1"

    # Logging configuration
    LOG_LEVEL: str = "INFO"
    DEV_LOGGING: bool = False

    # Development mode flag
    DEV_MODE: bool = False

    # Database settings
    DATABASE_URL: PostgresDsn = "sqlite+aiosqlite:///./test.db"
    DB_ECHO_LOG: bool = False

    # Redis settings
    REDIS_URL: str = "redis://localhost:6379/0"

    # JWT Settings
    SECRET_KEY: str = "change-this-secret-key"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRY_MINUTES: int = 60

    # CORS settings
    BACKEND_CORS_ORIGINS: list[AnyHttpUrl] = ["http://localhost:3001"]

    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True

    model_config = SettingsConfigDict(
        case_sensitive=True,
        env_file=".env.test" if os.getenv("TESTING") else ".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()