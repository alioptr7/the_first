from datetime import datetime
import json
from pathlib import Path
import asyncio

from celery import shared_task
from sqlalchemy import select

from core.config import settings
from db.session import async_session
from models.request import Request
from schemas.request import RequestExport

EXPORT_PATH = Path(settings.EXPORT_DIR) / "results"

@shared_task
def export_completed_results():
    """Export completed request results to request network."""
    async def _export():
        EXPORT_PATH.mkdir(parents=True, exist_ok=True)
        
        async with async_session() as db:
            # Get completed requests that haven't been exported
            result = await db.execute(
                select(Request)
                .where(
                    Request.status == "completed",
                    Request.exported_at.is_(None)
                )
            )
            completed_requests = result.scalars().all()
            
            if not completed_requests:
                return "No new results to export"
            
            # Prepare export data
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            export_data = RequestExport(
                requests=[req.to_export() for req in completed_requests],
                exported_at=datetime.utcnow(),
                version=1
            )
            
            # Write to file
            export_file = EXPORT_PATH / f"results_{timestamp}.json"
            with open(export_file, "w", encoding="utf-8") as f:
                json.dump(export_data.model_dump(), f, ensure_ascii=False, indent=2)
            
            # Write latest file
            latest_file = EXPORT_PATH / "latest.json"
            with open(latest_file, "w", encoding="utf-8") as f:
                json.dump(export_data.model_dump(), f, ensure_ascii=False, indent=2)
            
            # Update exported_at timestamp
            for request in completed_requests:
                request.exported_at = datetime.utcnow()
            
            await db.commit()
            
            return f"Exported {len(completed_requests)} results to {export_file}"
    
    return asyncio.run(_export())