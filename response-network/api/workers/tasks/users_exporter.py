"""
Users export task - Export users to request-network
"""
from datetime import datetime
import json
from pathlib import Path
import os
from dotenv import load_dotenv

from celery import shared_task
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

# Load .env file
load_dotenv()

# Use shared_data directory directly
EXPORT_DIR = Path("/home/docker/the_first/the_first/shared_data/users")

# Import User model
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.user import User
# Import all models to resolve dependencies
from models.profile_type import ProfileType  # noqa
from models.request_type import RequestType  # noqa
from models.profile_type_request_access import ProfileTypeRequestAccess  # noqa
from models.profile_type_config import ProfileTypeConfig  # noqa


@shared_task
def export_users_to_request_network():
    """Export all active users to Request Network."""
    
    # Build database URL from env
    db_user = os.getenv("RESPONSE_DB_USER", "postgres")
    db_pass = os.getenv("RESPONSE_DB_PASSWORD", "postgres")
    db_host = os.getenv("RESPONSE_DB_HOST", "127.0.0.1")
    db_port = os.getenv("RESPONSE_DB_PORT", "5432")
    db_name = os.getenv("RESPONSE_DB_NAME", "response_network")
    
    database_url = f"postgresql+psycopg://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
    
    # Create sync engine and session
    engine = create_engine(database_url)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Get all active users
        result = session.execute(
            select(User).where(User.is_active == True)
        )
        users = result.scalars().all()
        
        # Prepare export data
        export_data = {
            "users": [
                {
                    "id": str(user.id),
                    "username": user.username,
                    "email": user.email,
                    "hashed_password": user.hashed_password,
                    "full_name": user.full_name if hasattr(user, 'full_name') else None,
                    "profile_type": user.profile_type or "user",
                    "is_active": user.is_active,
                    # Fields for Request Network with defaults
                    "allowed_request_types": [],  # Empty by default
                    "blocked_request_types": [],  # Empty by default
                    "rate_limit_per_minute": 200,  # Default rate limit
                    "rate_limit_per_hour": 1000,
                    "rate_limit_per_day": 5000,
                    "daily_request_limit": getattr(user, 'daily_request_limit', 1000),
                    "monthly_request_limit": getattr(user, 'monthly_request_limit', 10000),
                    "priority": 5,  # Default priority
                    "created_at": user.created_at.isoformat() if user.created_at else None,
                    "updated_at": user.updated_at.isoformat() if user.updated_at else None
                }
                for user in users
            ],
            "exported_at": datetime.utcnow().isoformat(),
            "total_count": len(users),
        }
        
        # Ensure export directory exists
        EXPORT_DIR.mkdir(parents=True, exist_ok=True)
        
        # Save to latest.json
        latest_file = EXPORT_DIR / "latest.json"
        with open(latest_file, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        return {
            "status": "success",
            "exported_at": export_data["exported_at"],
            "total_count": len(users),
            "file": str(latest_file)
        }
    finally:
        session.close()


