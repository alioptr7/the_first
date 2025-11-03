"""Import all SQLAlchemy models here for Alembic to detect"""
from api.db.base_class import Base  # noqa
from api.db.models.user import User  # noqa
from api.models.task_logs import TaskLog  # noqa