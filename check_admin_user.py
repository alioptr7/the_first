import asyncio
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.join(os.getcwd(), "response-network", "api"))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import sessionmaker
from models.user import User

DATABASE_URL = "postgresql+asyncpg://user:password@localhost:5433/response_db"

async def check_admin():
    engine = create_async_engine(DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        result = await session.execute(select(User).where(User.username == 'admin'))
        user = result.scalar_one_or_none()
        if user:
            print(f'Admin found: {user.username}, is_active: {user.is_active}')
            print(f'Hashed password length: {len(user.hashed_password)}')
            
            # Test password verification
            from core.hashing import verify_password
            is_valid = verify_password('admin123', user.hashed_password)
            print(f'Password verification result: {is_valid}')
        else:
            print('Admin NOT found')
    
    await engine.dispose()

asyncio.run(check_admin())
