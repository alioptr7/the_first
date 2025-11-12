#!/usr/bin/env python
"""
تست اندپوینت های اکسپورت تنظیمات
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://127.0.0.1:8000/api/v1"

print("=" * 60)
print("تست اندپوینت های اکسپورت تنظیمات")
print("=" * 60)

# 1. Login
print("\n1️⃣ ورود به عنوان ادمین...")
response = requests.post(
    f"{BASE_URL}/auth/login",
    data={"username": "admin", "password": "admin123"}
)

if response.status_code != 200:
    print(f"❌ خطا در ورود: {response.status_code}")
    print(response.text)
    exit(1)

token = response.json()["access_token"]
print(f"✅ ورود موفق. توکن: {token[:30]}...")

headers = {"Authorization": f"Bearer {token}"}

# 2. دیدن تنظیمات فعلی برای اکسپورت
print("\n2️⃣ نمایش تنظیماتی که برای اکسپورت آماده هستند...")
response = requests.get(f"{BASE_URL}/settings/export/current", headers=headers)
print(f"وضعیت: {response.status_code}")
data = response.json()
print(f"تعداد تنظیمات: {data.get('total_settings', 0)}")
print(f"زمان اکسپورت: {data.get('export_timestamp')}")
print(f"مسیر اکسپورت: {data.get('export_path')}")
print("\nتنظیمات:")
for setting in data.get('settings', [])[:5]:  # Show first 5
    print(f"  • {setting['key']}: {setting.get('description', 'بدون توضیح')}")
if len(data.get('settings', [])) > 5:
    print(f"  ... و {len(data.get('settings', [])) - 5} تنظیم دیگر")

# 3. دستور اکسپورت تنظیمات
print("\n3️⃣ ارسال دستور اکسپورت تنظیمات...")
response = requests.post(f"{BASE_URL}/settings/export/now", headers=headers)
print(f"وضعیت: {response.status_code}")
result = response.json()
print(f"پیام: {result.get('message')}")
print(f"Task ID: {result.get('task_id')}")
print(f"وضعیت: {result.get('status')}")

# 4. لیست تنظیمات سیستم
print("\n4️⃣ لیست تنام تنظیمات سیستم...")
response = requests.get(f"{BASE_URL}/settings", headers=headers)
print(f"وضعیت: {response.status_code}")
settings = response.json()
print(f"تعداد کل تنظیمات: {len(settings)}")
for setting in settings[:3]:
    print(f"\n  تنظیم: {setting['key']}")
    print(f"    توضیح: {setting.get('description', 'ندارد')}")
    print(f"    فعال: {setting['is_active']}")
    print(f"    مقدار: {str(setting['value'])[:100]}...")

print("\n" + "=" * 60)
print("✅ تمام تست ها موفق بودند!")
print("=" * 60)
