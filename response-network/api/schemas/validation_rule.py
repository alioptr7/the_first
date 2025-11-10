from typing import Dict, Optional, List
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field


class ValidationRuleBase(BaseModel):
    """Base schema for validation rules."""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    rules: Dict = Field(..., description="The actual validation rules")
    version: int = Field(default=1)
    is_active: bool = Field(default=True)


class ValidationRuleCreate(ValidationRuleBase):
    """Schema for creating a new validation rule."""
    pass


class ValidationRuleUpdate(BaseModel):
    """Schema for updating an existing validation rule."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    rules: Optional[Dict] = None
    version: Optional[int] = None
    is_active: Optional[bool] = None


class ValidationRuleRead(ValidationRuleBase):
    """Schema for reading a validation rule."""
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ValidationRuleExport(BaseModel):
    """Schema for exporting validation rules to request network."""
    rules: List[ValidationRuleRead]
    exported_at: datetime = Field(default_factory=datetime.utcnow)
    version: int