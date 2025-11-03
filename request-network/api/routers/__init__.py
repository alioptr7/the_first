"""Router imports"""
from api.routers.admin_router import router as admin_router
from api.routers.auth_router import router as auth_router
from api.routers.monitoring import router as monitoring_router
from api.routers.settings_router import router as settings_router
from api.routers.stats_router import router as stats_router
from api.routers.system_router import router as system_router
from api.routers.user_management_router import router as user_management_router
from api.routers.user_router import router as user_router

__all__ = [
    "admin_router",
    "auth_router",
    "monitoring_router",
    "settings_router",
    "stats_router",
    "system_router",
    "user_management_router",
    "user_router",
]