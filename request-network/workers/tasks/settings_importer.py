"""
Settings and password importer task - Auto-imports settings/passwords from Response Network
Runs every 60 seconds via Celery Beat.
"""
import json
import logging
from datetime import datetime
from pathlib import Path

from workers.celery_app import celery_app
from workers.database import db_session_scope
from workers.config import settings as worker_settings

from api.models.user import User

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Path where Response Network exports settings and passwords
EXPORT_DIR = Path("./exports")
SETTINGS_PATH = EXPORT_DIR / "settings"
PASSWORD_CHANGES_PATH = EXPORT_DIR / "password_changes"


@celery_app.task(
    name="workers.tasks.settings_importer.import_settings_and_passwords",
    autoretry_for=(Exception,),
    retry_kwargs={"max_retries": 2, "countdown": 10},
)
def import_settings_and_passwords():
    """
    Automatically imports:
    1. Settings from Response Network
    2. Password changes from Response Network
    
    Runs every 60 seconds via Celery Beat.
    No manual intervention needed.
    """
    logger.info("Starting settings and passwords import task...")
    
    results = {
        "settings_imported": 0,
        "passwords_synced": 0,
        "errors": []
    }
    
    try:
        with db_session_scope() as db:
            # ============ IMPORT PASSWORD CHANGES ============
            queue_file = PASSWORD_CHANGES_PATH / "password_changes_queue.json"
            
            if queue_file.exists():
                try:
                    with open(queue_file, "r") as f:
                        password_changes = json.load(f)
                    
                    if isinstance(password_changes, list):
                        for change_data in password_changes:
                            try:
                                user_id = change_data.get("user_id")
                                hashed_password = change_data.get("hashed_password")
                                
                                if not user_id or not hashed_password:
                                    results["errors"].append(f"Invalid password change data: {change_data}")
                                    continue
                                
                                # Find user
                                user = db.query(User).filter(User.id == user_id).first()
                                if not user:
                                    results["errors"].append(f"User {user_id} not found during password sync")
                                    continue
                                
                                # Update password
                                user.hashed_password = hashed_password
                                user.synced_at = datetime.utcnow()
                                db.add(user)
                                results["passwords_synced"] += 1
                                logger.info(f"✅ Password synced for user {user.username}")
                                
                            except Exception as e:
                                results["errors"].append(f"Error syncing password for {change_data.get('user_id')}: {str(e)}")
                                logger.error(f"Error syncing password: {e}")
                        
                        # Commit all password changes
                        db.commit()
                        
                        # Delete queue file after successful import
                        queue_file.unlink()
                        logger.info(f"✅ Password queue file deleted after import")
                        
                except json.JSONDecodeError as e:
                    results["errors"].append(f"Invalid JSON in password_changes_queue.json: {str(e)}")
                    logger.error(f"Invalid JSON in password queue: {e}")
                except Exception as e:
                    results["errors"].append(f"Error processing password changes: {str(e)}")
                    logger.error(f"Error processing password changes: {e}")
            
            # ============ IMPORT SETTINGS (Future Use) ============
            settings_file = SETTINGS_PATH / "settings_latest.json"
            
            if settings_file.exists():
                try:
                    with open(settings_file, "r") as f:
                        settings_data = json.load(f)
                    
                    # TODO: Process settings as needed
                    logger.info(f"ℹ️ Settings file found but not yet processing: {settings_file}")
                    
                except Exception as e:
                    results["errors"].append(f"Error reading settings: {str(e)}")
                    logger.error(f"Error reading settings: {e}")
    
    except Exception as e:
        logger.error(f"Critical error in settings importer: {e}")
        results["errors"].append(f"Critical error: {str(e)}")
    
    logger.info(f"Settings importer task completed: {results}")
    return results
