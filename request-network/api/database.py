import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

load_dotenv()

db_user = os.getenv("REQUEST_DB_USER", "user")
db_password = os.getenv("REQUEST_DB_PASSWORD", "password")
db_host = os.getenv("REQUEST_DB_HOST", "localhost")
db_port = os.getenv("REQUEST_DB_PORT", "5432")
db_name = os.getenv("REQUEST_DB_NAME", "request_db")

DATABASE_URL = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()