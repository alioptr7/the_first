from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
from .config import settings


def get_database_url():
    """Constructs the synchronous database URL from worker settings."""
    return (
        f"postgresql+psycopg://{settings.REQUEST_DB_USER}:{settings.REQUEST_DB_PASSWORD}@"
        f"{settings.REQUEST_DB_HOST}:{settings.REQUEST_DB_PORT}/{settings.REQUEST_DB_NAME}"
    )


engine = create_engine(
    get_database_url(),
    pool_pre_ping=True,
    # pool_size=10,  # Configure based on worker concurrency
    # max_overflow=20,
)

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

# Dependency to be used in tasks
def get_db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()