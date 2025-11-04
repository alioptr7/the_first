
import asyncio
import uuid
import sys
from pathlib import Path

# --- Start of Path Fix ---
# Add project root, response-network, and api to the Python path
project_root = Path(__file__).resolve().parents[2]  # the_first/
response_network_root = Path(__file__).resolve().parents[1]  # response-network/
api_root = Path(__file__).resolve().parent  # api/
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))
if str(response_network_root) not in sys.path:
    sys.path.append(str(response_network_root))
if str(api_root) not in sys.path:
    sys.path.append(str(api_root))
# --- End of Path Fix ---

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from core.config import settings
from core.hashing import get_password_hash
from models.user import User

async def create_admin_user():
    engine = create_async_engine(str(settings.DATABASE_CONNECTION_URL), echo=True)
    async_session = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        async with session.begin():
            admin_user = User(
                id=uuid.uuid4(),
                username="admin",
                email="admin@example.com",
                hashed_password=get_password_hash("admin"),
                profile_type="admin",
                is_active=True,
            )
            session.add(admin_user)
            print("Admin user created successfully.")

if __name__ == "__main__":
    asyncio.run(create_admin_user())