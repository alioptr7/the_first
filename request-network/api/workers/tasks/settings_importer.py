from datetime import datetime
import json
from pathlib import Path
import asyncio

from celery import shared_task
from sqlalchemy import select

from core.config import settings
from db.session import get_db_session as get_db
from models.settings import Settings
from models.user import User
from schemas.settings import SettingsImport

IMPORT_PATH = Path(settings.IMPORT_DIR) / "settings"
PASSWORD_CHANGES_PATH = Path(settings.EXPORT_DIR) / "password_changes"

@shared_task
def import_settings_from_response_network():
    """
    Import settings from response network.
    
    Also automatically processes password changes if available:
    - Checks for password_changes_queue.json
    - Updates user passwords automatically
    - No manual intervention needed
    """
    async def _import():
        # Track results
        results = {
            "settings_imported": 0,
            "passwords_synced": 0,
            "errors": []
        }
        
        # ============ IMPORT SETTINGS ============
        try:
            # Ensure import directory exists
            if not IMPORT_PATH.exists():
                results["errors"].append(f"Import directory {IMPORT_PATH} does not exist")
            else:
                # Get latest settings file
                latest_file = IMPORT_PATH / "latest.json"
                if latest_file.exists():
                    # Read settings data
                    with open(latest_file, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        import_data = SettingsImport(**data)
                    
                    async with get_db() as db:
                        # For each imported setting
                        for setting in import_data.settings:
                            # Check if setting already exists
                            result = await db.execute(
                                select(Settings).where(Settings.key == setting.key)
                            )
                            existing = result.scalar_one_or_none()
                            
                            if existing:
                                # Update existing setting
                                existing.value = setting.value
                                existing.description = setting.description
                                existing.is_active = True
                                existing.updated_at = datetime.utcnow()
                            else:
                                # Create new setting
                                new_setting = Settings(
                                    key=setting.key,
                                    value=setting.value,
                                    description=setting.description,
                                    is_active=True,
                                )
                                db.add(new_setting)
                        
                        await db.commit()
                        results["settings_imported"] = len(import_data.settings)
        except Exception as e:
            results["errors"].append(f"Settings import error: {str(e)}")
        
        # ============ AUTO-SYNC PASSWORD CHANGES ============
        try:
            queue_file = PASSWORD_CHANGES_PATH / "password_changes_queue.json"
            
            if queue_file.exists():
                # Read password changes
                with open(queue_file, "r") as f:
                    password_changes = json.load(f)
                
                if not isinstance(password_changes, list):
                    password_changes = [password_changes]
                
                async with get_db() as db:
                    # Apply each password change
                    for change in password_changes:
                        try:
                            user_id = change.get("user_id")
                            hashed_password = change.get("hashed_password")
                            username = change.get("username")
                            
                            if not user_id or not hashed_password:
                                results["errors"].append(
                                    f"Invalid password change for {username}: missing user_id or hashed_password"
                                )
                                continue
                            
                            # Get user
                            result = await db.execute(
                                select(User).where(User.id == user_id)
                            )
                            user = result.scalar_one_or_none()
                            
                            if not user:
                                results["errors"].append(f"User {username} ({user_id}) not found")
                                continue
                            
                            # Update password
                            user.hashed_password = hashed_password
                            user.synced_at = datetime.utcnow()
                            db.add(user)
                            results["passwords_synced"] += 1
                            
                        except Exception as e:
                            results["errors"].append(
                                f"Error syncing password for {change.get('username', 'unknown')}: {str(e)}"
                            )
                    
                    await db.commit()
                
                # Delete queue file after successful import
                if results["passwords_synced"] > 0:
                    queue_file.unlink()
                    
        except FileNotFoundError:
            # No password changes to sync, this is normal
            pass
        except Exception as e:
            results["errors"].append(f"Password sync error: {str(e)}")
        
        # Return summary
        message = f"✅ Settings: {results['settings_imported']}, Passwords: {results['passwords_synced']}"
        if results["errors"]:
            message += f" | ⚠️ {len(results['errors'])} errors"
        
        return {
            "status": "success",
            "message": message,
            "results": results,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    return asyncio.run(_import())