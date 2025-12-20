from db.session import get_db_session as get_db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core.config import settings

# Sync DB setup for Celery tasks
sync_engine = create_engine(
    str(settings.DATABASE_URL).replace('postgresql+asyncpg', 'postgresql'),
    pool_pre_ping=True
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)

def get_db_sync():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
