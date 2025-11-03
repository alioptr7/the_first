"""Application settings"""
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings"""
    # Project
    PROJECT_NAME: str = "Request Network"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = True

    # Security
    SECRET_KEY: str = "your-secret-key"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    USE_HTTPS: bool = False

    # Database
    SQLALCHEMY_DATABASE_URI: str = "sqlite+aiosqlite:///./request_network.db"
    TEST_DATABASE_URI: str = "sqlite+aiosqlite:///:memory:"
    DB_ECHO_LOG: bool = False

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000"]

    model_config = SettingsConfigDict(case_sensitive=True)


settings = Settings()