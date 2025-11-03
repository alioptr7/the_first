"""System router"""
import platform
import psutil
from typing import Annotated, Dict

from fastapi import APIRouter, Depends

from api.auth.dependencies import get_current_admin_user
from api.models.user import User

router = APIRouter(prefix="/system", tags=["system"])


@router.get("/info")
async def get_system_info(
    _: Annotated[User, Depends(get_current_admin_user)],
) -> Dict:
    """Get system information"""
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage("/")

    return {
        "system": {
            "os": platform.system(),
            "version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
        },
        "resources": {
            "cpu": {
                "percent": cpu_percent,
                "cores": psutil.cpu_count(),
                "physical_cores": psutil.cpu_count(logical=False),
            },
            "memory": {
                "total": memory.total,
                "available": memory.available,
                "percent": memory.percent,
            },
            "disk": {
                "total": disk.total,
                "used": disk.used,
                "free": disk.free,
                "percent": disk.percent,
            },
        },
    }