import asyncio
import os
import sys
import uuid
from datetime import datetime, timezone

import bcrypt
from dotenv import load_dotenv
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

# --- Path Setup ---
# This allows the script to find modules in the 'api' and 'shared' directories.
api_dir = os.path.realpath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, api_dir)
project_root = os.path.realpath(os.path.join(api_dir, "..", ".."))
sys.path.insert(0, project_root)


def get_database_url():
    """Construct the database URL from environment variables."""
    load_dotenv(os.path.join(project_root, ".env"))

    user = os.getenv("RESPONSE_DB_USER", "user")
    password = os.getenv("RESPONSE_DB_PASSWORD", "password")
    host = os.getenv("RESPONSE_DB_HOST", "localhost")
    port = os.getenv("RESPONSE_DB_PORT", "5433")
    db_name = os.getenv("RESPONSE_DB_NAME", "response_db")

    if not all([user, password, host, port, db_name]):
        raise ValueError("One or more database environment variables are not set.")

    return f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{db_name}"


def hash_password(password: str) -> str:
    """Hashes a password using bcrypt."""
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(pwd_bytes, salt)
    return hashed_password.decode('utf-8')


async def seed_data():
    """
    Connects to the database and inserts initial data for development.
    """
    db_url = get_database_url()
    engine = create_async_engine(db_url, echo=True)

    async with engine.connect() as conn:
        print("--- Starting to seed data for response-network ---")

        # --- 1. Create Users ---
        print("Creating users...")
        users_to_create = [
            {
                "id": str(uuid.uuid4()),
                "username": "admin",
                "email": "admin@example.com",
                "hashed_password": hash_password("SuperSecureAdminP@ss!"),
                "full_name": "Admin User",
                "profile_type": "admin",
                "priority": 10,
                "allowed_indices": '["*"]',  # Admin can access all indices
                "is_active": True,
            },
            {
                "id": str(uuid.uuid4()),
                "username": "basic_user",
                "email": "basic@example.com",
                "hashed_password": hash_password("basic_password123"),
                "full_name": "Basic Test User",
                "profile_type": "basic",
                "priority": 5,
                "allowed_indices": '["products", "articles"]',
                "is_active": True,
            },
            {
                "id": str(uuid.uuid4()),
                "username": "premium_user",
                "email": "premium@example.com",
                "hashed_password": hash_password("premium_password456"),
                "full_name": "Premium Test User",
                "profile_type": "premium",
                "priority": 8,
                "allowed_indices": '["products", "articles", "logs-prod"]',
                "is_active": True,
            },
        ]

        # Using text() for SQL statement to avoid ORM dependency in this script
        user_insert_stmt = text(
            """
            INSERT INTO users (id, username, email, hashed_password, full_name, profile_type, priority, allowed_indices, is_active)
            VALUES (:id, :username, :email, :hashed_password, :full_name, :profile_type, :priority, :allowed_indices, :is_active)
            ON CONFLICT (username) DO NOTHING;
            """
        )
        await conn.execute(user_insert_stmt, users_to_create)
        print(f"-> {len(users_to_create)} users created or already exist.")

        # --- 2. Create Incoming Requests ---
        print("Creating sample incoming requests...")
        basic_user_id = users_to_create[1]['id']
        premium_user_id = users_to_create[2]['id']

        requests_to_create = [
            {
                "id": str(uuid.uuid4()),
                "original_request_id": "a1b2c3d4-e5f6-7788-9900-aabbccddeeff",
                "user_id": basic_user_id,
                "query_type": "match",
                "query_params": '{"field": "content", "query": "hello world"}',
                "priority": 5,
                "status": "pending",
            },
            {
                "id": str(uuid.uuid4()),
                "original_request_id": "b2c3d4e5-f6a7-8899-0011-bbccddeeff00",
                "user_id": premium_user_id,
                "query_type": "aggregation",
                "query_params": '{"type": "terms", "field": "category.keyword"}',
                "priority": 8,
                "status": "pending",
            },
            {
                "id": str(uuid.uuid4()),
                "original_request_id": "c3d4e5f6-a7b8-9900-1122-ccddeeff0011",
                "user_id": premium_user_id,
                "query_type": "bool",
                "query_params": '{"must": [{"match": {"title": "test"}}], "filter": [{"term": {"tags": "urgent"}}]}',
                "priority": 9,
                "status": "pending",
            },
        ]

        request_insert_stmt = text(
            """
            INSERT INTO incoming_requests (id, original_request_id, user_id, query_type, query_params, priority, status)
            VALUES (:id, :original_request_id, :user_id, :query_type, :query_params, :priority, :status)
            ON CONFLICT (id) DO NOTHING;
            """
        )
        await conn.execute(request_insert_stmt, requests_to_create)
        print(f"-> {len(requests_to_create)} incoming requests created.")

        await conn.commit()
        print("\n--- Seeding completed successfully! ---")


if __name__ == "__main__":
    # Install required packages if not present
    # pip install sqlalchemy "asyncpg" "python-dotenv" "bcrypt"
    asyncio.run(seed_data())