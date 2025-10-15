from pydantic_settings import BaseSettings
from pydantic import RedisDsn, AnyHttpUrl


class Settings(BaseSettings):
    PROJECT_NAME: str = "Response Network Monitoring API"
    API_V1_STR: str = "/api/v1"

    # Secret key for API access
    MONITORING_API_KEY: str = "super-secret-monitoring-key"

    # Database URL for async connection
    DATABASE_URL: str = "postgresql+asyncpg://user:password@postgres-response:5432/response_db"

    # Redis URL (for Celery stats)
    REDIS_URL: RedisDsn = "redis://redis-response:6379/0"

    # Elasticsearch URL for monitoring
    ELASTICSEARCH_URL: AnyHttpUrl = "http://elasticsearch:9200"

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'

settings = Settings()