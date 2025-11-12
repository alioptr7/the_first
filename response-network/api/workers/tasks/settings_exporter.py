from datetime import datetime
import json
from pathlib import Path
import asyncio

from celery import shared_task
from sqlalchemy import select

from core.config import settings
from core.dependencies import get_db
from models.settings import Settings as SettingsModel
from schemas.settings import SettingsExport, Settings as SettingsSchema

EXPORT_PATH = Path(settings.EXPORT_DIR) / "settings"

@shared_task
def export_settings_to_request_network():
    """Export all public settings to file."""
    async def _export():
        # Create export directory if it doesn't exist
        EXPORT_PATH.mkdir(parents=True, exist_ok=True)
        
        # Get current timestamp for filename
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        
        async with get_db() as db:
            # Get all public settings
            result = await db.execute(
                select(SettingsModel).where(SettingsModel.is_public == True)
            )
            all_settings = result.scalars().all()
            
            # Prepare export data
            settings_list = []
            for setting in all_settings:
                settings_list.append({
                    "key": setting.key,
                    "value": setting.value,
                    "description": setting.description,
                    "is_public": setting.is_public,
                    "created_at": setting.created_at.isoformat() if setting.created_at else None,
                    "updated_at": setting.updated_at.isoformat() if setting.updated_at else None
                })
            
            export_data = {
                "settings": settings_list,
                "exported_at": datetime.utcnow().isoformat(),
                "version": 1,
                "total_count": len(settings_list)
            }
            
            # Write to file
            export_file = EXPORT_PATH / f"settings_{timestamp}.json"
            with open(export_file, "w", encoding="utf-8") as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
            
            # Write latest.json for easy access
            latest_file = EXPORT_PATH / "latest.json"
            with open(latest_file, "w", encoding="utf-8") as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
            
            return {
                "export_file": str(export_file),
                "total_settings": len(settings_list),
                "exported_at": datetime.utcnow().isoformat()
            }
    
    return asyncio.run(_export())