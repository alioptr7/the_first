"""
CRUD operations for profile type configurations
"""

from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_

from models.profile_type_config import ProfileTypeConfig
from schemas.profile_type_config import (
    ProfileTypeConfigCreate,
    ProfileTypeConfigUpdate,
    ProfileTypeConfigRead
)


async def create_profile_type(
    db: AsyncSession,
    profile_type: ProfileTypeConfigCreate
) -> ProfileTypeConfig:
    """Create a new profile type configuration"""
    db_profile_type = ProfileTypeConfig(
        name=profile_type.name,
        display_name=profile_type.display_name,
        description=profile_type.description,
        permissions=profile_type.permissions,
        daily_request_limit=profile_type.daily_request_limit,
        monthly_request_limit=profile_type.monthly_request_limit,
        max_results_per_request=profile_type.max_results_per_request,
        is_active=profile_type.is_active,
        config_metadata=profile_type.config_metadata
    )
    db.add(db_profile_type)
    await db.commit()
    await db.refresh(db_profile_type)
    return db_profile_type


async def get_profile_type(
    db: AsyncSession,
    name: str
) -> Optional[ProfileTypeConfig]:
    """Get a profile type by name"""
    result = await db.execute(
        select(ProfileTypeConfig).where(ProfileTypeConfig.name == name)
    )
    return result.scalar_one_or_none()


async def list_profile_types(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None
) -> List[ProfileTypeConfig]:
    """List all profile types"""
    query = select(ProfileTypeConfig)
    
    if is_active is not None:
        query = query.where(ProfileTypeConfig.is_active == is_active)
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


async def update_profile_type(
    db: AsyncSession,
    name: str,
    profile_type_update: ProfileTypeConfigUpdate
) -> Optional[ProfileTypeConfig]:
    """Update a profile type configuration"""
    result = await db.execute(
        select(ProfileTypeConfig).where(ProfileTypeConfig.name == name)
    )
    db_profile_type = result.scalar_one_or_none()
    
    if not db_profile_type:
        return None
    
    update_data = profile_type_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_profile_type, field, value)
    
    db.add(db_profile_type)
    await db.commit()
    await db.refresh(db_profile_type)
    return db_profile_type


async def delete_profile_type(
    db: AsyncSession,
    name: str
) -> bool:
    """Delete a profile type (only if not builtin)"""
    result = await db.execute(
        select(ProfileTypeConfig).where(ProfileTypeConfig.name == name)
    )
    db_profile_type = result.scalar_one_or_none()
    
    if not db_profile_type:
        return False
    
    if db_profile_type.is_builtin:
        raise ValueError(f"Cannot delete builtin profile type: {name}")
    
    await db.delete(db_profile_type)
    await db.commit()
    return True
