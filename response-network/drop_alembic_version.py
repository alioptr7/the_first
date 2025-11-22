#!/usr/bin/env python
import os
import sys
from sqlalchemy import create_engine, text

# Add paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'api'))
sys.path.insert(0, os.path.dirname(__file__))

# Build database URL from env vars
user = os.getenv("REQUEST_DB_USER", "responses_user")
password = os.getenv("REQUEST_DB_PASSWORD", "responses_pass")
host = os.getenv("REQUEST_DB_HOST", "localhost")
port = os.getenv("REQUEST_DB_PORT", "5432")
db_name = os.getenv("REQUEST_DB_NAME", "responses_db")
url = f"postgresql+psycopg://{user}:{password}@{host}:{port}/{db_name}"

# Create engine and drop table
engine = create_engine(url)
with engine.connect() as conn:
    conn.execute(text("DROP TABLE IF EXISTS alembic_version"))
    conn.commit()
    print("✓ alembic_version table dropped")
