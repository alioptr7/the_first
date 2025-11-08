from typing import Any
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    """
    Base class for all database models.
    Provides common functionality and naming conventions.
    """
    
    @declared_attr
    def __tablename__(cls) -> str:
        """
        Generate __tablename__ automatically from class name.
        Converts CamelCase to snake_case.
        """
        # Convert camel case to snake case
        name = cls.__name__
        return ''.join(['_' + c.lower() if c.isupper() else c for c in name]).lstrip('_')