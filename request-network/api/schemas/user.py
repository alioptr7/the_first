import uuid
from datetime import datetime
from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    """Shared properties for a user."""
    username: str
    email: EmailStr
    full_name: str | None = None


class User(UserBase):
    """Properties to return to client."""
    id: uuid.UUID
    is_active: bool
    role: str
    created_at: datetime
    updated_at: datetime

    class Config:
        # This allows Pydantic to read data from ORM models (e.g., SQLAlchemy)
        from_attributes = True