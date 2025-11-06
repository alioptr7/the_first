"""اسکریپت پر کردن دیتابیس با داده‌های اولیه"""
import asyncio
import json
import os
import sys
import uuid
from datetime import datetime, timezone

from sqlalchemy.future import select

# --- Path Setup ---
# This allows the script to find modules in the 'api' and 'shared' directories.
api_dir = os.path.dirname(os.path.abspath(__file__))
response_network_dir = os.path.dirname(api_dir)
project_root = os.path.dirname(response_network_dir)

sys.path.insert(0, project_root)
sys.path.insert(0, api_dir)

from core.hashing import get_password_hash
from db.session import async_session
from models.user import User
from models.request_type import RequestType
from models.user_request_access import UserRequestAccess


async def seed_data():
    """
    Connects to the database and inserts initial data for development.
    """
    async with async_session() as session:
        print("--- Starting to seed data for response-network ---")

        # --- 0. Clear Existing Data ---
        print("Clearing existing data...")
        await session.execute(UserRequestAccess.__table__.delete())
        await session.execute(RequestType.__table__.delete())
        await session.execute(User.__table__.delete())
        await session.commit()
        print("-> Existing data cleared.")

        # --- 1. Create Users ---
        print("Creating users...")
        users_to_create = [
            User(
                id=uuid.uuid4(),
                username="admin",
                email="admin@example.com",
                hashed_password=get_password_hash("SuperSecureAdminP@ss!"),
                is_active=True,
                profile_type="admin",
            ),
            User(
                id=uuid.uuid4(),
                username="basic_user",
                email="basic@example.com",
                hashed_password=get_password_hash("basic_password123"),
                is_active=True,
                profile_type="basic",
            ),
            User(
                id=uuid.uuid4(),
                username="premium_user",
                email="premium@example.com",
                hashed_password=get_password_hash("premium_password456"),
                is_active=True,
                profile_type="premium",
            ),
        ]
        session.add_all(users_to_create)
        await session.commit()
        print(f"-> {len(users_to_create)} users created.")

        # --- 2. Create Request Types ---
        print("Creating request types...")
        request_types_to_create = [
            RequestType(
                name="match_query",
                description="جستجوی تطبیقی ساده",
                query_type="match",
                query_type_alias="match",
                query_template={"query": {"match": {"_all": "{{query_string}}"}}},
                available_indices=["*"],
                is_active=True,
            ),
            RequestType(
                name="term_query",
                description="جستجوی دقیق",
                query_type="term",
                query_type_alias="term",
                query_template={"query": {"term": {"_all": "{{query_string}}"}}},
                available_indices=["*"],
                is_active=True,
            ),
            RequestType(
                name="bool_query",
                description="جستجوی منطقی",
                query_type="bool",
                query_type_alias="bool",
                query_template={"query": {"bool": {"must": []}}},
                available_indices=["*"],
                is_active=True,
            ),
            RequestType(
                name="aggregation",
                description="تجمیع داده‌ها",
                query_type="aggregation",
                query_type_alias="agg",
                query_template={"aggs": {}},
                available_indices=["*"],
                is_active=True,
            ),
        ]
        session.add_all(request_types_to_create)
        await session.commit()
        print(f"-> {len(request_types_to_create)} request types created.")

        # --- 3. Create User Request Access ---
        print("Creating user request access...")

        # Retrieve users and request types to get their IDs
        admin_user = await session.execute(select(User).where(User.username == "admin"))
        admin_user = admin_user.scalar_one()

        basic_user = await session.execute(select(User).where(User.username == "basic_user"))
        basic_user = basic_user.scalar_one()

        premium_user = await session.execute(select(User).where(User.username == "premium_user"))
        premium_user = premium_user.scalar_one()

        req_types = await session.execute(select(RequestType))
        req_types = req_types.scalars().all()

        user_request_access_to_create = []

        # Admin has access to all request types with no limits
        for req_type in req_types:
            user_request_access_to_create.append(
                UserRequestAccess(
                    user_id=admin_user.id,
                    request_type_id=req_type.id,
                    is_active=True,
                    allowed_indices=["*"],
                    rate_limit=None,
                    daily_limit=None,
                )
            )

        # Basic user has access to match and term queries with limits
        for req_type in req_types[:2]:  # match_query and term_query
            user_request_access_to_create.append(
                UserRequestAccess(
                    user_id=basic_user.id,
                    request_type_id=req_type.id,
                    is_active=True,
                    allowed_indices=["products", "articles"],
                    rate_limit=10,  # 10 requests per minute
                    daily_limit=1000,  # 1000 requests per day
                )
            )

        # Premium user has access to all request types with higher limits
        for req_type in req_types:
            user_request_access_to_create.append(
                UserRequestAccess(
                    user_id=premium_user.id,
                    request_type_id=req_type.id,
                    is_active=True,
                    allowed_indices=["products", "articles", "logs-prod"],
                    rate_limit=100,  # 100 requests per minute
                    daily_limit=10000,  # 10000 requests per day
                )
            )

        session.add_all(user_request_access_to_create)
        await session.commit()
        print(f"-> {len(user_request_access_to_create)} user request access records created.")

        print("--- Data seeding finished successfully! ---")


if __name__ == "__main__":
    asyncio.run(seed_data())