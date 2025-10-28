import os
import sys
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool
from dotenv import load_dotenv

# --- Path Setup ---
# This allows Alembic to find your models.
# Add the 'api' directory to the path to find local models.
api_dir = os.path.realpath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, api_dir)
# Add the project root to the path to find the 'shared' module.
sys.path.insert(0, os.path.realpath(os.path.join(api_dir, "..", "..")))

# --- Environment Variables ---
# Load environment variables from a .env file if it exists.
# This is useful for local development.
load_dotenv()

# --- Alembic Config ---
# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# --- Model Metadata ---
# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
# For now, we set it to None as we don't have models yet.
# We will update this later when we create the SQLAlchemy models.
from shared.database.base import Base
target_metadata = Base.metadata
# Import all models here so that Alembic's autogenerate can see them.
from models.user import User
from models.request import Request



def get_database_url():
    """Construct the database URL from environment variables."""
    # Load variables from .env file if present
    load_dotenv()

    user = os.getenv("RESPONSE_DB_USER", "user")
    password = os.getenv("RESPONSE_DB_PASSWORD", "password")
    host = os.getenv("RESPONSE_DB_HOST", "127.0.0.1")
    port = os.getenv("RESPONSE_DB_PORT", "5432")
    db_name = os.getenv("RESPONSE_DB_NAME", "response_db")

    # Ensure all parts are available before constructing the URL
    return f"postgresql+psycopg://{user}:{password}@{host}:{port}/{db_name}"


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = get_database_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    # Set the correct database URL in the config object
    config.set_main_option("sqlalchemy.url", get_database_url())

    # Create an engine from the updated config
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()