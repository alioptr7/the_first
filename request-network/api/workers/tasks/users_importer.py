"""
Users Importer Task - Import users from response-network (only if changed)
"""
from datetime import datetime
import json
from pathlib import Path
import hashlib

from celery import shared_task
from sqlalchemy.orm import Session

from core.config import settings
from core.dependencies import get_db_sync
from models.user import User as UserModel

IMPORT_PATH = Path(settings.IMPORT_DIR) / "users"
PROCESSED_FILE = IMPORT_PATH / ".processed_users"


@shared_task(bind=True, max_retries=3)
def import_users_from_response_network(self):
    """
    Import users from response-network.
    
    Workflow:
    1. Check /imports/users/ for latest.json
    2. Calculate checksum and compare with last imported
    3. If changed, import/update users
    4. Save checksum for next comparison
    
    This is a DELTA sync - only updates when files change.
    """
    try:
        IMPORT_PATH.mkdir(parents=True, exist_ok=True)
        
        latest_file = IMPORT_PATH / "latest.json"
        
        # If no file exists, nothing to import
        if not latest_file.exists():
            return {
                "status": "no_file",
                "message": "No latest.json found in imports/users/",
                "imported_at": datetime.utcnow().isoformat()
            }

        # Calculate current file checksum
        with open(latest_file, "rb") as f:
            current_checksum = hashlib.sha256(f.read()).hexdigest()

        # Read previous checksum
        previous_checksum = None
        if PROCESSED_FILE.exists():
            try:
                with open(PROCESSED_FILE, "r", encoding="utf-8") as f:
                    previous_data = json.load(f)
                    previous_checksum = previous_data.get("checksum")
            except Exception:
                pass

        # If checksums match, no changes
        if previous_checksum and current_checksum == previous_checksum:
            return {
                "status": "no_changes",
                "message": "Users file has not changed",
                "imported_at": datetime.utcnow().isoformat()
            }

        # File has changed or first time, import it
        with open(latest_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        users_list = data.get("users", [])
        db = next(get_db_sync())

        try:
            imported_count = 0
            updated_count = 0

            for user_data in users_list:
                user_id = user_data.get("id")
                
                # Try to find existing user
                existing_user = db.query(UserModel).filter(
                    UserModel.id == user_id
                ).first()

                if existing_user:
                    # Update existing user
                    existing_user.username = user_data.get("username")
                    existing_user.email = user_data.get("email")
                    existing_user.hashed_password = user_data.get("hashed_password")
                    existing_user.is_active = user_data.get("is_active", True)
                    existing_user.profile_type = user_data.get("role", "user")
                    updated_count += 1
                else:
                    # Create new user
                    new_user = UserModel(
                        id=user_id,
                        username=user_data.get("username"),
                        email=user_data.get("email"),
                        hashed_password=user_data.get("hashed_password"),
                        is_active=user_data.get("is_active", True),
                        profile_type=user_data.get("role", "user")
                    )
                    db.add(new_user)
                    imported_count += 1

            db.commit()

            # Save new checksum
            with open(PROCESSED_FILE, "w", encoding="utf-8") as f:
                json.dump({
                    "checksum": current_checksum,
                    "imported_at": datetime.utcnow().isoformat(),
                    "imported_count": imported_count,
                    "updated_count": updated_count
                }, f)

            return {
                "status": "success",
                "imported_count": imported_count,
                "updated_count": updated_count,
                "checksum": current_checksum,
                "imported_at": datetime.utcnow().isoformat()
            }
        finally:
            db.close()

    except Exception as exc:
        # Retry on error
        raise self.retry(exc=exc, countdown=60)
