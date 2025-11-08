"""تنظیمات شبکه پاسخ"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import RedisDsn, PostgresDsn


"""تنظیمات برنامه"""
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """تنظیمات برنامه"""
    # تنظیمات پایگاه داده
    RESPONSE_DB_USER: str = "user"
    RESPONSE_DB_PASSWORD: str = "password"
    RESPONSE_DB_HOST: str = "localhost"
    RESPONSE_DB_PORT: str = "5433"
    RESPONSE_DB_NAME: str = "response_db"

    # تنظیمات Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6380
    REDIS_DB: int = 0

    # تنظیمات شبکه درخواست
    REQUEST_NETWORK_API_URL: str = "http://localhost:8000"
    REQUEST_NETWORK_API_KEY: str = "your-api-key-here"

    @property
    def RESPONSE_DB_URL(self) -> str:
        """آدرس اتصال به پایگاه داده"""
        return f"postgresql+psycopg2://{self.RESPONSE_DB_USER}:{self.RESPONSE_DB_PASSWORD}@{self.RESPONSE_DB_HOST}:{self.RESPONSE_DB_PORT}/{self.RESPONSE_DB_NAME}"

    @property
    def REDIS_URL(self) -> str:
        """آدرس اتصال به Redis"""
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    class Config:
        """تنظیمات مدل"""
        env_file = ".env"
        case_sensitive = True
        extra = "allow"

settings = Settings()