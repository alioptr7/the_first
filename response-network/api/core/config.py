from pydantic_settings import BaseSettings
from pydantic import RedisDsn, AnyHttpUrl, PostgresDsn, model_validator
from typing import Optional, Any


class Settings(BaseSettings):
    PROJECT_NAME: str = "Response Network Monitoring API"
    API_V1_STR: str = "/api/v1"

    # --- Database Settings ---
    RESPONSE_DB_USER: str = "user"
    RESPONSE_DB_PASSWORD: str = "password"
    RESPONSE_DB_HOST: str = "postgres-response"
    RESPONSE_DB_PORT: int = 5432
    RESPONSE_DB_NAME: str = "response_db"
    DATABASE_URL: Optional[PostgresDsn] = None

    @model_validator(mode='before')
    def assemble_db_connection(cls, v: Any) -> Any:
        if isinstance(v, dict) and 'DATABASE_URL' not in v:
            v['DATABASE_URL'] = str(PostgresDsn.build(
                scheme="postgresql+asyncpg",
                username=v.get('RESPONSE_DB_USER'),
                password=v.get('RESPONSE_DB_PASSWORD'),
                host=v.get('RESPONSE_DB_HOST'),
                port=int(v.get('RESPONSE_DB_PORT')),
                path=f"{v.get('RESPONSE_DB_NAME') or ''}",
            ))
        return v

    # Secret key for API access
    MONITORING_API_KEY: str = "super-secret-monitoring-key"

    # Redis URL (for Celery stats)
    REDIS_URL: RedisDsn = "redis://redis-response:6379/0"

    # Elasticsearch URL for monitoring
    ELASTICSEARCH_URL: AnyHttpUrl = "http://elasticsearch:9200"

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'


settings = Settings()