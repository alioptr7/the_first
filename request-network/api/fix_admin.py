import asyncio
import uuid
from sqlalchemy import select
from db.session import AsyncSessionFactory
from models import User
import bcrypt

def get_password_hash(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

async def fix_admin():
    async with AsyncSessionFactory() as session:
        result = await session.execute(select(User).where(User.username == 'admin'))
        admin = result.scalar_one_or_none()
        
        if not admin:
            print("Creating admin user in Request Network...")
            admin = User(
                id=uuid.uuid4(),
                username='admin',
                email='admin@example.com',
                hashed_password=get_password_hash('admin123'),
                profile_type='admin',
                is_active=True,
                allowed_request_types=[],
                blocked_request_types=[]
            )
            session.add(admin)
            await session.commit()
            print("Admin created successfully.")
        else:
            print("Admin user already exists. Updating password to 'admin123'...")
            admin.hashed_password = get_password_hash('admin123')
            await session.commit()
            print("Admin password updated successfully.")

if __name__ == "__main__":
    asyncio.run(fix_admin())
