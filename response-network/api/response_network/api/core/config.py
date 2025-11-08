from pydantic_settings import BaseSettings
from pydantic import RedisDsn, AnyHttpUrl, PostgresDsn, model_validator
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
    RESPONSE_DB_HOST: str = "localhost"  # Changed to localhost for local development
    RESPONSE_DB_PORT: int = 5433  # Using port 5433 as per docker-compose.dev.yml
    RESPONSE_DB_NAME: str = "response_db"
    DATABASE_URL: Optional[PostgresDsn] = None

    @model_validator(mode='before')
    def assemble_db_connection(cls, v: Any) -> Any:
        if isinstance(v, dict) and 'DATABASE_URL' not in v:
            # Get values from v if present, otherwise use the default values defined in the class
            # This ensures that even if .env is not loaded or values are not provided,
            # the validator can still construct the DSN using the class defaults.
            db_user = v.get('RESPONSE_DB_USER', cls.model_fields['RESPONSE_DB_USER'].default)
            db_password = v.get('RESPONSE_DB_PASSWORD', cls.model_fields['RESPONSE_DB_PASSWORD'].default)
            db_host = v.get('RESPONSE_DB_HOST', cls.model_fields['RESPONSE_DB_HOST'].default)
            db_port = v.get('RESPONSE_DB_PORT', cls.model_fields['RESPONSE_DB_PORT'].default)
            db_name = v.get('RESPONSE_DB_NAME', cls.model_fields['RESPONSE_DB_NAME'].default)

            v['DATABASE_URL'] = f"postgresql+asyncpg://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
        return v

    # Secret key for API access
    MONITORING_API_KEY: str = "super-secret-monitoring-key"
    LOG_LEVEL: str = "INFO"
    
    # Development mode flag
    DEV_MODE: bool = True

    # CORS settings
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000"]

    # Redis URL (for Celery stats)
    REDIS_URL: RedisDsn = "redis://localhost:6379/0"

    # Elasticsearch URL for monitoring
    ELASTICSEARCH_URL: AnyHttpUrl = "http://elasticsearch:9200"
    
    # CORS
    # With Caddy as a reverse proxy, requests are same-origin, so complex CORS is not needed.
    # For Cloud Shell development, we need to explicitly allow the frontend's preview URL.
    # Example: ["https://3000-....cloudshell.dev"]
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = ["https://3001-cs-486191814526-default.cs-europe-west4-pear.cloudshell.dev/"]

    class Config:
        # env_file = ".env" # Temporarily disable .env loading to bypass persistent parsing issues
        env_file_encoding = 'utf-8'
        extra = 'ignore'


settings = Settings()