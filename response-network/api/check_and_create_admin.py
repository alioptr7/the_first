"""Script to check database and create admin user."""
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
from auth.security import get_password_hash

async def check_database():
    """Check if database exists and create admin user if needed."""
    
    # Create async engine
    engine = create_async_engine(
        str(settings.DATABASE_URL),
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
            print("  Run: cd response-network/api && alembic upgrade head")
            return
        
        # Check if admin user exists
        async with async_session() as session:
            result = await session.execute(text("""
                SELECT COUNT(*) FROM users WHERE is_admin = true
            """))
            admin_count = result.scalar()
            print(f"✓ Admin users in database: {admin_count}")
            
            if admin_count > 0:
                print("✓ Admin user already exists!")
                # Show admin details
                result = await session.execute(text("""
                    SELECT id, username, email, is_admin FROM users WHERE is_admin = true LIMIT 1
                """))
                admin = result.fetchone()
                if admin:
                    print(f"  ID: {admin[0]}")
                    print(f"  Username: {admin[1]}")
                    print(f"  Email: {admin[2]}")
                    print(f"  Is Admin: {admin[3]}")
                return
            
            # Create admin user
            print("\n➤ Creating admin user...")
            
            admin_username = "admin"
            admin_email = "admin@example.com"
            admin_password = "admin123"
            
            # Check if user with same username exists
            result = await session.execute(text(f"""
                SELECT id FROM users WHERE username = '{admin_username}'
            """))
            existing_user = result.scalar()
            
            if existing_user:
                print(f"✗ User with username '{admin_username}' already exists!")
                return
            
            # Hash password
            hashed_password = get_password_hash(admin_password)
            
            # Generate UUID for admin user
            admin_id = str(uuid.uuid4())
            
            # Insert admin user with UUID and default values
            await session.execute(text(f"""
                INSERT INTO users (
                    id, username, email, hashed_password, is_admin, is_active, profile_type,
                    daily_request_limit, monthly_request_limit, max_results_per_request, allowed_indices
                )
                VALUES (
                    '{admin_id}', '{admin_username}', '{admin_email}', '{hashed_password}', true, true, 'admin',
                    1000, 10000, 5000, '{{}}'
                )
            """))
            await session.commit()
            
            print(f"✓ Admin user created successfully!")
            print(f"  Username: {admin_username}")
            print(f"  Email: {admin_email}")
            print(f"  Password: {admin_password}")
            print("\n⚠ Change this password after first login!")
    
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        await engine.dispose()

async def main():
    """Main entry point."""
    print("=" * 50)
    print("Database Check and Admin User Creation")
    print("=" * 50)
    print(f"Database URL: {settings.DATABASE_URL}")
    print("=" * 50 + "\n")
    
    await check_database()

if __name__ == "__main__":
    asyncio.run(main())