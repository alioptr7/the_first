import uuid
from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    """Shared properties for a user."""
    email: EmailStr
    full_name: str | None = None
    username: str


class UserRead(UserBase):
    """Properties to return to a client."""
    id: uuid.UUID
    profile_type: str
    is_active: bool

    class Config:
        # This tells Pydantic to read data from object attributes (ORM mode)
        from_attributes = True