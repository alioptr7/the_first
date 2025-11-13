"""
Password sync task - Sync password changes to Request Network
"""
from datetime import datetime
import json
from pathlib import Path
import redis

from celery import shared_task
from sqlalchemy.orm import Session

from core.config import settings
from core.dependencies import get_db_sync
from models.user import User as UserModel

EXPORT_PATH = Path(settings.EXPORT_DIR) / "password_changes"

# Redis client for deduplication
redis_client = redis.from_url(settings.CELERY_BROKER_URL)


@shared_task(bind=True, max_retries=3)
def sync_password_to_request_network(self, user_id: str, hashed_password: str):
    """
    Sync ONLY a single user's password change to Request Network.
    
    Called ONLY when an admin resets a user's password in Response Network.
    This task exports ONLY the changed password to a queue file that 
    Request Network can import and apply.
    
    This ensures we only sync password changes, NOT all passwords.
    
    Parameters:
    - user_id: UUID of the user (the one whose password changed)
    - hashed_password: The new hashed password (bcrypt hash)
    """
    try:
        # Create export directory if it doesn't exist
        EXPORT_PATH.mkdir(parents=True, exist_ok=True)
        
        # Get current timestamp for filename
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        
        # Get synchronous session
        db = next(get_db_sync())
        
        try:
            # Get user
            user = db.query(UserModel).filter(UserModel.id == user_id).first()
            
            if not user:
                return {
                    "status": "error",
                    "message": f"User {user_id} not found",
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            # Prepare export data for THIS user's password change
            password_change = {
                "user_id": str(user.id),
                "username": user.username,
                "email": user.email,
                "hashed_password": hashed_password,
                "is_admin": user.is_admin,
                "changed_at": datetime.utcnow().isoformat()
            }
            
            # Write to timestamped file (for audit trail)
            export_file = EXPORT_PATH / f"password_change_{user.username}_{timestamp}.json"
            with open(export_file, "w", encoding="utf-8") as f:
                json.dump(password_change, f, ensure_ascii=False, indent=2)
            
            # Write to queue file for Request Network to process
            queue_file = EXPORT_PATH / "password_changes_queue.json"
            queue_data = []
            if queue_file.exists():
                try:
                    with open(queue_file, "r") as f:
                        queue_data = json.load(f)
                except:
                    queue_data = []
            
            # Add this password change to the queue
            queue_data.append(password_change)
            with open(queue_file, "w") as f:
                json.dump(queue_data, f, indent=2)
            
            return {
                "status": "success",
                "message": f"Password change queued for user {user.username}",
                "user_id": str(user.id),
                "username": user.username,
                "export_file": str(export_file),
                "queued_at": datetime.utcnow().isoformat()
            }
            
        finally:
            db.close()
            
    except Exception as e:
        # Retry on error
        raise self.retry(exc=e, countdown=60, max_retries=3)

