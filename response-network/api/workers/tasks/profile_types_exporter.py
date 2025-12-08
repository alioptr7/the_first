"""
Export profile types to Request Network
"""
from datetime import datetime
import json
import asyncio

from celery import shared_task
from sqlalchemy import select

from db.session import async_session
from models.profile_type_config import ProfileTypeConfig
from services.export_storage import ExportStorageService


@shared_task
def export_profile_types_to_request_network():
    """Export all active profile types to Request Network."""
    
    async def _export():
        async with async_session() as db:
            # Get all active profile types
            result = await db.execute(
                select(ProfileTypeConfig).where(ProfileTypeConfig.is_active == True)
            )
            profile_types = result.scalars().all()
            
            # Prepare export data
            export_data = {
                "profile_types": [
                    {
                        "name": pt.name,
                        "display_name": pt.display_name,
                        "description": pt.description,
                        "permissions": pt.permissions,
                        "daily_request_limit": pt.daily_request_limit,
                        "monthly_request_limit": pt.monthly_request_limit,
                        "is_active": pt.is_active,
                    }
                    for pt in profile_types
                ],
                "exported_at": datetime.utcnow().isoformat(),
                "total_count": len(profile_types),
            }
            
            # Save using ExportStorageService
            filename = f"profile_types_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
            json_data = json.dumps(export_data, indent=2, default=str).encode('utf-8')
            file_path = await ExportStorageService.save_export_file(filename, json_data)
            
            return {
                "status": "success",
                "exported_at": export_data["exported_at"],
                "total_count": len(profile_types),
                "file": file_path
            }
    
    return asyncio.run(_export())
