from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from db.session import get_db_session

async def get_db() -> Session:
    """Get database session."""
    db = get_db_session()
    try:
        yield db
    finally:
        db.close()