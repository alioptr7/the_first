"""تنظیمات API"""
from typing import List

from pydantic import AnyHttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """تنظیمات برنامه"""
    PROJECT_NAME: str = "Response Network Monitoring API"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "your-secret-key-change-this-in-production-min-32-chars"
    LOG_LEVEL: str = "INFO"
    MONITORING_API_KEY: str = "admin-secret-key-change-this"
    ALGORITHM: str = "HS256"  # الگوریتم رمزنگاری برای JWT
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30  # مدت زمان اعتبار توکن دسترسی به دقیقه

    # CORS
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = ["http://localhost:3000"]

    # تنظیمات پایگاه داده
    RESPONSE_DB_USER: str = "user"
    RESPONSE_DB_PASSWORD: str = "password"
    RESPONSE_DB_HOST: str = "localhost"
    RESPONSE_DB_PORT: str = "5433"
    RESPONSE_DB_NAME: str = "response_db"
    DATABASE_URL: str = ""

    @property
    def DATABASE_CONNECTION_URL(self) -> str:
        """آدرس اتصال به پایگاه داده"""
        self.DATABASE_URL = f"postgresql+asyncpg://{self.RESPONSE_DB_USER}:{self.RESPONSE_DB_PASSWORD}@{self.RESPONSE_DB_HOST}:{self.RESPONSE_DB_PORT}/{self.RESPONSE_DB_NAME}"
        return self.DATABASE_URL

    # تنظیمات Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6380
    REDIS_DB: int = 0
    REDIS_URL: str = ""

    @property
    def REDIS_CONNECTION_URL(self) -> str:
        """آدرس اتصال به Redis"""
        self.REDIS_URL = f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return self.REDIS_URL

    # تنظیمات Elasticsearch
    ELASTICSEARCH_HOST: str = "localhost"
    ELASTICSEARCH_PORT: int = 9200
    ELASTICSEARCH_URL: str = ""
    ELASTICSEARCH_QUERY_TIMEOUT: int = 30  # زمان انتظار برای پاسخ به ثانیه
    ELASTICSEARCH_MAX_RESULT_SIZE: int = 1000  # حداکثر تعداد نتایج

    @property
    def ELASTICSEARCH_CONNECTION_URL(self) -> str:
        """آدرس اتصال به Elasticsearch"""
        self.ELASTICSEARCH_URL = f"http://{self.ELASTICSEARCH_HOST}:{self.ELASTICSEARCH_PORT}"
        return self.ELASTICSEARCH_URL

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="allow"  # اجازه فیلدهای اضافی
    )

settings = Settings()

settings = Settings()