from fastapi import FastAPI, Request

# PYTHONPATH باید شامل ریشه پروژه باشد تا این import کار کند
from shared.logger import get_logger

log = get_logger(__name__)

app = FastAPI(
    title="Request Network API",
    description="API for submitting and managing requests in the air-gapped system.",
    version="0.1.0",
)

@app.on_event("startup")
async def startup_event():
    log.info("Application startup...")

@app.get("/")
async def root():
    return {"message": "Welcome to the Request Network API"}

@app.get("/health", tags=["Monitoring"])
async def health_check():
    log.debug("Health check endpoint was hit")
    return {"status": "ok"}