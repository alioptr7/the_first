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

    model_config = SettingsConfigDict(
        case_sensitive=True, env_file=".env", env_file_encoding="utf-8"
    )


settings = Settings()