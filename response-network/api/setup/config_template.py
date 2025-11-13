"""
Configuration template for Response Network setup.
This file is used to generate the actual configuration when needed.
"""

# Database Configuration
DATABASE_CONFIG = {
    "RESPONSE_DB_USER": "user",
    "RESPONSE_DB_PASSWORD": "password",
    "RESPONSE_DB_HOST": "localhost",
    "RESPONSE_DB_PORT": 5433,
    "RESPONSE_DB_NAME": "response_db",
}

# Redis Configuration
REDIS_CONFIG = {
    "REDIS_HOST": "localhost",
    "REDIS_PORT": 6380,
    "REDIS_DB": 0,
    "REDIS_URL": "redis://localhost:6380/0",
}

# Elasticsearch Configuration
ELASTICSEARCH_CONFIG = {
    "ES_HOST": "localhost",
    "ES_PORT": 9200,
    "ES_URL": "http://localhost:9200",
}

# API Configuration
API_CONFIG = {
    "PROJECT_NAME": "Response Network Monitoring API",
    "API_HOST": "127.0.0.1",
    "API_PORT": 8000,
    "SECRET_KEY": "a_very_secret_key_for_response_network_admin",
    "ACCESS_TOKEN_EXPIRE_MINUTES": 30,
    "ALGORITHM": "HS256",
}

# Admin User Configuration
ADMIN_USER_CONFIG = {
    "username": "admin",
    "email": "admin@response-network.local",
    "password": "admin123",  # Change this in production!
}

# Export Configuration
EXPORT_CONFIG = {
    "EXPORT_DIR": "exports",
    "EXPORT_SETTINGS_DIR": "exports/settings",
    "EXPORT_RESULTS_DIR": "exports/results",
}

# Celery Configuration
CELERY_CONFIG = {
    "CELERY_BROKER_URL": "redis://localhost:6380/0",
    "CELERY_RESULT_BACKEND": "redis://localhost:6380/1",
}
