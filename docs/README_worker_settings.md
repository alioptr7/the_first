# راه‌اندازی و پیکربندی ورکرها

این سند نحوه راه‌اندازی و پیکربندی ورکرها در شبکه‌های پاسخ و درخواست را توضیح می‌دهد.

## پیش‌نیازها

- پایگاه داده PostgreSQL راه‌اندازی شده باشد
- متغیرهای محیطی زیر تنظیم شده باشند:
  ```env
  # شبکه پاسخ
  RESPONSE_DB_URL=postgresql://user:pass@localhost:5432/response_db
  RESPONSE_EXPORT_PATH=/path/to/exports

  # شبکه درخواست
  REQUEST_DB_URL=postgresql://user:pass@localhost:5432/request_db
  REQUEST_IMPORT_PATH=/path/to/imports
  ```

## مراحل راه‌اندازی

### 1. آماده‌سازی پایگاه داده

```bash
# در شبکه پاسخ
cd response-network/api
alembic current  # چک کردن وضعیت فعلی
alembic heads    # مشاهده آخرین ورژن‌ها

# اگر جداول ورژن مشکل داشتند:
psql -d response_db -c "DROP TABLE IF EXISTS alembic_version;"
rm -rf alembic/versions/*
alembic revision --autogenerate -m "initial migration"
alembic upgrade head

# چک کردن وضعیت نهایی
alembic current
```

### 2. اجرای اسکریپت‌های راه‌اندازی

```bash
# راه‌اندازی تنظیمات پایه در شبکه پاسخ
cd response-network/api
python setup/setup_worker_settings.py

# راه‌اندازی تنظیمات پایه در شبکه درخواست
cd request-network/api
python setup/setup_worker_settings.py
```

### 3. تأیید راه‌اندازی

بعد از اجرای مراحل بالا، موارد زیر را چک کنید:

1. در شبکه پاسخ:
   - جدول `worker_settings` ایجاد شده باشد
   - تنظیمات پایه `export_settings` در دیتابیس ثبت شده باشد
   - دایرکتوری `exports/settings` ایجاد شده باشد

2. در شبکه درخواست:
   - فایل `config/worker_settings.json` ایجاد شده باشد
   - دایرکتوری `imports/settings` ایجاد شده باشد

## عیب‌یابی

### مشکلات رایج

1. خطای دسترسی به دایرکتوری:
   ```
   mkdir: cannot create directory: Permission denied
   ```
   راه‌حل: اطمینان از دسترسی کاربر به مسیرهای export/import

2. خطای اتصال به دیتابیس:
   ```
   sqlalchemy.exc.OperationalError: connection refused
   ```
   راه‌حل: چک کردن متغیرهای محیطی و دسترسی به دیتابیس

3. مشکلات مایگریشن:
   - اگر جدول `alembic_version` مشکل داشت، طبق مراحل بخش 1 از ابتدا مایگریشن بسازید
   - هرگز مایگریشن دستی نسازید، همیشه از `--autogenerate` استفاده کنید

## ساختار فایل‌ها

```
shared/
├── config/
│   └── base_worker_settings.py  # تنظیمات پایه مشترک
└── models/
    └── worker_settings.py       # مدل مشترک تنظیمات

response-network/
├── api/
│   ├── router/
│   │   └── worker_settings.py   # API مدیریت تنظیمات
│   └── setup/
│       └── setup_worker_settings.py  # اسکریپت راه‌اندازی
└── exports/
    └── settings/               # محل ذخیره تنظیمات صادر شده

request-network/
├── api/
│   └── setup/
│       └── setup_worker_settings.py  # اسکریپت راه‌اندازی
├── config/
│   └── worker_settings.json    # تنظیمات پایه شبکه درخواست
└── imports/
    └── settings/               # محل دریافت تنظیمات
```

## انواع ذخیره‌سازی

سیستم از چند نوع ذخیره‌سازی پشتیبانی می‌کند:

### ذخیره‌سازی محلی (Local Storage)
برای ذخیره فایل‌ها در سیستم فایل محلی:
```json
{
    "base_path": "/path/to/storage"
}
```

### ذخیره‌سازی FTP
برای ذخیره فایل‌ها روی سرور FTP:
```json
{
    "host": "ftp.example.com",
    "port": 21,
    "username": "user",
    "password": "pass",
    "base_path": "/remote/path",
    "use_tls": false
}
```

### ذخیره‌سازی S3
برای ذخیره فایل‌ها در Amazon S3 یا سرویس‌های سازگار:
```json
{
    "bucket_name": "my-bucket",
    "base_path": "path/prefix",
    "aws_access_key_id": "KEY",
    "aws_secret_access_key": "SECRET",
    "region_name": "us-east-1",
    "endpoint_url": "https://custom-s3.example.com"  // اختیاری، برای سرویس‌های سازگار با S3
}
```

## تست اتصال به ذخیره‌ساز

می‌توانید با استفاده از API اتصال به ذخیره‌ساز را تست کنید:

### 1. تست تنظیمات جدید
```http
POST /worker-settings/test-connection
Content-Type: application/json

{
    "worker_type": "EXPORT_SETTINGS",
    "storage_type": "S3",
    "storage_settings": {
        "bucket_name": "test-bucket",
        "aws_access_key_id": "KEY",
        "aws_secret_access_key": "SECRET"
    }
}
```

پاسخ موفق:
```json
{
    "success": true,
    "message": "Connection successful"
}
```

### 2. تست تنظیمات موجود
```http
GET /worker-settings/{settings_id}/test
```

## نکات مهم

1. تنظیمات همه ورکرها در شبکه پاسخ مدیریت می‌شوند
2. شبکه درخواست فقط از تنظیمات دریافتی استفاده می‌کند
3. برای تغییر تنظیمات، همیشه از API شبکه پاسخ استفاده کنید
4. تنظیمات به صورت خودکار توسط `export_settings` به شبکه درخواست منتقل می‌شوند
5. برای حفظ امنیت، رمزهای عبور و کلیدهای دسترسی را در متغیرهای محیطی ذخیره کنید
6. همیشه قبل از ذخیره تنظیمات جدید، اتصال را تست کنید