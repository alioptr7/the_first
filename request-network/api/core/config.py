from typing import List
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

    # Database settings
    DATABASE_URL: PostgresDsn
    DB_ECHO_LOG: bool = False

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # JWT Settings
    SECRET_KEY: str = "change-this-secret-key-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRY_MINUTES: int = 60

    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True

    # CORS settings
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000"]

    model_config = SettingsConfigDict(
        case_sensitive=True,
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
