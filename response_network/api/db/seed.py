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
                "profile_type": "admin",
                "allowed_indices": '["*"]',
                "is_active": True,
                "daily_request_limit": 1000,
                "monthly_request_limit": 20000,
                "max_results_per_request": 10000,
            },
            {
                "id": str(uuid.uuid4()),
                "username": "basic_user",
                "email": "basic@example.com",
                "hashed_password": hash_password("basic_password123"),
                "profile_type": "basic",
                "allowed_indices": '["products", "articles"]',
                "is_active": True,
                "daily_request_limit": 100,
                "monthly_request_limit": 2000,
                "max_results_per_request": 1000,
            },
            {
                "id": str(uuid.uuid4()),
                "username": "premium_user",
                "email": "premium@example.com",
                "hashed_password": hash_password("premium_password456"),
                "profile_type": "premium",
                "allowed_indices": '["products", "articles", "logs-prod"]',
                "is_active": True,
                "daily_request_limit": 500,
                "monthly_request_limit": 10000,
                "max_results_per_request": 5000,
            },
        ]

        # Using text() for SQL statement to avoid ORM dependency in this script
        user_insert_stmt = text(
            """
            INSERT INTO users (id, username, email, hashed_password, profile_type, allowed_indices, is_active, 
                             daily_request_limit, monthly_request_limit, max_results_per_request)
            VALUES (:id, :username, :email, :hashed_password, :profile_type, :allowed_indices, :is_active,
                   :daily_request_limit, :monthly_request_limit, :max_results_per_request)
            ON CONFLICT (username) DO NOTHING;
            """
        )
        await conn.execute(user_insert_stmt, users_to_create)
        print(f"-> {len(users_to_create)} users created or already exist.")

        # Skip incoming requests for now - they will be created when requests are imported
        print("Skipping sample incoming requests (will be created via file import).")

        await conn.commit()
        print("\n--- Seeding completed successfully! ---")


if __name__ == "__main__":
    # Install required packages if not present
    # pip install sqlalchemy "asyncpg" "python-dotenv" "bcrypt"
    asyncio.run(seed_data())