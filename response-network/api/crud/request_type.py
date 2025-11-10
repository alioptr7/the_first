from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from models.request_type import RequestType
from models.request_type_parameter import RequestTypeParameter
from schemas.request_type import RequestTypeCreate, RequestTypeUpdate
from crud.base import CRUDBase


class CRUDRequestType(CRUDBase[RequestType, RequestTypeCreate, RequestTypeUpdate]):
    async def create_with_parameters(
        self, db: AsyncSession, *, obj_in: RequestTypeCreate, created_by_id: UUID
    ) -> RequestType:
        # Create request type
        db_obj = RequestType(
            name=obj_in.name,
            description=obj_in.description,
            is_active=obj_in.is_active,
            is_public=obj_in.is_public,
            version=obj_in.version,
            max_items_per_request=obj_in.max_items_per_request,
            available_indices=obj_in.available_indices,
            created_by_id=created_by_id,
        )
        db.add(db_obj)
        await db.flush()  # Get the ID without committing

        # Create parameters
        for param in obj_in.parameters:
            db_param = RequestTypeParameter(
                request_type_id=db_obj.id,
                name=param.name,
                description=param.description,
                parameter_type=param.parameter_type,
                is_required=param.is_required,
                validation_rules=param.validation_rules,
            )
            db.add(db_param)
        
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update_with_parameters(
        self, db: AsyncSession, *, db_obj: RequestType, obj_in: RequestTypeUpdate
    ) -> RequestType:
        # Update request type fields
        update_data = obj_in.model_dump(exclude_unset=True)
        if "parameters" in update_data:
            parameters = update_data.pop("parameters")
            
            # Delete existing parameters
            await db.execute(
                select(RequestTypeParameter).where(RequestTypeParameter.request_type_id == db_obj.id)
            )
            
            # Create new parameters
            for param in parameters:
                db_param = RequestTypeParameter(
                    request_type_id=db_obj.id,
                    name=param.name,
                    description=param.description,
                    parameter_type=param.parameter_type,
                    is_required=param.is_required,
                    validation_rules=param.validation_rules,
                )
                db.add(db_param)
        
        # Update other fields
        if update_data:
            await db.execute(
                update(RequestType)
                .where(RequestType.id == db_obj.id)
                .values(**update_data)
            )
        
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def get_active(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> List[RequestType]:
        result = await db.execute(
            select(RequestType)
            .where(RequestType.is_active == True)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_by_name(
        self, db: AsyncSession, *, name: str
    ) -> Optional[RequestType]:
        result = await db.execute(
            select(RequestType).where(RequestType.name == name)
        )
        return result.scalar_one_or_none()


request_type = CRUDRequestType(RequestType)