import asyncio
import uuid
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import async_session
from models.user import User
from core.security import get_password_hash

async def create_admin_user():
    async with async_session() as session:
        admin_user = User(
            id=uuid.uuid4(),
            username="admin",
            email="admin@example.com",
            hashed_password=get_password_hash("admin123"),
            is_active=True
        )
        session.add(admin_user)
        await session.commit()
        print("Admin user created successfully!")

if __name__ == "__main__":
    asyncio.run(create_admin_user())