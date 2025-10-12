from sqlalchemy import Boolean, Column, String, Integer, DateTime
from sqlalchemy.orm import validates

from base import BaseModel


class User(BaseModel):
    __tablename__ = "users"

    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)

    profile_type = Column(String(50), nullable=False, default='basic')
    rate_limit_per_minute = Column(Integer, nullable=False, default=10)
    rate_limit_per_hour = Column(Integer, nullable=False, default=100)
    rate_limit_per_day = Column(Integer, nullable=False, default=500)

    priority = Column(Integer, nullable=False, default=5)
    is_active = Column(Boolean, default=True, index=True)
    last_login = Column(DateTime(timezone=True), nullable=True)

    @validates('profile_type')
    def validate_profile_type(self, key, profile_type):
        allowed_profiles = ['basic', 'premium', 'enterprise', 'admin']
        if profile_type not in allowed_profiles:
            raise ValueError(f"Profile type '{profile_type}' is not valid. Allowed values are: {allowed_profiles}")
        return profile_type

    @validates('priority')
    def validate_priority(self, key, priority):
        if not 1 <= priority <= 10:
            raise ValueError("Priority must be between 1 and 10.")
        return priority