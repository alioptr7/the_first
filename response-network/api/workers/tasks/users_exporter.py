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
META_FILE = EXPORT_PATH / "last_export_meta.json"

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

        # Determine last export timestamp (if available)
        last_export_at = None
        if META_FILE.exists():
            try:
                with open(META_FILE, "r", encoding="utf-8") as mf:
                    meta = json.load(mf)
                    last_export_at = meta.get("exported_at")
                    if last_export_at:
                        last_export_at = datetime.fromisoformat(last_export_at)
            except Exception:
                last_export_at = None

        # Get current timestamp for filename
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")

        # Get synchronous session
        db = next(get_db_sync())

        try:
            # Query users changed since last export (or all if no last_export_at)
            if last_export_at:
                changed_users = db.query(UserModel).filter(
                    (UserModel.updated_at != None) & (
                        (UserModel.updated_at > last_export_at) | (UserModel.created_at > last_export_at)
                    )
                ).all()
            else:
                changed_users = db.query(UserModel).all()

            # If nothing changed, return quickly
            if not changed_users:
                return {"status": "no_changes", "exported_at": datetime.utcnow().isoformat(), "total_users": 0}

            # Prepare export data (use stored hashed_password)
            users_list = []
            for user in changed_users:
                users_list.append({
                    "id": str(user.id),
                    "username": user.username,
                    "email": user.email,
                    "hashed_password": user.hashed_password,
                    "role": user.profile_type or ("admin" if getattr(user, "is_admin", False) else "user"),
                    "is_active": user.is_active,
                    "created_at": user.created_at.isoformat() if getattr(user, "created_at", None) else None,
                    "updated_at": user.updated_at.isoformat() if getattr(user, "updated_at", None) else None
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

            # Update meta file with last export time
            with open(META_FILE, "w", encoding="utf-8") as mf:
                json.dump({"exported_at": export_data["exported_at"]}, mf)

            return {
                "status": "success",
                "export_file": str(export_file),
                "total_users": len(users_list),
                "exported_at": export_data["exported_at"],
            }
        finally:
            db.close()
            
    except Exception as exc:
        # Retry on error
        raise self.retry(exc=exc, countdown=60)
