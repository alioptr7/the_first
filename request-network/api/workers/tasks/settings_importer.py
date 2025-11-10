from datetime import datetime
import json
from pathlib import Path
import asyncio

from celery import shared_task
from sqlalchemy import select

from core.config import settings
from core.dependencies import get_db
from models.settings import Settings
from schemas.settings import SettingsImport

IMPORT_PATH = Path(settings.IMPORT_DIR) / "settings"

@shared_task
def import_settings_from_response_network():
    """Import settings from response network."""
    async def _import():
        # Ensure import directory exists
        if not IMPORT_PATH.exists():
            raise FileNotFoundError(f"Import directory {IMPORT_PATH} does not exist")
            
        # Get latest settings file
        latest_file = IMPORT_PATH / "latest.json"
        if not latest_file.exists():
            raise FileNotFoundError(f"No settings file found at {latest_file}")
        
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
            
            return f"Successfully imported {len(import_data.settings)} settings"
    
    return asyncio.run(_import())