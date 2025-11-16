"""Script to check Request Network database and create admin user if needed."""
import sys
import asyncio
import uuid
from pathlib import Path

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from core.config import settings
from models.user import User

async def check_database():
    """Check if database exists and create admin user if needed."""
    
    # Create async engine
    engine = create_async_engine(
        str(settings.SQLALCHEMY_DATABASE_URI),
        echo=False,
    )
    
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    try:
        # Check database connection
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT 1"))
            print("✓ Database connection successful!")
        
        # Check if users table exists
        async with engine.begin() as conn:
            result = await conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'users'
                )
            """))
            table_exists = result.scalar()
            print(f"✓ Users table exists: {table_exists}")
        
        if not table_exists:
            print("✗ Users table does not exist. Running migrations first...")
            print("  Run: cd request-network/api && alembic upgrade head")
            return False
        
        # Check if admin user exists
        async with async_session() as session:
            result = await session.execute(text("SELECT COUNT(*) FROM users WHERE role = 'admin'"))
            admin_count = result.scalar()
            print(f"✓ Admin users in database: {admin_count}")
            
            if admin_count > 0:
                result = await session.execute(text("SELECT id, username, email, role FROM users WHERE role = 'admin' LIMIT 1"))
                admin = result.fetchone()
                if admin:
                    print("✓ Admin user already exists!")
                    print(f"  ID: {admin[0]}")
                    print(f"  Username: {admin[1]}")
                    print(f"  Email: {admin[2]}")
                    print(f"  Role: {admin[3]}")
                    return True
        
        print("\n❌ No admin user found in Request Network database!")
        print("   Admins should be synced from Response Network using settings_importer")
        print("   Waiting for sync...")
        return False
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return False
    finally:
        await engine.dispose()

if __name__ == "__main__":
    print("\n" + "="*50)
    print("Request Network Database Check")
    print("="*50)
    print(f"Database URL: {settings.SQLALCHEMY_DATABASE_URI}")
    print("="*50 + "\n")
    
    success = asyncio.run(check_database())
    sys.exit(0 if success else 1)
