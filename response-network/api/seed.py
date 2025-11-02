"""اسکریپت پر کردن دیتابیس با داده‌های اولیه"""
import asyncio
import json
import os
import sys
import uuid
from datetime import datetime, timezone

from dotenv import load_dotenv
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.future import select
from core.hashing import get_password_hash

# --- Path Setup ---
# This allows the script to find modules in the 'api' and 'shared' directories.
api_dir = os.path.realpath(os.path.dirname(__file__))
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
    """Hashes a password using core hashing module."""
    return get_password_hash(password)


async def seed_data():
    """
    Connects to the database and inserts initial data for development.
    """
    db_url = get_database_url()
    engine = create_async_engine(db_url, echo=True)

    async with engine.connect() as conn:
        print("--- Starting to seed data for response-network ---")
        
        # First, delete existing data
        print("Deleting existing data...")
        await conn.execute(text("DELETE FROM user_request_access"))
        await conn.execute(text("DELETE FROM users"))
        await conn.execute(text("DELETE FROM request_types"))
        await conn.execute(text("DELETE FROM exportable_settings"))
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
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
            },
            {
                "id": str(uuid.uuid4()),
                "username": "basic_user",
                "email": "basic@example.com",
                "hashed_password": hash_password("basic_password123"),
                "is_active": True,
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
            },
            {
                "id": str(uuid.uuid4()),
                "username": "premium_user",
                "email": "premium@example.com",
                "hashed_password": hash_password("premium_password456"),
                "is_active": True,
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
            },
        ]

        # Using text() for SQL statement to avoid ORM dependency in this script
        user_insert_stmt = text(
            """
            INSERT INTO users (id, username, email, hashed_password, is_active, created_at, updated_at)
            VALUES (:id, :username, :email, :hashed_password, :is_active, :created_at, :updated_at);
            """
        )
        await conn.execute(user_insert_stmt, users_to_create)
        print(f"-> {len(users_to_create)} users created.")

        # --- 2. Create Request Types ---
        print("Creating request types...")
        request_types_to_create = [
            {
                "name": "match_query",
                "description": "جستجوی تطبیقی ساده",
                "is_active": True,
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
            },
            {
                "name": "term_query",
                "description": "جستجوی دقیق",
                "is_active": True,
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
            },
            {
                "name": "bool_query",
                "description": "جستجوی منطقی",
                "is_active": True,
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
            },
            {
                "name": "aggregation",
                "description": "تجمیع داده‌ها",
                "is_active": True,
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
            },
        ]

        request_type_insert_stmt = text(
            """
            INSERT INTO request_types (name, description, is_active, created_at, updated_at)
            VALUES (:name, :description, :is_active, :created_at, :updated_at)
            RETURNING id;
            """
        )
        request_type_ids = []
        for request_type in request_types_to_create:
            result = await conn.execute(request_type_insert_stmt, request_type)
            request_type_id = result.scalar()
            request_type_ids.append(request_type_id)
        print(f"-> {len(request_types_to_create)} request types created.")

        # --- 3. Create User Request Access ---
        print("Creating user request access...")
        user_request_access_to_create = []
        
        # Admin has access to all request types with no limits
        for request_type_id in request_type_ids:
            user_request_access_to_create.append({
                "user_id": users_to_create[0]["id"],  # admin
                "request_type_id": request_type_id,
                "is_active": True,
                "allowed_indices": json.dumps(["*"]),  # Convert list to JSON string
                "rate_limit": None,
                "daily_limit": None,
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
            })

        # Basic user has access to match and term queries with limits
        for request_type_id in request_type_ids[:2]:  # match_query and term_query
            user_request_access_to_create.append({
                "user_id": users_to_create[1]["id"],  # basic_user
                "request_type_id": request_type_id,
                "is_active": True,
                "allowed_indices": json.dumps(["products", "articles"]),  # Convert list to JSON string
                "rate_limit": 10,  # 10 requests per minute
                "daily_limit": 1000,  # 1000 requests per day
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
            })

        # Premium user has access to all request types with higher limits
        for request_type_id in request_type_ids:
            user_request_access_to_create.append({
                "user_id": users_to_create[2]["id"],  # premium_user
                "request_type_id": request_type_id,
                "is_active": True,
                "allowed_indices": json.dumps(["products", "articles", "logs-prod"]),  # Convert list to JSON string
                "rate_limit": 100,  # 100 requests per minute
                "daily_limit": 10000,  # 10000 requests per day
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
            })

        user_request_access_insert_stmt = text(
            """
            INSERT INTO user_request_access (user_id, request_type_id, is_active, allowed_indices, rate_limit, daily_limit, created_at, updated_at)
            VALUES (:user_id, :request_type_id, :is_active, :allowed_indices, :rate_limit, :daily_limit, :created_at, :updated_at);
            """
        )
        await conn.execute(user_request_access_insert_stmt, user_request_access_to_create)
        print(f"-> {len(user_request_access_to_create)} user request access entries created.")

        # --- 4. Create Exportable Settings ---
        print("Creating exportable settings...")
        exportable_settings_to_create = [
            {
                "name": "default_match_settings",
                "description": "تنظیمات پیش‌فرض برای جستجوی تطبیقی",
                "is_active": True,
                "settings": json.dumps({  # Convert dict to JSON string
                    "operator": "or",
                    "minimum_should_match": "50%",
                    "boost": 1.0,
                    "fuzziness": "AUTO",
                }),
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
            },
            {
                "name": "default_bool_settings",
                "description": "تنظیمات پیش‌فرض برای جستجوی منطقی",
                "is_active": True,
                "settings": json.dumps({  # Convert dict to JSON string
                    "minimum_should_match": 1,
                    "boost": 1.0,
                    "tie_breaker": 0.3,
                }),
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
            },
            {
                "name": "default_aggregation_settings",
                "description": "تنظیمات پیش‌فرض برای تجمیع داده‌ها",
                "is_active": True,
                "settings": json.dumps({  # Convert dict to JSON string
                    "size": 10,
                    "min_doc_count": 1,
                    "order": {"_count": "desc"},
                }),
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
            },
        ]

        exportable_settings_insert_stmt = text(
            """
            INSERT INTO exportable_settings (name, description, is_active, settings, created_at, updated_at)
            VALUES (:name, :description, :is_active, :settings, :created_at, :updated_at);
            """
        )
        await conn.execute(exportable_settings_insert_stmt, exportable_settings_to_create)
        print(f"-> {len(exportable_settings_to_create)} exportable settings created.")

        await conn.commit()
        print("--- Data seeding completed successfully ---")


if __name__ == "__main__":
    asyncio.run(seed_data())