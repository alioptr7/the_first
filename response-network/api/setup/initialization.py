"""
Database initialization and seeding for startup
"""
import sys
from pathlib import Path
from uuid import uuid4
import logging

# Setup paths
_api_dir = Path(__file__).resolve().parent.parent
_project_root = _api_dir.parent.parent
sys.path.insert(0, str(_project_root))
sys.path.insert(0, str(_api_dir))

from db.session import SessionLocal
from models.user import User
from core.hashing import get_password_hash

logger = logging.getLogger(__name__)


def create_default_admin():
    """Create default admin user if it doesn't exist"""
    try:
        db = SessionLocal()
        
        # Check if admin exists
        existing = db.query(User).filter(User.username == "admin").first()
        if existing:
            logger.info("Admin user already exists")
            return False
        
        # Create admin
        admin = User(
            id=uuid4(),
            username="admin",
            email="admin@example.com",
            hashed_password=get_password_hash("admin@123456"),
            full_name="System Administrator",
            profile_type="admin",
            is_active=True,
            is_admin=True,
            daily_request_limit=10000,
            monthly_request_limit=100000,
            max_results_per_request=5000,
            allowed_indices=["*"],
        )
        
        db.add(admin)
        db.commit()
        logger.info("✓ Created default admin user")
        return True
        
    except Exception as e:
        logger.error(f"Failed to create admin user: {e}")
        db.rollback()
        return False
    finally:
        db.close()


def seed_sample_users():
    """Create sample users for development"""
    try:
        db = SessionLocal()
        
        sample_users = [
            {
                "username": "user_basic",
                "email": "basic@example.com",
                "password": "user@123456",
                "profile_type": "basic",
                "daily_limit": 100,
                "monthly_limit": 2000,
            },
            {
                "username": "user_premium",
                "email": "premium@example.com",
                "password": "user@123456",
                "profile_type": "premium",
                "daily_limit": 1000,
                "monthly_limit": 20000,
            },
        ]
        
        created = 0
        for user_data in sample_users:
            existing = db.query(User).filter(User.username == user_data["username"]).first()
            if not existing:
                user = User(
                    id=uuid4(),
                    username=user_data["username"],
                    email=user_data["email"],
                    hashed_password=get_password_hash(user_data["password"]),
                    full_name=user_data["username"].replace("_", " ").title(),
                    profile_type=user_data["profile_type"],
                    is_active=True,
                    is_admin=False,
                    daily_request_limit=user_data["daily_limit"],
                    monthly_request_limit=user_data["monthly_limit"],
                    max_results_per_request=1000,
                    allowed_indices=["*"],
                )
                db.add(user)
                created += 1
        
        if created > 0:
            db.commit()
            logger.info(f"✓ Created {created} sample users")
        
        return created
        
    except Exception as e:
        logger.error(f"Failed to seed users: {e}")
        db.rollback()
        return 0
    finally:
        db.close()


def initialize_database():
    """Full database initialization (call on startup)"""
    logger.info("Initializing database...")
    
    admin_created = create_default_admin()
    users_created = seed_sample_users()
    
    logger.info(f"Database initialization complete (admin: {admin_created}, users: {users_created})")
