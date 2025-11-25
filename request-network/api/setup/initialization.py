"""
Database initialization for Request Network startup
Request Network users are automatically imported from Response Network
"""
import sys
from pathlib import Path
import logging

# Setup paths
_api_dir = Path(__file__).resolve().parent.parent
_project_root = _api_dir.parent.parent
sys.path.insert(0, str(_project_root))
sys.path.insert(0, str(_api_dir))

from db.session import SessionLocal

logger = logging.getLogger(__name__)


def initialize_database():
    """
    Initialize Request Network database
    Note: Users are synced from Response Network via import workers
    """
    logger.info("Initializing Request Network database...")
    
    try:
        db = SessionLocal()
        
        # Just verify connection
        db.execute("SELECT 1")
        
        logger.info("✓ Request Network database initialized")
        return True
        
    except Exception as e:
        logger.error(f"Failed to initialize Request Network: {e}")
        return False
    finally:
        db.close()
