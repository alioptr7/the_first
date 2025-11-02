"""تنظیمات شبکه درخواست"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import RedisDsn, PostgresDsn


class Settings(BaseSettings):
    """تنظیمات برنامه"""
    PROJECT_NAME: str = "Request Network Workers"

    # تنظیمات پایگاه داده
    REQUEST_DB_USER: str
    REQUEST_DB_PASSWORD: str
    REQUEST_DB_HOST: str
    REQUEST_DB_PORT: int
    REQUEST_DB_NAME: str

    @property
    def REQUEST_DB_URL(self) -> str:
        """ساخت URL اتصال به پایگاه داده"""
        return (
            f"postgresql://{self.REQUEST_DB_USER}:{self.REQUEST_DB_PASSWORD}"
            f"@{self.REQUEST_DB_HOST}:{self.REQUEST_DB_PORT}/{self.REQUEST_DB_NAME}"
        )

    # تنظیمات Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0

    @property
    def REDIS_URL(self) -> str:
        """ساخت URL اتصال به Redis"""
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

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