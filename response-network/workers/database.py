"""تنظیمات پایگاه داده برای شبکه پاسخ"""
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from workers.config import settings

engine = create_engine(settings.RESPONSE_DB_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@contextmanager
def db_session_scope():
    """Provide a transactional scope around a series of operations for workers."""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

@contextmanager
def get_db_session():
    """Get a database session for use in tasks."""
    with db_session_scope() as session:
        yield session