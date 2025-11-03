from typing import List, Union

from pydantic import AnyHttpUrl, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables or a .env file.
    """

    # Application metadata
    PROJECT_NAME: str = "Request Network API"
    API_V1_STR: str = "/api/v1"

    # Logging configuration
    LOG_LEVEL: str = "INFO"
    DEV_LOGGING: bool = False

    # Development mode flag
    DEV_MODE: bool = False

    # CORS settings
    # The value should be a comma-separated list of origins.
    # e.g., "http://localhost:3000,http://127.0.0.1:3000"
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    # Database settings
    DATABASE_URL: PostgresDsn
    DB_ECHO_LOG: bool = False

    # Redis settings
    REDIS_URL: str = "redis://localhost:6379/0"

    # JWT Settings
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRY_MINUTES: int = 60

    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True

    model_config = SettingsConfigDict(
        case_sensitive=True,
        env_file=".env",
        env_file_encoding="utf-8",
        extra="allow"  # Allow extra fields from .env file
    )


settings = Settings()