import sys
from pathlib import Path
from fastapi import Depends, FastAPI, Request
from starlette.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

# --- Start of Path Fix ---
# Add project root to the Python path to allow imports from `shared`
api_dir = Path(__file__).resolve().parent
project_root = api_dir.parent

# Insert api_dir FIRST so local modules take precedence
if str(api_dir) not in sys.path:
    sys.path.insert(0, str(api_dir))
    
if str(project_root) not in sys.path:
    sys.path.insert(1, str(project_root))
# --- End of Path Fix ---

from core.config import settings
from core.middleware import RequestContextMiddleware
from core.rate_limiter import RateLimiter
from core.exceptions import global_exception_handler
from db.session import get_db_session
from routers import auth_router, request_router, admin_router
from routers import users as users_router  # Import users router
from shared.logger import get_logger

log = get_logger(__name__, level=settings.LOG_LEVEL)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API for submitting and managing requests in the air-gapped system.",
    version="0.1.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

# Add Exception Handlers
app.add_exception_handler(Exception, global_exception_handler)

# Add Middlewares
app.add_middleware(RequestContextMiddleware)

# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Include API routers
app.include_router(auth_router.router, prefix=settings.API_V1_STR)
app.include_router(users_router.router, prefix=settings.API_V1_STR)
app.include_router(request_router.router, prefix=settings.API_V1_STR)
app.include_router(admin_router.router, prefix=settings.API_V1_STR)


@app.on_event("startup")
async def startup_event():
    log.info("Application startup...", api_version=app.version)

@app.get(f"{settings.API_V1_STR}/", tags=["Root"])
async def root():
    return {"message": "Welcome to the Request Network API"}

@app.get(f"{settings.API_V1_STR}/health", tags=["Monitoring"])
async def health_check():
    return {"status": "ok"}

@app.get(f"{settings.API_V1_STR}/health/ready", tags=["Monitoring"])
async def readiness_check(db: AsyncSession = Depends(get_db_session)):
    """
    Checks if the service is ready to accept traffic (e.g., DB is connected).
    """
    try:
        await db.execute(text("SELECT 1"))
        return {"status": "ok", "database": "connected"}
    except Exception as e:
        log.error("Readiness check failed: Database connection error.", error=str(e))
        return {"status": "error", "database": "disconnected"}
