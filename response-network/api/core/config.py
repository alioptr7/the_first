from pydantic import RedisDsn, AnyHttpUrl, PostgresDsn, validator
from pydantic_settings import BaseSettings
from typing import Optional, Any, List


class Settings(BaseSettings):
    PROJECT_NAME: str = "Response Network Monitoring API"
    API_V1_STR: str = "/api/v1"

    # --- Security Settings ---
    SECRET_KEY: str = "a_very_secret_key_for_response_network_admin"  # Change this in production!
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALGORITHM: str = "HS256"

    # --- Database Settings ---
    RESPONSE_DB_USER: str = "user"
    RESPONSE_DB_PASSWORD: str = "password"
    RESPONSE_DB_HOST: str = "localhost"
    RESPONSE_DB_PORT: int = 5433
    RESPONSE_DB_NAME: str = "response_db"
    DATABASE_URL: Optional[PostgresDsn] = None

    @validator('DATABASE_URL', pre=True, allow_reuse=True)
    def assemble_db_connection(cls, v: Optional[str], values: dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
            
        # Get values from values dict, using class defaults if not found
        db_user = values.get('RESPONSE_DB_USER', cls.__fields__['RESPONSE_DB_USER'].default)
        db_password = values.get('RESPONSE_DB_PASSWORD', cls.__fields__['RESPONSE_DB_PASSWORD'].default)
        db_host = values.get('RESPONSE_DB_HOST', cls.__fields__['RESPONSE_DB_HOST'].default)
        db_port = values.get('RESPONSE_DB_PORT', cls.__fields__['RESPONSE_DB_PORT'].default)
        db_name = values.get('RESPONSE_DB_NAME', cls.__fields__['RESPONSE_DB_NAME'].default)

        return f"postgresql+asyncpg://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

    # Secret key for API access
    MONITORING_API_KEY: str = "super-secret-monitoring-key"
    LOG_LEVEL: str = "INFO"
    
    # Development mode flag
    DEV_MODE: bool = True

    # CORS settings
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000"]

    # Redis URL (for Celery stats)
    REDIS_URL: RedisDsn = "redis://localhost:6380/0"

    # Elasticsearch URL for monitoring
    ELASTICSEARCH_URL: AnyHttpUrl = "http://localhost:9200"
    
    # Export directory for settings
    EXPORT_DIR: str = "exports"
    
    # CORS
    # With Caddy as a reverse proxy, requests are same-origin, so complex CORS is not needed.
    # For Cloud Shell development, we need to explicitly allow the frontend's preview URL.
    # Example: ["https://3000-....cloudshell.dev"]
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = ["https://3001-cs-486191814526-default.cs-europe-west4-pear.cloudshell.dev/"]

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'
        extra = 'ignore'


settings = Settings()