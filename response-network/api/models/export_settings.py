"""تنظیمات قابل صادرات به شبکه درخواست"""
from sqlalchemy import Column, String, Boolean, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from shared.database.base import Base


class ExportableSettings(Base):
    """تنظیمات قابل صادرات به شبکه درخواست"""
    __tablename__ = "exportable_settings"

    id = Column(UUID, primary_key=True)
    setting_key = Column(String, unique=True, nullable=False)
    description = Column(String)
    is_exportable = Column(Boolean, default=False)
    transform_function = Column(String, nullable=True)  # نام تابع برای تبدیل داده قبل از صادرات
    
    # برای گروه‌بندی تنظیمات
    category = Column(String, nullable=False, default="general")  # مثلاً: security, limits, access, etc.

    # برای تنظیمات حساس که نیاز به رمزنگاری دارند
    requires_encryption = Column(Boolean, default=False)
    encryption_key_name = Column(String, nullable=True)  # کلید رمزنگاری در vault

    # تنظیمات اضافی برای صادرات
    export_config = Column(JSON, nullable=True)  # مثلاً: {"format": "string", "validation": "email"}