"""اسکریپت پر کردن دیتابیس با داده‌های اولیه"""
import asyncio
import os
import sys
import uuid
from datetime import datetime, timezone

from dotenv import load_dotenv
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from shared.auth.security import get_password_hash

# --- Path Setup ---
# This allows the script to find modules in the 'api' and 'shared' directories.
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)


def get_database_url():
    """Construct the database URL from environment variables."""
    load_dotenv(os.path.join(project_root, ".env"))

    user = os.getenv("REQUEST_DB_USER", "user")
    password = os.getenv("REQUEST_DB_PASSWORD", "password")
    host = os.getenv("REQUEST_DB_HOST", "localhost")
    port = os.getenv("REQUEST_DB_PORT", "5432")
    db_name = os.getenv("REQUEST_DB_NAME", "request_db")

    if not all([user, password, host, port, db_name]):
        raise ValueError("One or more database environment variables are not set.")

    return f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{db_name}"


def hash_password(password: str) -> str:
    """Hashes a password using core hashing module."""
    return get_password_hash(password)


async def seed_data():
    """
    Connects to the database and inserts initial data for development.
    """
    db_url = get_database_url()
    engine = create_async_engine(db_url, echo=True)

    async with engine.connect() as conn:
        print("--- Starting to seed data for request-network ---")
        
        # First, delete existing data
        print("Deleting existing data...")
        await conn.execute(text("DELETE FROM api_keys"))
        await conn.execute(text("DELETE FROM requests"))
        await conn.execute(text("DELETE FROM users"))
        await conn.commit()
        print("-> Existing data deleted.")

        # --- 1. Create Users ---
        print("Creating users...")
        users_to_create = [
            {
                "id": str(uuid.uuid4()),
                "username": "admin",
                "email": "admin@example.com",
                "hashed_password": hash_password("SuperSecureAdminP@ss!"),
                "is_active": True,
                "is_admin": True,
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
            },
            {
                "id": str(uuid.uuid4()),
                "username": "basic_user",
                "email": "basic@example.com",
                "hashed_password": hash_password("basic_password123"),
                "is_active": True,
                "is_admin": False,
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
            },
            {
                "id": str(uuid.uuid4()),
                "username": "premium_user",
                "email": "premium@example.com",
                "hashed_password": hash_password("premium_password456"),
                "is_active": True,
                "is_admin": False,
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
            },
        ]

        # Using text() for SQL statement to avoid ORM dependency in this script
        user_insert_stmt = text(
            """
            INSERT INTO users (id, username, email, hashed_password, is_active, is_admin, created_at, updated_at)
            VALUES (:id, :username, :email, :hashed_password, :is_active, :is_admin, :created_at, :updated_at);
            """
        )
        await conn.execute(user_insert_stmt, users_to_create)
        print(f"-> {len(users_to_create)} users created.")

        # --- 2. Create API Keys ---
        print("Creating API keys...")
        api_keys_to_create = [
            {
                "id": str(uuid.uuid4()),
                "user_id": users_to_create[0]["id"],  # admin
                "key_hash": str(uuid.uuid4()),
                "prefix": "admin",
                "name": "Admin API Key",
                "is_active": True,
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
            },
            {
                "id": str(uuid.uuid4()),
                "user_id": users_to_create[1]["id"],  # basic_user
                "key_hash": str(uuid.uuid4()),
                "prefix": "basic",
                "name": "Basic User API Key",
                "is_active": True,
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
            },
            {
                "id": str(uuid.uuid4()),
                "user_id": users_to_create[2]["id"],  # premium_user
                "key_hash": str(uuid.uuid4()),
                "prefix": "premium",
                "name": "Premium User API Key",
                "is_active": True,
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
            },
        ]

        api_key_insert_stmt = text(
            """
            INSERT INTO api_keys (id, user_id, key_hash, prefix, name, is_active, created_at, updated_at)
            VALUES (:id, :user_id, :key_hash, :prefix, :name, :is_active, :created_at, :updated_at);
            """
        )
        await conn.execute(api_key_insert_stmt, api_keys_to_create)
        print(f"-> {len(api_keys_to_create)} API keys created.")

        # --- 3. Create Sample Requests ---
        print("Creating sample requests...")
        requests_to_create = [
            {
                "id": str(uuid.uuid4()),
                "user_id": users_to_create[1]["id"],  # basic_user
                "name": "Basic Match Query",
                "query_type": "match",
                "query_params": '{"field": "content", "query": "hello world"}',
                "priority": 5,
                "status": "pending",
                "retry_count": 0,
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
            },
            {
                "id": str(uuid.uuid4()),
                "user_id": users_to_create[2]["id"],  # premium_user
                "name": "Premium Aggregation Query",
                "query_type": "aggregation",
                "query_params": '{"type": "terms", "field": "category.keyword"}',
                "priority": 8,
                "status": "pending",
                "retry_count": 0,
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
            },
            {
                "id": str(uuid.uuid4()),
                "user_id": users_to_create[2]["id"],  # premium_user
                "name": "Premium Bool Query",
                "query_type": "bool",
                "query_params": '{"must": [{"match": {"title": "test"}}], "filter": [{"term": {"tags": "urgent"}}]}',
                "priority": 9,
                "status": "pending",
                "retry_count": 0,
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
            },
        ]

        request_insert_stmt = text(
            """
            INSERT INTO requests (id, user_id, name, query_type, query_params, priority, status, retry_count, created_at, updated_at)
            VALUES (:id, :user_id, :name, :query_type, :query_params, :priority, :status, :retry_count, :created_at, :updated_at);
            """
        )
        await conn.execute(request_insert_stmt, requests_to_create)
        print(f"-> {len(requests_to_create)} requests created.")

        await conn.commit()
        print("\n--- Seeding completed successfully! ---")


if __name__ == "__main__":
    asyncio.run(seed_data())