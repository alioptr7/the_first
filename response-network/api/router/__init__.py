from router.request_router import router as request_router
from router.system_router import router as system_router
from router.user_router import router as user_router
from router.monitoring_router import router as monitoring_router
from router.stats_router import router as stats_router
from router.auth_router import router as auth_router
from router.request_type_router import router as request_type_router

__all__ = [
    "request_router",
    "system_router",
    "user_router",
    "monitoring_router",
    "stats_router",
    "auth_router",
    "request_type_router",
]
