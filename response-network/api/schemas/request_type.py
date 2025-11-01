from datetime import datetime
from typing import Optional, List, Dict, Any, Union
from uuid import UUID
from pydantic import BaseModel, Field, constr, conint


class RequestTypeParameterBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    parameter_type: str = Field(..., pattern="^(string|number|boolean|array|object)$")
    required: bool = True
    validation_rules: Optional[Dict[str, Any]] = None
    default_value: Optional[str] = None
    example: Optional[str] = None


class RequestTypeParameterCreate(RequestTypeParameterBase):
    pass


class RequestTypeParameterRead(RequestTypeParameterBase):
    id: UUID
    request_type_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class RequestTypeAccessBase(BaseModel):
    profile_type: str = Field(..., pattern="^(admin|user|viewer)$")
    rate_limit_multiplier: float = Field(1.0, gt=0, le=10.0)  # محدودیت ضریب بین 1 تا 10 برابر
    allowed_indices: Optional[List[str]] = None  # اگر None باشد، به همه ایندکس‌ها دسترسی دارد
    is_active: bool = True


class RequestTypeAccessCreate(RequestTypeAccessBase):
    pass


class RequestTypeAccessRead(RequestTypeAccessBase):
    id: UUID
    request_type_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class RequestTypeBase(BaseModel):
    name: constr(min_length=1, max_length=100)
    description: Optional[str] = None
    query_type: str = Field(..., pattern="^(match|term|match_phrase|range|bool|exists|prefix|wildcard|regexp|fuzzy|ids|multi_match)$")
    query_type_alias: str = Field(..., min_length=1, max_length=50)
    query_template: Dict[str, Any]
    available_indices: List[str]
    max_results: conint(gt=0, le=10000) = 100
    cache_ttl: Optional[conint(gt=0)] = None
    default_rate_limit: Optional[conint(gt=0)] = None
    default_daily_limit: Optional[conint(gt=0)] = None
    requires_auth: bool = True
    is_active: bool = True
    response_template: Optional[Dict[str, Any]] = None
    error_templates: Optional[Dict[str, Dict[str, str]]] = None


class RequestTypeCreate(RequestTypeBase):
    parameters: List[RequestTypeParameterCreate]
    access_rules: Optional[List[RequestTypeAccessCreate]] = None


class RequestTypeUpdate(BaseModel):
    name: Optional[constr(min_length=1, max_length=100)] = None
    description: Optional[str] = None
    query_type: Optional[str] = Field(None, pattern="^(match|term|match_phrase|range|bool|exists|prefix|wildcard|regexp|fuzzy|ids|multi_match)$")
    query_type_alias: Optional[str] = Field(None, min_length=1, max_length=50)
    query_template: Optional[Dict[str, Any]] = None
    available_indices: Optional[List[str]] = None
    max_results: Optional[conint(gt=0, le=10000)] = None
    cache_ttl: Optional[conint(gt=0)] = None
    default_rate_limit: Optional[conint(gt=0)] = None
    default_daily_limit: Optional[conint(gt=0)] = None
    requires_auth: Optional[bool] = None
    is_active: Optional[bool] = None
    response_template: Optional[Dict[str, Any]] = None
    error_templates: Optional[Dict[str, Dict[str, str]]] = None
    parameters: Optional[List[RequestTypeParameterCreate]] = None
    access_rules: Optional[List[RequestTypeAccessCreate]] = None


class RequestTypeRead(RequestTypeBase):
    id: UUID
    created_by_id: Optional[UUID]
    created_at: datetime
    updated_at: datetime
    parameters: List[RequestTypeParameterRead]
    access_rules: List[RequestTypeAccessRead]

    class Config:
        from_attributes = True