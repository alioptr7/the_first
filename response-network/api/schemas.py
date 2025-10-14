from pydantic import BaseModel, EmailStr, Field
import uuid
from datetime import datetime
from typing import Optional, List


# --- User Schemas ---
class UserBase(BaseModel):
    username: str
    email: EmailStr


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)


class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        orm_mode = True


# --- Responder Schemas ---
class ResponderBase(BaseModel):
    availability_status: str = "available"


class ResponderCreate(ResponderBase):
    user_id: int


class Responder(ResponderBase):
    id: uuid.UUID
    user_id: int
    user: User  # Nested User schema for reading

    class Config:
        orm_mode = True


# --- Incident Schemas ---
class IncidentBase(BaseModel):
    title: str = Field(..., max_length=255)
    description: Optional[str] = None


class IncidentCreate(IncidentBase):
    pass


class Incident(IncidentBase):
    id: uuid.UUID
    status: str
    created_at: datetime

    class Config:
        orm_mode = True


# --- Response Schemas ---
class ResponseBase(BaseModel):
    status: str = "assigned"
    notes: Optional[str] = None


class ResponseCreate(ResponseBase):
    incident_id: uuid.UUID
    responder_id: uuid.UUID


class Response(ResponseBase):
    id: uuid.UUID
    incident: Incident  # Nested Incident schema
    responder: Responder  # Nested Responder schema

    class Config:
        orm_mode = True