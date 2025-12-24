import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sqlalchemy import select
from db.session import async_session
from models import User
from auth import security

async def check_admin():
    async with async_session() as session:
        result = await session.execute(select(User).where(User.username == 'admin'))
        admin = result.scalar_one_or_none()
        
        if admin:
            print(f"Admin user found:")
            print(f"  Username: {admin.username}")
            print(f"  Email: {admin.email}")
            print(f"  Is active: {admin.is_active}")
            print(f"  Profile type: {admin.profile_type}")
            print(f"  Hashed password: {admin.hashed_password}")
            
            test_password = "admin123"
            is_valid = security.verify_password(test_password, admin.hashed_password)
            print(f"\n  Password 'admin123' is valid: {is_valid}")
            
            if not is_valid:
                print(f"\n  Resetting password to 'admin123'...")
                admin.hashed_password = security.get_password_hash(test_password)
                await session.commit()
                print(f"  Password reset successfully!")
        else:
            print("Admin user not found!")

if __name__ == "__main__":
    asyncio.run(check_admin())
