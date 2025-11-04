"""تنظیمات Alembic"""
import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# اضافه کردن مسیر پروژه به PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

# این بخش بعد از اضافه کردن مسیر پروژه به PYTHONPATH باید باشد
from shared.models import Base
from models.incoming_request import IncomingRequest
from models.request_type import RequestType

# این بخش برای تنظیمات Alembic است
config = context.config

# تنظیم فایل لاگ
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# اضافه کردن MetaData برای مدل‌ها
target_metadata = Base.metadata

def get_url():
    """ساخت URL دیتابیس از متغیرهای محیطی"""
    user = os.getenv("RESPONSE_DB_USER", "user")
    password = os.getenv("RESPONSE_DB_PASSWORD", "password")
    host = os.getenv("RESPONSE_DB_HOST", "localhost")
    port = os.getenv("RESPONSE_DB_PORT", "5433")
    db = os.getenv("RESPONSE_DB_NAME", "response_db")
    return f"postgresql://{user}:{password}@{host}:{port}/{db}"

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