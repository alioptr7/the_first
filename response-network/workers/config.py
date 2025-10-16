from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import RedisDsn, AnyHttpUrl, PostgresDsn


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

    # Redis URL for Celery broker and backend (Response Network specific)
    REDIS_URL: RedisDsn = "redis://redis-response:6379/0"

    # Elasticsearch settings
    ELASTICSEARCH_URL: AnyHttpUrl = "http://elasticsearch:9200"
    ELASTICSEARCH_QUERY_TIMEOUT: int = 30  # seconds
    ELASTICSEARCH_MAX_RESULT_SIZE: int = 1000

    # Task-specific settings from TODO.md
    IMPORT_REQUESTS_POLL_SECONDS: int = 30
    EXPORT_RESULTS_SCHEDULE_SECONDS: int = 120  # 2 minutes
    CACHE_MAINTENANCE_SCHEDULE_SECONDS: int = 3600  # 1 hour
    SYSTEM_MONITORING_SCHEDULE_SECONDS: int = 300  # 5 minutes

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"  # Ignore extra fields from .env file
    )

settings = Settings()