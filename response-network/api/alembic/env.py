"""تنظیمات Alembic"""
import os
import sys
from logging.config import fileConfig

# اضافه کردن پوشه api به sys.path
from os.path import abspath, dirname
api_dir = abspath(dirname(dirname(__file__)))
sys.path.insert(0, api_dir)

# اضافه کردن پوشه response-network به sys.path برای دسترسی به api module
response_network_dir = dirname(api_dir)
sys.path.insert(0, response_network_dir)

# اضافه کردن پوشه shared به sys.path
project_root = dirname(response_network_dir)
sys.path.insert(0, project_root)

from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context

# Import Base از همان جایی که مدل‌ها import می‌شوند
# ابتدا باید api را به عنوان یک ماژول قابل import کنیم
import importlib.util
spec = importlib.util.spec_from_file_location("api", os.path.join(api_dir, "__init__.py"))
if spec and spec.loader:
    api_module = importlib.util.module_from_spec(spec)
    sys.modules["api"] = api_module

# حالا می‌توانیم modules را با prefix api import کنیم
from api.db.base_class import Base
from api import models

# Import کردن همه مدل‌ها برای ثبت در metadata
from api.models import (
    User, Request, IncomingRequest, QueryResult,
    ExportBatch, ImportBatch, ExportableSettings,
    RequestType, Settings, SystemHealth, SystemLog,
    UserRequestAccess
)


# این بخش برای تنظیمات Alembic است
config = context.config

# تنظیم فایل لاگ
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# اضافه کردن MetaData برای مدل‌ها
target_metadata = Base.metadata

from sqlalchemy.engine import URL

def get_url():
    """ساخت URL دیتابیس از متغیرهای محیطی"""
    return URL.create(
        drivername="postgresql+psycopg2",
        username=os.getenv("RESPONSE_DB_USER", "user"),
        password=os.getenv("RESPONSE_DB_PASSWORD", "password"),
        host=os.getenv("RESPONSE_DB_HOST", "localhost"),
        port=int(os.getenv("RESPONSE_DB_PORT", 5433)),
        database=os.getenv("RESPONSE_DB_NAME", "response_db"),
    )

def run_migrations_offline() -> None:
    """اجرای مهاجرت‌ها در حالت آفلاین"""
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """اجرای مهاجرت‌ها در حالت آنلاین"""
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = get_url()
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()