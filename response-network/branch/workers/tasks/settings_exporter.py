"""صادرکننده تنظیمات از شبکه پاسخ به شبکه درخواست"""
import json
from datetime import datetime
from typing import Dict, Any, List
import httpx

from workers.celery_app import celery_app
from workers.database import get_db_session
from workers.config import settings
from shared.models import User, UserRequestAccess, RequestType, ExportableSettings

def get_exportable_settings(db) -> Dict[str, Any]:
    """دریافت تنظیمات قابل صادرات"""
    settings = db.query(ExportableSettings).filter(
        ExportableSettings.is_exportable == True
    ).all()
    return {s.setting_key: s for s in settings}

def calculate_settings_hash(user: User, access_rules: List[UserRequestAccess], exportable_settings: Dict[str, Any]) -> Dict[str, Any]:
    """محاسبه هش تنظیمات برای تشخیص تغییرات"""
    settings_data = {"user": {}}
    
    # فقط تنظیمات قابل صادرات را اضافه می‌کنیم
    for key, setting in exportable_settings.items():
        if key.startswith("user."):
            attr_name = key.split(".", 1)[1]
            if hasattr(user, attr_name):
                settings_data["user"][attr_name] = getattr(user, attr_name)
    
    # اضافه کردن دسترسی‌های کاربر
    settings_data["access_rules"] = [
        {
            "request_type_id": str(access.request_type_id),
            "allowed_indices": access.allowed_indices,
            "rate_limit": access.rate_limit,
            "daily_limit": access.daily_limit
        }
        for access in access_rules
    ]
    
    return settings_data

@celery_app.task(name="export_settings_to_request_network")
def export_settings_to_request_network(force_export: bool = False) -> Dict[str, Any]:
    """صادرات تنظیمات کاربران و دسترسی‌ها به شبکه درخواست"""
    exported_count = 0
    skipped_count = 0
    failed_count = 0
    
    with get_db_session() as db:
        try:
            # دریافت تنظیمات قابل صادرات
            exportable_settings = get_exportable_settings(db)
            
            # دریافت همه کاربران فعال
            users = db.query(User).filter(User.is_active == True).all()
            
            for user in users:
                try:
                    # دریافت دسترسی‌های کاربر به انواع درخواست
                    access_rules = db.query(UserRequestAccess).filter(
                        UserRequestAccess.user_id == user.id,
                        UserRequestAccess.is_active == True
                    ).all()
                    
                    # محاسبه هش جدید تنظیمات
                    new_settings_hash = calculate_settings_hash(user, access_rules, exportable_settings)
                    
                    # بررسی نیاز به صادرات
                    if not force_export and user.settings_hash == new_settings_hash:
                        skipped_count += 1
                        continue
                    
                    # تبدیل دسترسی‌ها به فرمت مناسب برای صادرات
                    access_data = []
                    for access in access_rules:
                        request_type = db.query(RequestType).filter(RequestType.id == access.request_type_id).first()
                        if request_type:
                            access_data.append({
                                "request_type_name": request_type.name,
                                "allowed_indices": access.allowed_indices,
                                "rate_limit": access.rate_limit,
                                "daily_limit": access.daily_limit
                            })
                    
                    # ساخت داده‌های کاربر برای صادرات (فقط موارد مجاز)
                    user_data = {
                        "user_id": str(user.id),
                        "username": user.username,
                        "email": user.email,
                        "updated_at": datetime.utcnow().isoformat(),
                        "access_rules": access_data
                    }
                    
                    # اضافه کردن فیلدهای مجاز کاربر
                    for key, setting in exportable_settings.items():
                        if key.startswith("user."):
                            attr_name = key.split(".", 1)[1]
                            if hasattr(user, attr_name):
                                user_data[attr_name] = getattr(user, attr_name)
                    
                    # ارسال داده‌ها به شبکه درخواست
                    response = httpx.post(
                        f"{settings.REQUEST_NETWORK_API_URL}/api/v1/settings/import",
                        json=user_data,
                        headers={"Authorization": f"Bearer {settings.REQUEST_NETWORK_API_KEY}"}
                    )
                    
                    if response.status_code == 200:
                        # به‌روزرسانی هش و زمان آخرین صادرات
                        user.settings_hash = new_settings_hash
                        user.last_exported_at = datetime.utcnow()
                        db.commit()
                        exported_count += 1
                    else:
                        failed_count += 1
                        
                except Exception as e:
                    failed_count += 1
                    print(f"خطا در صادرات تنظیمات کاربر {user.id}: {str(e)}")
                    
        except Exception as e:
            return {
                "error": str(e),
                "exported_count": exported_count,
                "skipped_count": skipped_count,
                "failed_count": failed_count,
                "timestamp": datetime.utcnow().isoformat()
            }
    
    return {
        "exported_count": exported_count,
        "skipped_count": skipped_count,
        "failed_count": failed_count,
        "timestamp": datetime.utcnow().isoformat()
    }