"""تنظیمات پیش‌فرض برای صادرات"""
from uuid import uuid4

DEFAULT_EXPORT_SETTINGS = [
    {
        "id": str(uuid4()),
        "setting_key": "user.allowed_indices",
        "description": "ایندکس‌های مجاز برای کاربر",
        "is_exportable": True,
        "category": "access",
        "requires_encryption": False,
    },
    {
        "id": str(uuid4()),
        "setting_key": "user.daily_request_limit",
        "description": "محدودیت تعداد درخواست روزانه",
        "is_exportable": True,
        "category": "limits",
        "requires_encryption": False,
    },
    {
        "id": str(uuid4()),
        "setting_key": "user.monthly_request_limit",
        "description": "محدودیت تعداد درخواست ماهانه",
        "is_exportable": True,
        "category": "limits",
        "requires_encryption": False,
    },
    {
        "id": str(uuid4()),
        "setting_key": "user.max_results_per_request",
        "description": "محدودیت تعداد نتایج در هر درخواست",
        "is_exportable": True,
        "category": "limits",
        "requires_encryption": False,
    },
    {
        "id": str(uuid4()),
        "setting_key": "user.username",
        "description": "نام کاربری",
        "is_exportable": True,
        "category": "profile",
        "requires_encryption": False,
    },
    {
        "id": str(uuid4()),
        "setting_key": "user.email",
        "description": "ایمیل کاربر",
        "is_exportable": True,
        "category": "profile",
        "requires_encryption": False,
    },
    {
        "id": str(uuid4()),
        "setting_key": "user.password",
        "description": "رمز عبور کاربر",
        "is_exportable": False,  # رمز عبور هرگز صادر نمی‌شود
        "category": "security",
        "requires_encryption": True,
    },
    {
        "id": str(uuid4()),
        "setting_key": "user.is_admin",
        "description": "دسترسی ادمین",
        "is_exportable": False,  # وضعیت ادمین هرگز صادر نمی‌شود
        "category": "security",
        "requires_encryption": False,
    },
]