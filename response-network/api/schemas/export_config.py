"""
Export Configuration Schemas
"""
from pydantic import BaseModel, Field
from typing import List


class ExportConfigUpdate(BaseModel):
    """Configuration for what data gets exported to Request Network"""
    
    settings_export_enabled: bool = Field(default=True, description="Export Settings")
    settings_filter_by_is_public: bool = Field(default=True, description="Only export Settings with is_public=true")
    
    users_export_enabled: bool = Field(default=True, description="Export Users")
    users_filter_by_is_active: bool = Field(default=True, description="Only export active users")
    users_include_roles: List[str] = Field(default=["admin", "user"], description="Which roles to export")
    
    profile_types_export_enabled: bool = Field(default=True, description="Export ProfileTypes")
    profile_types_filter_by_is_active: bool = Field(default=True, description="Only export active ProfileTypes")
    
    export_interval_seconds: int = Field(default=60, ge=10, le=3600, description="Export interval in seconds")


class ExportConfigResponse(BaseModel):
    """Response with current export configuration"""
    
    settings_export_enabled: bool
    settings_filter_by_is_public: bool
    
    users_export_enabled: bool
    users_filter_by_is_active: bool
    users_include_roles: List[str]
    
    profile_types_export_enabled: bool
    profile_types_filter_by_is_active: bool
    
    export_interval_seconds: int
    message: str = ""


class ExportStatusResponse(BaseModel):
    """Status of exports"""
    
    settings: dict = Field(description="Settings export status")
    users: dict = Field(description="Users export status")
    profile_types: dict = Field(description="ProfileTypes export status")
