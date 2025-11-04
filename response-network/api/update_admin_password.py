
import asyncio
import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

# Add project paths to sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
response_network_root = os.path.abspath(os.path.join(project_root, ".."))
api_root = os.path.abspath(os.path.join(response_network_root, "response-network", "api"))

sys.path.insert(0, project_root)
sys.path.insert(0, response_network_root)
sys.path.insert(0, api_root)

from core.config import settings
from core.hashing import get_password_hash
from models.user import User

async def update_admin_password():
    """Updates the admin password in the database."""
    engine = create_async_engine(settings.DATABASE_CONNECTION_URL, echo=True)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        async with session.begin():
            admin_user = await session.execute(
                text("SELECT * FROM users WHERE email = :email")
                , {"email": "admin@example.com"}
            )
            admin_user = admin_user.fetchone()

            if admin_user:
                new_password = "admin"
                hashed_password = get_password_hash(new_password)
                await session.execute(
                    text("UPDATE users SET hashed_password = :hashed_password WHERE email = :email"),
                    {"hashed_password": hashed_password, "email": "admin@example.com"}
                )
                print(f"Password for admin user {admin_user.email} updated successfully.")
            else:
                print("Admin user not found.")

if __name__ == "__main__":
    asyncio.run(update_admin_password())
