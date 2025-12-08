from datetime import datetime
import json
from pathlib import Path
import os
import asyncio

from celery import shared_task
from sqlalchemy import select

from core.config import settings
from db.session import async_session
from models.request import Request
from schemas.request import RequestExport
from services.export_storage import ExportStorageService

@shared_task
def export_completed_results():
    """Export completed request results to request network."""
    async def _export():
        async with async_session() as db:
            # Get completed requests that haven't been exported
            result = await db.execute(
                select(Request)
                .where(
                    Request.status == "completed",
                    Request.exported_at.is_(None)
                )
            )
            requests = result.scalars().all()
            
            if not requests:
                return {"status": "no_new_results", "count": 0}
            
            # Prepare export data
            export_data = {
                "requests": [
                    RequestExport(
                        id=str(req.id),
                        user_id=str(req.user_id),
                        request_type=req.request_type,
                        status=req.status,
                        created_at=req.created_at,
                        updated_at=req.updated_at,
                        result=req.result
                    ).model_dump()
                    for req in requests
                ],
                "exported_at": datetime.utcnow().isoformat(),
                "count": len(requests)
            }
            
            # Save using ExportStorageService
            filename = f"results_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
            json_data = json.dumps(export_data, indent=2, default=str).encode('utf-8')
            file_path = await ExportStorageService.save_export_file(filename, json_data)
            
            # Mark as exported
            for req in requests:
                req.exported_at = datetime.utcnow()
            await db.commit()
            
            return {
                "status": "success",
                "count": len(requests),
                "file": file_path
            }
    
    return asyncio.run(_export())