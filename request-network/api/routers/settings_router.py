import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.future import select
from sqlalchemy.orm import Session

from db.session import get_db_session
from models.settings import Settings as SettingsModel
from schemas.settings import Settings as SettingsSchema
from workers.tasks.users_importer import import_users_from_response_network

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/settings", tags=["settings"])

@router.put("/system/import_config", response_model=SettingsSchema)
async def update_import_config(
    config: dict,
    db: Session = Depends(get_db_session)
):
    """
    Update import configuration (Local/FTP).
    Example config: {"type": "local", "path": "/imports"} or {"type": "ftp", "host": "...", ...}
    """
    key = "import_config"
    # Use sync-style execution for simple updates if AsyncSession is not mandatory or wrap in async
    # For Request Network which might be Sync or Async, we'll try to follow existing patterns.
    # Assuming get_db_session returns an AsyncSession based on previous files.
    
    result = await db.execute(select(SettingsModel).where(SettingsModel.key == key))
    db_setting = result.scalar_one_or_none()
    
    if db_setting:
        db_setting.value = config
    else:
        db_setting = SettingsModel(
            key=key,
            value=config,
            description="Dynamic Import Configuration (Local/FTP)",
            is_public=False
        )
        db.add(db_setting)
        
    await db.commit()
    await db.refresh(db_setting)
    
    # Trigger an immediate import check to verify config
    import_users_from_response_network.delay()
    
    return db_setting

@router.post("/system/trigger_import")
async def trigger_import():
    """Trigger user import task manually."""
    import_users_from_response_network.delay()
    return {"message": "Import task triggered"}


@router.get("/system/import_config", response_model=dict)
async def get_import_config(
    db: Session = Depends(get_db_session)
):
    """Get current import configuration."""
    result = await db.execute(select(SettingsModel).where(SettingsModel.key == "import_config"))
    setting = result.scalar_one_or_none()
    
    if not setting:
        return {"status": "not_configured"}
        
    return setting.value
