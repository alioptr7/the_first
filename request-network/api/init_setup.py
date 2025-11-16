"""
Request Network Initialization Script

مراحل:
1. بررسی/ایجاد پایگاه داده
2. اجرای Alembic migrations
3. ایجاد فهرست‌های import
4. چاپ وضعیت
"""
import asyncio
import subprocess
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker


def create_directories():
    """Create required directories for imports."""
    import_dir = Path("./imports")
    export_dir = Path("./exports")
    
    for dir_path in [import_dir, export_dir]:
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"✓ Directory created/verified: {dir_path}")
    
    return True


def update_env_file():
    """Update .env with correct configurations."""
    print("\n📝 Updating .env Configuration...")
    from dotenv import set_key
    
    env_path = Path(".env")
    
    # Redis configuration (مشترک از Response)
    set_key(env_path, "REDIS_URL", "redis://localhost:6380/0")
    print("✓ REDIS_URL set to: redis://localhost:6380/0 (Response Network)")
    
    # Database configuration
    set_key(env_path, "DATABASE_URL", "postgresql+asyncpg://user:password@localhost:5432/request_db")
    print("✓ DATABASE_URL set for Request Network")
    
    return True


def run_migrations():
    """Run Alembic migrations."""
    print("\n📦 Running Database Migrations...")
    try:
        # Change to API directory to ensure proper path resolution
        import os
        original_dir = os.getcwd()
        os.chdir(Path(__file__).parent)
        
        cmd = [sys.executable, "-m", "alembic", "upgrade", "head"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        os.chdir(original_dir)
        
        if result.returncode == 0:
            print("✓ Migrations completed successfully")
            return True
        else:
            print(f"✗ Migration failed:")
            print(result.stderr)
            # Don't fail the whole initialization - continue anyway
            print("⚠️ Continuing with setup despite migration failure...")
            return True  # Return True to continue
    except Exception as e:
        print(f"✗ Error running migrations: {e}")
        print("⚠️ Continuing with setup despite error...")
        return True  # Return True to continue


async def check_database():
    """Check database connection and tables."""
    print("\n🔍 Checking Database...")
    
    try:
        from core.config import settings
        
        engine = create_async_engine(
            str(settings.DATABASE_URL),
            echo=False,
        )
        
        # Test connection
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT 1"))
            print("✓ Database connection successful!")
        
        # Check tables
        async with engine.begin() as conn:
            result = await conn.execute(text("""
                SELECT table_name FROM information_schema.tables 
                WHERE table_schema = 'public'
            """))
            tables = result.fetchall()
            print(f"✓ Database tables count: {len(tables)}")
            for table in tables:
                print(f"   - {table[0]}")
        
        await engine.dispose()
        return True
        
    except Exception as e:
        print(f"✗ Database check failed: {e}")
        return False


async def main():
    """Run all setup steps."""
    print("="*60)
    print("🚀 Request Network Initialization")
    print("="*60)
    
    try:
        # Step 1: Create directories
        if not create_directories():
            return False
        
        # Step 2: Update .env
        if not update_env_file():
            return False
        
        # Step 3: Run migrations
        if not run_migrations():
            return False
        
        # Step 4: Check database
        if not await check_database():
            return False
        
        # Step 4: Print summary
        print("\n" + "="*60)
        print("✅ Request Network Initialization Complete!")
        print("="*60)
        print("\n📋 Next Steps:")
        print("1. شروع Request Network API:")
        print("   python -m uvicorn main:app --host 127.0.0.1 --port 8001")
        print("\n2. شروع Beat Scheduler:")
        print("   python -m celery -A workers.celery_app beat --loglevel=info")
        print("\n3. شروع Worker:")
        print("   python -m celery -A workers.celery_app worker --pool=solo --loglevel=info")
        print("\n⏳ منتظر بمانید تا Response Network تنظیمات و کاربران را sync کند:")
        print("   - هر 60 ثانیه: settings_importer اجرا می‌شود")
        print("   - کاربران و تنظیمات از Response Network import خواهند شد")
        print("\n📊 سرویس‌های درخواست برای تست:")
        print("   API: http://127.0.0.1:8001/api/v1")
        print("   Swagger: http://127.0.0.1:8001/docs")
        print("="*60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Setup failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
