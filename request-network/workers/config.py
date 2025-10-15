from pydantic_settings import BaseSettings
from pydantic import RedisDsn


class Settings(BaseSettings):
    """
    Configuration settings for the Celery workers in the Request Network.
    """
    PROJECT_NAME: str = "Request Network Workers"
    
    # Redis URL for Celery broker and backend
    REDIS_URL: RedisDsn = "redis://localhost:6379/0"

    # Task-specific settings
    EXPORT_SCHEDULE_SECONDS: int = 120  # 2 minutes
    IMPORT_POLL_SECONDS: int = 30

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'

settings = Settings()