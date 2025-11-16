from pydantic_settings import BaseSettings
from pydantic import RedisDsn, AnyHttpUrl, PostgresDsn, model_validator
from typing import Optional, Any


class Settings(BaseSettings):
    PROJECT_NAME: str = "Request Network API"
    API_V1_STR: str = "/api/v1"

    # --- Database Settings ---
    DB_USER: str = "user"
    DB_PASSWORD: str = "password"
    DB_HOST: str = "postgres-request"
    DB_PORT: int = 5432
    DB_NAME: str = "requests_db"
    DATABASE_URL: Optional[PostgresDsn] = None

    @model_validator(mode='before')
    def assemble_db_connection(cls, v: Any) -> Any:
        if isinstance(v, dict) and 'DATABASE_URL' not in v:
            v['DATABASE_URL'] = str(PostgresDsn.build(
                scheme="postgresql+asyncpg",
                username=v.get('DB_USER'),
                password=v.get('DB_PASSWORD'),
                host=v.get('DB_HOST'),
                port=int(v.get('DB_PORT')),
                path=f"{v.get('DB_NAME') or ''}",
            ))
        return v

    # Secret key for JWT
    SECRET_KEY: str = "change-this-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    LOG_LEVEL: str = "INFO"
    DB_ECHO_LOG: bool = False

    # Redis URL (for Celery stats)
    REDIS_URL: RedisDsn = "redis://localhost:6379/0"

    # Elasticsearch URL for monitoring
    # ELASTICSEARCH_URL: AnyHttpUrl = "http://elasticsearch:9200" # Not used in Request Network
    
    # Celery Configuration
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/1"
    
    # Import/Export directories
    IMPORT_DIR: str = "imports"
    EXPORT_DIR: str = "exports"
    
    # CORS
    BACKEND_CORS_ORIGINS: list[str] = ["http://localhost:3001"]

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'
        extra = 'ignore'


settings = Settings()