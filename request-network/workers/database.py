from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager

# This needs to be configured to read from the same .env file as the API
# For now, we hardcode it, but it should use the worker's settings.
# Let's assume the API's DB_URL is accessible or configured for the worker.
DATABASE_URL = "postgresql+psycopg://user:password@postgres-request:5432/request_db"

engine = create_engine(
    DATABASE_URL,
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