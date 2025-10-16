from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import RedisDsn, PostgresDsn


class Settings(BaseSettings):
    """
    Configuration settings for the Celery workers in the Request Network.
    """
    PROJECT_NAME: str = "Request Network Workers"

    # --- Database Settings (needed for worker to connect to DB) ---
    REQUEST_DB_USER: str
    REQUEST_DB_PASSWORD: str
    REQUEST_DB_HOST: str
    REQUEST_DB_PORT: int
    REQUEST_DB_NAME: str

    # Redis URL for Celery broker and backend
    REDIS_URL: RedisDsn = "redis://redis-request:6379/0"

    # Task-specific settings
    EXPORT_SCHEDULE_SECONDS: int = 120  # 2 minutes
    IMPORT_POLL_SECONDS: int = 30
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"  # Ignore extra fields from .env file
    )

settings = Settings()