import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

load_dotenv()

db_user = os.getenv("RESPONSE_DB_USER", "user")
db_password = os.getenv("RESPONSE_DB_PASSWORD", "password")
db_host = os.getenv("RESPONSE_DB_HOST", "localhost")
db_port = os.getenv("RESPONSE_DB_PORT", "5433")
db_name = os.getenv("RESPONSE_DB_NAME", "response_db")

# The driver is specified as 'postgresql+psycopg' to use the v3 driver
DATABASE_URL = f"postgresql+psycopg://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()