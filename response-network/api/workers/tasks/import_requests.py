from datetime import datetime
import json
from pathlib import Path
import asyncio

from celery import shared_task
from sqlalchemy import select

from core.config import settings
from core.dependencies import get_db
from models.request import Request
from schemas.request import RequestImport

IMPORT_PATH = Path(settings.IMPORT_DIR) / "requests"

@shared_task
def import_requests_from_request_network():
    """Import new requests from request network."""
    async def _import():
        if not IMPORT_PATH.exists():
            raise FileNotFoundError(f"Import directory {IMPORT_PATH} does not exist")
        
        # Get all JSON files in import directory that haven't been processed
        imported_files = []
        for file in IMPORT_PATH.glob("*.json"):
            if file.stem == "latest":
                continue
                
            with open(file, "r", encoding="utf-8") as f:
                data = json.load(f)
                import_data = RequestImport(**data)
            
            async with get_db() as db:
                for request in import_data.requests:
                    # Check if request already exists
                    result = await db.execute(
                        select(Request).where(Request.external_id == request.id)
                    )
                    if not result.scalar_one_or_none():
                        # Create new request
                        new_request = Request(
                            external_id=request.id,
                            query=request.query,
                            parameters=request.parameters,
                            priority=request.priority,
                            status="pending",
                            created_at=request.created_at
                        )
                        db.add(new_request)
                
                await db.commit()
            
            # Move processed file to archive
            archive_dir = IMPORT_PATH / "archive"
            archive_dir.mkdir(exist_ok=True)
            file.rename(archive_dir / file.name)
            imported_files.append(file.name)
        
        return f"Processed {len(imported_files)} files: {', '.join(imported_files)}"
    
    return asyncio.run(_import())