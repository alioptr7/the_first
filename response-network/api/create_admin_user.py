import asyncio
import sys
import os
import uuid
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load environment variables from root .env
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
load_dotenv(os.path.join(project_root, ".env"))

# Add project root to Python path
sys.path.insert(0, project_root)

from core.hashing import get_password_hash
from models.user import User
# Import all models to resolve SQLAlchemy dependencies
from models.profile_type import ProfileType  # noqa
from models.request_type import RequestType  # noqa
from models.profile_type_request_access import ProfileTypeRequestAccess  # noqa

# Database connection settings from env
DB_USER = os.getenv("RESPONSE_DB_USER", "respuser")
DB_PASS = os.getenv("RESPONSE_DB_PASSWORD", "resppassword123")
DB_HOST = os.getenv("RESPONSE_DB_HOST", "localhost")
DB_PORT = os.getenv("RESPONSE_DB_PORT", "5433")
DB_NAME = os.getenv("RESPONSE_DB_NAME", "response_network_db")

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