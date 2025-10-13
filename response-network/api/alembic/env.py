import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# --- Custom configuration starts here ---
from dotenv import load_dotenv

# This is the correct way to handle imports for a flat structure.
# We ensure alembic knows where to find our modules by adding the parent dir.
import sys
sys.path.insert(0, os.path.realpath(os.path.join(os.path.dirname(__file__), '..')))

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

db_user = os.getenv("RESPONSE_DB_USER")
db_password = os.getenv("RESPONSE_DB_PASSWORD")
db_host = os.getenv("RESPONSE_DB_HOST")
db_port = os.getenv("RESPONSE_DB_PORT")
db_name = os.getenv("RESPONSE_DB_NAME")

# The driver is specified as 'postgresql+psycopg' to use the v3 driver
database_url = f"postgresql+psycopg://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
config.set_main_option('sqlalchemy.url', database_url)
# --- Custom configuration ends here ---

# Interpret the config file for Python logging.
# This line sets up loggers basically.
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.

from database import Base
from user import User  # Import all your models here
from incoming_request import IncomingRequest
from query_result import QueryResult
from import_batch import ImportBatch
from export_batch import ExportBatch # Ensure this line is NOT commented out
from query_cache import QueryCache
from system_log import SystemLog

# Add your model's MetaData object here for 'autogenerate' support.
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
