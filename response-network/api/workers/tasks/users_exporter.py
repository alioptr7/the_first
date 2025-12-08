"""
Users export task - Export users to request-network
"""
from datetime import datetime
import json
import asyncio

from celery import shared_task
from sqlalchemy import select

from db.session import async_session
from models.user import User
from services.export_storage import ExportStorageService


@shared_task
def export_users_to_request_network():
    """Export all active users to Request Network."""
    
    async def _export():
        async with async_session() as db:
            # Get all active users
            result = await db.execute(
                select(User).where(User.is_active == True)
            )
            users = result.scalars().all()
            
            # Prepare export data
            export_data = {
                "users": [
                    {
                        "id": str(user.id),
                        "username": user.username,
                        "email": user.email,
                        "hashed_password": user.hashed_password,
                        "role": user.profile_type or "user",
                        "is_active": user.is_active,
                        "created_at": user.created_at.isoformat() if user.created_at else None,
                        "updated_at": user.updated_at.isoformat() if user.updated_at else None
                    }
                    for user in users
                ],
                "exported_at": datetime.utcnow().isoformat(),
                "total_count": len(users),
            }
            
            # Save using ExportStorageService
            filename = f"users_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
            json_data = json.dumps(export_data, indent=2, default=str).encode('utf-8')
            file_path = await ExportStorageService.save_export_file(filename, json_data)
            
            return {
                "status": "success",
                "exported_at": export_data["exported_at"],
                "total_count": len(users),
                "file": file_path
            }
    
    return asyncio.run(_export())
