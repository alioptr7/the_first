"""
Users export task - Export users to request-network
"""
from datetime import datetime
import json
from pathlib import Path
import redis
import bcrypt

from celery import shared_task
from sqlalchemy.orm import Session

from core.config import settings
from core.dependencies import get_db_sync
from models.user import User as UserModel

EXPORT_PATH = Path(settings.EXPORT_DIR) / "users"

# Redis client for deduplication
redis_client = redis.from_url(settings.CELERY_BROKER_URL)


@shared_task(bind=True, max_retries=3)
def export_users_to_request_network(self):
    """
    Export all users to file for request-network.
    
    Exports: id, username, email, role, is_active, created_at, updated_at
    """
    try:
        # Create export directory if it doesn't exist
        EXPORT_PATH.mkdir(parents=True, exist_ok=True)
        
        # Get current timestamp for filename
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        
        # Get synchronous session
        db = next(get_db_sync())
        
        try:
            # Get all users
            all_users = db.query(UserModel).all()
            
            # Prepare export data
            users_list = []
            for user in all_users:
                # Generate default password hash (using username as default password)
                # In production, this should be handled differently (one-time password, email, etc.)
                default_password = user.username  # For testing: password = username
                hashed_password = bcrypt.hashpw(
                    default_password.encode('utf-8'),
                    bcrypt.gensalt()
                ).decode('utf-8')
                
                users_list.append({
                    "id": str(user.id),
                    "username": user.username,
                    "email": user.email,
                    "hashed_password": hashed_password,
                    "role": "admin" if user.is_admin else "user",  # Convert is_admin to role
                    "is_active": user.is_active,
                    "created_at": user.created_at.isoformat() if user.created_at else None,
                    "updated_at": user.updated_at.isoformat() if user.updated_at else None
                })
            
            export_data = {
                "users": users_list,
                "exported_at": datetime.utcnow().isoformat(),
                "version": 1,
                "total_count": len(users_list)
            }
            
            # Write to file
            export_file = EXPORT_PATH / f"users_{timestamp}.json"
            with open(export_file, "w", encoding="utf-8") as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
            
            # Write latest.json for easy access
            latest_file = EXPORT_PATH / "latest.json"
            with open(latest_file, "w", encoding="utf-8") as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
            
            return {
                "status": "success",
                "export_file": str(export_file),
                "total_users": len(users_list),
                "exported_at": datetime.utcnow().isoformat()
            }
        finally:
            db.close()
            
    except Exception as exc:
        # Retry on error
        raise self.retry(exc=exc, countdown=60)
