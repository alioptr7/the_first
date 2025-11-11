"""Worker settings CRUD operations."""
from typing import Optional, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from models.worker_settings import WorkerSettings
from schemas.worker_settings import WorkerSettingsCreate, WorkerSettingsUpdate

class WorkerSettingsCrud:
    """CRUD operations for worker settings."""
    
    async def create(self, db: AsyncSession, obj_in: WorkerSettingsCreate) -> WorkerSettings:
        """Create a new worker settings."""
        db_obj = WorkerSettings(**obj_in.dict())
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def get(self, db: AsyncSession, id: UUID) -> Optional[WorkerSettings]:
        """Get worker settings by id."""
        result = await db.execute(
            select(WorkerSettings).where(WorkerSettings.id == id)
        )
        return result.scalars().first()
    
    async def get_all(self, db: AsyncSession) -> List[WorkerSettings]:
        """Get all worker settings."""
        result = await db.execute(select(WorkerSettings))
        return result.scalars().all()
    
    async def update(
        self, 
        db: AsyncSession, 
        id: UUID, 
        obj_in: WorkerSettingsUpdate
    ) -> Optional[WorkerSettings]:
        """Update worker settings."""
        db_obj = await self.get(db, id)
        if db_obj:
            for field, value in obj_in.dict(exclude_unset=True).items():
                setattr(db_obj, field, value)
            await db.commit()
            await db.refresh(db_obj)
        return db_obj
    
    async def delete(self, db: AsyncSession, id: UUID) -> bool:
        """Delete worker settings."""
        db_obj = await self.get(db, id)
        if db_obj:
            await db.delete(db_obj)
            await db.commit()
            return True
        return False

worker_settings_crud = WorkerSettingsCrud()