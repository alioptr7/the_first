from pydantic_settings import BaseSettings
from pydantic import RedisDsn, AnyHttpUrl


class Settings(BaseSettings):
    """
    Configuration settings for the Celery workers in the Response Network.
    """
    PROJECT_NAME: str = "Response Network Workers"

    # Redis URL for Celery broker and backend (Response Network specific)
    REDIS_URL: RedisDsn = "redis://localhost:6380/0"

    # Elasticsearch settings
    ELASTICSEARCH_URL: AnyHttpUrl = "http://elasticsearch:9200"
    ELASTICSEARCH_QUERY_TIMEOUT: int = 30  # seconds
    ELASTICSEARCH_MAX_RESULT_SIZE: int = 1000

    # Task-specific settings from TODO.md
    IMPORT_REQUESTS_POLL_SECONDS: int = 30
    EXPORT_RESULTS_SCHEDULE_SECONDS: int = 120  # 2 minutes
    CACHE_MAINTENANCE_SCHEDULE_SECONDS: int = 3600  # 1 hour
    SYSTEM_MONITORING_SCHEDULE_SECONDS: int = 300  # 5 minutes

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'

settings = Settings()