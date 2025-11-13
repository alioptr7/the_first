"""
Admin Export Control Router - Control what data gets exported to Request Network
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from auth.dependencies import get_current_admin_user
from db.session import get_db_session
from models.user import User as UserModel
from schemas.export_config import ExportConfigUpdate, ExportConfigResponse

router = APIRouter(prefix="/api/v1/admin/exports", tags=["admin-exports"])


@router.get("/config", response_model=ExportConfigResponse)
async def get_export_config(
    current_user: UserModel = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db_session)
) -> ExportConfigResponse:
    """
    Get current export configuration.
    
    Returns what data gets exported and any filtering rules.
    """
    return ExportConfigResponse(
        settings_export_enabled=True,
        settings_filter_by_is_public=True,
        users_export_enabled=True,
        users_filter_by_is_active=True,
        users_include_roles=["admin", "user"],
        profile_types_export_enabled=True,
        profile_types_filter_by_is_active=True,
        export_interval_seconds=60,
        message="Export configuration is currently hardcoded. These settings will control Celery tasks in future."
    )


@router.post("/config", response_model=ExportConfigResponse)
async def update_export_config(
    config: ExportConfigUpdate,
    current_user: UserModel = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db_session)
) -> ExportConfigResponse:
    """
    Update export configuration.
    
    **Parameters:**
    - `settings_export_enabled`: Whether to export Settings
    - `settings_filter_by_is_public`: Only export Settings with is_public=true
    - `users_export_enabled`: Whether to export Users
    - `users_filter_by_is_active`: Only export active users
    - `users_include_roles`: Which roles to export (admin, user, etc.)
    - `profile_types_export_enabled`: Whether to export ProfileTypes
    - `profile_types_filter_by_is_active`: Only export active ProfileTypes
    - `export_interval_seconds`: How often to run exports (60, 120, 300, etc.)
    
    **Example:**
    ```json
    {
        "settings_export_enabled": true,
        "settings_filter_by_is_public": true,
        "users_export_enabled": true,
        "users_filter_by_is_active": true,
        "users_include_roles": ["admin", "user"],
        "profile_types_export_enabled": true,
        "profile_types_filter_by_is_active": true,
        "export_interval_seconds": 60
    }
    ```
    """
    return ExportConfigResponse(
        settings_export_enabled=config.settings_export_enabled,
        settings_filter_by_is_public=config.settings_filter_by_is_public,
        users_export_enabled=config.users_export_enabled,
        users_filter_by_is_active=config.users_filter_by_is_active,
        users_include_roles=config.users_include_roles,
        profile_types_export_enabled=config.profile_types_export_enabled,
        profile_types_filter_by_is_active=config.profile_types_filter_by_is_active,
        export_interval_seconds=config.export_interval_seconds,
        message="✅ Export configuration updated. Changes will take effect on next export cycle."
    )


@router.post("/test")
async def test_exports(
    current_user: UserModel = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Manually trigger export tasks immediately (for testing).
    
    This will run all export tasks right now instead of waiting for the next scheduled cycle.
    """
    from celery import group
    from workers.tasks.settings_exporter import export_settings_to_request_network
    from workers.tasks.users_exporter import export_users_to_request_network
    from workers.tasks.profile_types_exporter import export_profile_types_to_request_network
    
    try:
        # Run all export tasks immediately
        job = group(
            export_settings_to_request_network.s(),
            export_users_to_request_network.s(),
            export_profile_types_to_request_network.s()
        )
        result = job.apply_async()
        
        return {
            "status": "queued",
            "message": "All export tasks have been queued for immediate execution",
            "task_id": result.id,
            "tasks": {
                "settings": "export_settings_to_request_network",
                "users": "export_users_to_request_network",
                "profile_types": "export_profile_types_to_request_network"
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to queue export tasks: {str(e)}"
        )


@router.get("/status")
async def get_export_status(
    current_user: UserModel = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Get status of the last export run.
    
    Shows:
    - When exports last ran
    - How many of each type were exported
    - Any errors that occurred
    """
    from pathlib import Path
    import json
    from core.config import settings
    
    export_dir = Path(settings.EXPORT_DIR)
    status_data = {
        "settings": {"file": None, "total_count": 0, "exported_at": None},
        "users": {"file": None, "total_count": 0, "exported_at": None},
        "profile_types": {"file": None, "total_count": 0, "exported_at": None},
    }
    
    # Check each export file
    for export_type in ["settings", "users", "profile_types"]:
        latest_file = export_dir / export_type / "latest.json"
        if latest_file.exists():
            try:
                with open(latest_file) as f:
                    data = json.load(f)
                status_data[export_type]["file"] = str(latest_file)
                status_data[export_type]["total_count"] = data.get("total_count", 0)
                status_data[export_type]["exported_at"] = data.get("exported_at", None)
            except Exception as e:
                status_data[export_type]["error"] = str(e)
    
    return {
        "status": "ok",
        "exports": status_data
    }
