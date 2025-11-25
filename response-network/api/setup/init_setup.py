"""
Setup script for initializing the Response Network.
This script:
1. Creates/updates .env file from config_template.py
2. Runs database migrations
3. Creates initial admin user
4. Sets up base worker settings
5. Seeds sample data (if SEED_DATA=true)
"""
import asyncio
import sys
from pathlib import Path
from dotenv import load_dotenv, set_key
import os

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from setup.config_template import (
    DATABASE_CONFIG,
    REDIS_CONFIG,
    ELASTICSEARCH_CONFIG,
    API_CONFIG,
    ADMIN_USER_CONFIG,
    EXPORT_CONFIG,
    CELERY_CONFIG,
)


def create_env_file():
    """Create or update .env file with configuration."""
    env_path = Path(__file__).parent.parent / ".env"
    
    print(f"📝 Creating/updating .env file at {env_path}")
    
    # Database settings
    set_key(env_path, "RESPONSE_DB_USER", DATABASE_CONFIG["RESPONSE_DB_USER"])
    set_key(env_path, "RESPONSE_DB_PASSWORD", DATABASE_CONFIG["RESPONSE_DB_PASSWORD"])
    set_key(env_path, "RESPONSE_DB_HOST", DATABASE_CONFIG["RESPONSE_DB_HOST"])
    set_key(env_path, "RESPONSE_DB_PORT", str(DATABASE_CONFIG["RESPONSE_DB_PORT"]))
    set_key(env_path, "RESPONSE_DB_NAME", DATABASE_CONFIG["RESPONSE_DB_NAME"])
    
    # Redis settings
    set_key(env_path, "REDIS_URL", REDIS_CONFIG["REDIS_URL"])
    
    # Elasticsearch settings
    set_key(env_path, "ELASTICSEARCH_URL", ELASTICSEARCH_CONFIG["ES_URL"])
    
    # API settings
    set_key(env_path, "SECRET_KEY", API_CONFIG["SECRET_KEY"])
    set_key(env_path, "ACCESS_TOKEN_EXPIRE_MINUTES", str(API_CONFIG["ACCESS_TOKEN_EXPIRE_MINUTES"]))
    
    # Export settings
    set_key(env_path, "EXPORT_DIR", EXPORT_CONFIG["EXPORT_DIR"])
    
    print(f"✅ .env file created/updated successfully")


