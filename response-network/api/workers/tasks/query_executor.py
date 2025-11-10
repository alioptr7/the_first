import asyncio
from datetime import datetime

from celery import shared_task
from sqlalchemy import select

from core.config import settings
from core.dependencies import get_db
from models.request import Request
from services.query_executor import QueryExecutor

@shared_task
def execute_pending_queries():
    """Execute pending queries in order of priority."""
    async def _execute():
        async with get_db() as db:
            # Get pending requests ordered by priority and creation date
            result = await db.execute(
                select(Request)
                .where(Request.status == "pending")
                .order_by(Request.priority.desc(), Request.created_at.asc())
                .limit(settings.MAX_BATCH_SIZE)
            )
            requests = result.scalars().all()
            
            executor = QueryExecutor()
            processed = 0
            
            for request in requests:
                try:
                    # Execute query
                    result = await executor.execute(request.query, request.parameters)
                    
                    # Update request with results
                    request.results = result
                    request.status = "completed"
                    request.completed_at = datetime.utcnow()
                    processed += 1
                except Exception as e:
                    request.status = "failed"
                    request.error = str(e)
                    request.completed_at = datetime.utcnow()
                
                # Save changes for each request immediately
                await db.commit()
            
            return f"Processed {processed} out of {len(requests)} requests"
    
    return asyncio.run(_execute())