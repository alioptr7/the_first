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

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

db_user = os.getenv("RESPONSE_DB_USER")
db_password = os.getenv("RESPONSE_DB_PASSWORD")
db_host = os.getenv("RESPONSE_DB_HOST")
db_port = os.getenv("RESPONSE_DB_PORT")
db_name = os.getenv("RESPONSE_DB_NAME")

database_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
config.set_main_option('sqlalchemy.url', database_url)
# --- Custom configuration ends here ---

# Interpret the config file for Python logging.
# This line sets up loggers basically.
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.

# Add your model's MetaData object here for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = None

# other values from the config, defined by the needs of env.py,

