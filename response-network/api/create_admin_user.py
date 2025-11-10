import asyncio
import sys
import os
import uuid
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# Add project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, project_root)

from core.hashing import get_password_hash
from models.user import User

# Database connection settings
DB_USER = "user"
DB_PASS = "password"
DB_HOST = "127.0.0.1"
DB_PORT = "5433"
DB_NAME = "response_db"

# Create database URL
DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

async def create_admin_user():
    # Create async database engine
    engine = create_async_engine(DATABASE_URL)
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        # Create admin user
        admin_user = User(
            username="admin",
            email="admin@example.com",
            hashed_password=get_password_hash("admin"),
            full_name="Admin User",
            profile_type="admin",
            is_active=True,
            is_admin=True,
            daily_request_limit=1000,
            monthly_request_limit=10000,
            max_results_per_request=1000,
            allowed_indices=["*"]
        )
        
        session.add(admin_user)
        await session.commit()
        print("Admin user created successfully!")

if __name__ == "__main__":
    asyncio.run(create_admin_user())