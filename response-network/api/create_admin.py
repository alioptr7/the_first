import asyncio
import sys
import os
from pathlib import Path
from uuid import uuid4

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from db.session import async_session
from models import User
from auth.security import get_password_hash
from sqlalchemy import select

async def create_admin():
    print("🌱 Creating admin user...")
    async with async_session() as session:
        # Check if admin exists
        result = await session.execute(select(User).where(User.username == "admin"))
        existing_admin = result.scalar_one_or_none()
        
        if existing_admin:
            print("  ℹ Admin user already exists.")
            return

        # Create admin user
        admin_user = User(
            id=uuid4(),
            username="admin",
            email="admin@example.com",
            hashed_password=get_password_hash("admin123"),
            full_name="System Administrator",
            profile_type="admin",
            is_active=True,
            is_admin=True,
            daily_request_limit=10000,
            monthly_request_limit=100000,
            max_results_per_request=5000,
            allowed_indices=["*"],
        )
        
        session.add(admin_user)
        await session.commit()
        print("  ✓ Created admin user: admin (password: admin@123456)")

if __name__ == "__main__":
    asyncio.run(create_admin())