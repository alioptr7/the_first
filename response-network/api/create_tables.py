"""Create all database tables"""
import sys
import os
from pathlib import Path

# Add the api directory to path
api_dir = Path(__file__).parent
sys.path.insert(0, str(api_dir))

# Add project root to path
project_root = api_dir.parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import create_engine
from db.base_class import Base

# Import all models to register them with Base
from models import (
    User, Request, IncomingRequest, QueryResult,
    ExportBatch, ImportBatch, ExportableSettings,
    RequestType, Settings, SystemHealth, SystemLog,
    UserRequestAccess
)

from dotenv import load_dotenv
load_dotenv()

# Get database URL from environment
db_url = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5433/response_db")
print(f"Creating tables using: {db_url}")

# Create engine
engine = create_engine(db_url)

# Create all tables
print("Creating all tables...")
Base.metadata.create_all(bind=engine)
print("Tables created successfully!")

# List all tables
from sqlalchemy import inspect
inspector = inspect(engine)
tables = inspector.get_table_names()
print(f"\nCreated tables ({len(tables)}):")
for table in tables:
    print(f"  - {table}")
