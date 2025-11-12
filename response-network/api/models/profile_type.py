"""
Profile types for users in the system.
Defines different user roles and their permissions.
"""

from enum import Enum


class ProfileType(str, Enum):
    """Enumeration of user profile types"""
    ADMIN = "admin"
    USER = "user"
    VIEWER = "viewer"
    BASIC = "basic"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"

    @classmethod
    def get_all(cls):
        """Get all available profile types"""
        return [item.value for item in cls]

    @classmethod
    def is_valid(cls, value: str) -> bool:
        """Check if a value is a valid profile type"""
        return value in cls.get_all()