def run_migrations():
    """Run Alembic migrations."""
    print("\n🔄 Running database migrations...")
    api_path = Path(__file__).parent.parent
    
    import subprocess
    result = subprocess.run(
        ["alembic", "upgrade", "head"],
        cwd=api_path,
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print(f"❌ Migration failed: {result.stderr}")
        return False
    
    print("✅ Migrations completed successfully")
    return True


async def create_admin_user():
    """Create initial admin user."""
    print("\n👤 Creating admin user...")
    
    from sqlalchemy.ext.asyncio import AsyncSession
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy.ext.asyncio import create_async_engine
    from core.config import settings
    from models.user import User
    from security import get_password_hash
    
    try:
        # Create engine and session
        engine = create_async_engine(settings.DATABASE_URL)
        async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        
        async with async_session() as db:
            from sqlalchemy import select
            
            # Check if admin user already exists
            result = await db.execute(
                select(User).where(User.username == ADMIN_USER_CONFIG["username"])
            )
            existing_user = result.scalar_one_or_none()
            
            if existing_user:
                print(f"⚠️  Admin user '{ADMIN_USER_CONFIG['username']}' already exists")
                return True
            
            # Create admin user
            admin_user = User(
                username=ADMIN_USER_CONFIG["username"],
                email=ADMIN_USER_CONFIG["email"],
                hashed_password=get_password_hash(ADMIN_USER_CONFIG["password"]),
                is_active=True,
                is_admin=True,
            )
            db.add(admin_user)
            await db.commit()
            
            print(f"✅ Admin user '{ADMIN_USER_CONFIG['username']}' created successfully")
            print(f"   Email: {ADMIN_USER_CONFIG['email']}")
            print(f"   Password: {ADMIN_USER_CONFIG['password']}")
            return True
            
    except Exception as e:
        print(f"❌ Failed to create admin user: {str(e)}")
        return False
    finally:
        await engine.dispose()


async def setup_base_worker_settings():
    """Setup base worker settings in database."""
    print("\n⚙️  Setting up base worker settings...")
    
    try:
        from sqlalchemy.ext.asyncio import AsyncSession
        from sqlalchemy.orm import sessionmaker
        from sqlalchemy.ext.asyncio import create_async_engine
        from core.config import settings
        from core.dependencies import get_db
        from models.worker_settings import WorkerSettings
        from sqlalchemy import select
        
        # This is just a placeholder - actual implementation depends on your models
        print("⚠️  Base worker settings setup - please configure manually or implement")
        return True
        
    except Exception as e:
        print(f"⚠️  Failed to setup worker settings: {str(e)}")
        return True


def seed_sample_data():
    """Seed sample development data (only if SEED_DATA env var is true)"""
    should_seed = os.getenv("SEED_DATA", "false").lower() == "true"
    
    if not should_seed:
        print("\n⏭️  Skipping sample data seeding (set SEED_DATA=true to enable)")
        return True
    
    print("\n🌱 Seeding sample data...")
    
    try:
        from setup.initialization import create_default_admin, seed_sample_users
        
        admin_created = create_default_admin()
        users_created = seed_sample_users()
        
        print(f"✅ Sample data seeded (admin: {admin_created}, users: {users_created})")
        return True
    except Exception as e:
        print(f"⚠️  Failed to seed sample data: {str(e)}")
        return True  # Don't fail setup if seeding fails


def print_setup_summary():
    """Print setup summary and next steps."""
    print("\n" + "="*60)
    print("🎉 SETUP COMPLETED!")
    print("="*60)
    print("\n📋 Configuration Summary:")
    print(f"   Database: {DATABASE_CONFIG['RESPONSE_DB_HOST']}:{DATABASE_CONFIG['RESPONSE_DB_PORT']}")
    print(f"   Redis: {REDIS_CONFIG['REDIS_HOST']}:{REDIS_CONFIG['REDIS_PORT']}")
    print(f"   Elasticsearch: {ELASTICSEARCH_CONFIG['ES_HOST']}:{ELASTICSEARCH_CONFIG['ES_PORT']}")
    print(f"   API: {API_CONFIG['API_HOST']}:{API_CONFIG['API_PORT']}")
    
    print("\n🚀 Next steps:")
    print("   1. Start Docker services:")
    print("      docker-compose -f docker-compose.dev.yml --profile response up -d")
    print("\n   2. Start FastAPI server:")
    print("      python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload")
    print("\n   3. (Optional) Start Celery worker:")
    print("      celery -A workers.celery_app worker --loglevel=info")
    print("\n   4. Access API:")
    print("      http://127.0.0.1:8000/docs")
    print("\n   5. Login with:")
    print(f"      Username: {ADMIN_USER_CONFIG['username']}")
    print(f"      Password: {ADMIN_USER_CONFIG['password']}")
    print("\n" + "="*60)


async def main():
    """Run all setup steps."""
    print("🔧 Response Network Setup Started...\n")
    
    try:
        # Step 1: Create .env file
        create_env_file()
        
        # Step 2: Run migrations
        if not run_migrations():
            print("❌ Setup failed at migration step")
            return False
        
        # Step 3: Create admin user
        if not await create_admin_user():
            print("❌ Setup failed at admin user creation")
            return False
        
        # Step 4: Setup base worker settings
        if not await setup_base_worker_settings():
            print("❌ Setup failed at worker settings")
            return False
        
        # Step 5: Seed sample data (optional)
        seed_sample_data()
        
        print_setup_summary()
        return True
        
    except Exception as e:
        print(f"\n❌ Setup failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
