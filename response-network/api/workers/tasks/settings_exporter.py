from datetime import datetime
import json
from pathlib import Path

from celery import shared_task
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.dependencies import get_db
from models.settings import Settings
from schemas.settings import SettingsExport

EXPORT_PATH = Path(settings.EXPORT_DIR) / "settings"

@shared_task
def export_settings_to_request_network():
    """Export all settings to request network."""
    async def _export():
        # Create export directory if it doesn't exist
        EXPORT_PATH.mkdir(parents=True, exist_ok=True)
        
        # Get current timestamp for filename
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        
        async with get_db() as db:
            # Get all active settings
            result = await db.execute(
                select(Settings).where(Settings.is_active == True)
            )
            all_settings = result.scalars().all()
            
            # Prepare export data
            export_data = SettingsExport(
                settings=[setting.to_read() for setting in all_settings],
                exported_at=datetime.utcnow(),
                version=1  # Increment this when format changes
            )
            
            # Write to file
            export_file = EXPORT_PATH / f"settings_{timestamp}.json"
            with open(export_file, "w", encoding="utf-8") as f:
                json.dump(export_data.model_dump(), f, ensure_ascii=False, indent=2)
            
            # Write latest.json for easy access
            latest_file = EXPORT_PATH / "latest.json"
            with open(latest_file, "w", encoding="utf-8") as f:
                json.dump(export_data.model_dump(), f, ensure_ascii=False, indent=2)
            
            return str(export_file)
    
    return asyncio.run(_export())