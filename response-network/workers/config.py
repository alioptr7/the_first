from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import RedisDsn, PostgresDsn


class Settings(BaseSettings):
    """
    Configuration settings for the Celery workers in the Response Network.
    """
    PROJECT_NAME: str = "Response Network Workers"

    # --- Database Settings (needed for worker to connect to DB) ---
    RESPONSE_DB_USER: str
    RESPONSE_DB_PASSWORD: str
    RESPONSE_DB_HOST: str
    RESPONSE_DB_PORT: int
    RESPONSE_DB_NAME: str

    # Redis URL for Celery broker and backend
    REDIS_URL: RedisDsn = "redis://localhost:6379/0"

    # Task-specific settings
    EXPORT_SCHEDULE_SECONDS: int = 120  # 2 minutes
    IMPORT_POLL_SECONDS: int = 30
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"  # Ignore extra fields from .env file
    )

    @property
    def celery_broker_url(self) -> str:
        return str(self.REDIS_URL)

    @property
    def celery_result_backend(self) -> str:
        return str(self.REDIS_URL)

settings = Settings()