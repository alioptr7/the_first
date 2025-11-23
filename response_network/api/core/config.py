"""تنظیمات API"""
from typing import List

from pydantic import AnyHttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """تنظیمات برنامه"""
    PROJECT_NAME: str = "Response Network Monitoring API"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "your-secret-key-change-this-in-production-min-32-chars"
    LOG_LEVEL: str = "DEBUG"
    DEV_MODE: bool = True
    MONITORING_API_KEY: str = "admin-secret-key-change-this"
    ALGORITHM: str = "HS256"  # الگوریتم رمزنگاری برای JWT
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30  # مدت زمان اعتبار توکن دسترسی به دقیقه

    # CORS
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = ["http://localhost:3000"]

    # تنظیمات پایگاه داده
    DATABASE_URL: str

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

    # تنظیمات Claude Sonnet
    ENABLE_CLAUDE_SONNET_3_5: bool = True  # فعال‌سازی Claude Sonnet 3.5 برای همه کاربران

    @property
    def ELASTICSEARCH_CONNECTION_URL(self) -> str:
        """آدرس اتصال به Elasticsearch"""
        self.ELASTICSEARCH_URL = f"http://{self.ELASTICSEARCH_HOST}:{self.ELASTICSEARCH_PORT}"
        return self.ELASTICSEARCH_URL



    model_config = SettingsConfigDict(
        env_file="z:/Newfolder/the_first/response-network/api/.env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

settings = Settings()