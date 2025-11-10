# تنظیمات و راه‌اندازی ورکرها

این مستند نحوه راه‌اندازی و پیکربندی ورکرها در هر دو شبکه را توضیح می‌دهد.

## معماری تنظیمات

تمام تنظیمات ورکرها در شبکه پاسخ مدیریت می‌شوند و از طریق مکانیزم انتقال تنظیمات به شبکه درخواست منتقل می‌شوند. این شامل:

1. تنظیمات ورکرهای شبکه پاسخ:
   - export_settings
   - export_results
   - system_monitoring

2. تنظیمات ورکرهای شبکه درخواست:
   - import_settings
   - export_requests
   - import_results

## ساختار فایل‌ها

```
shared/
├── config/
│   └── base_worker_settings.py     # تنظیمات پایه برای راه‌اندازی اولیه
├── models/
│   └── worker_settings.py          # مدل مشترک تنظیمات ورکرها
└── ...

response-network/
├── api/
│   ├── setup/
│   │   └── setup_worker_settings.py  # اسکریپت راه‌اندازی اولیه
│   └── ...
└── exports/
    └── settings/                     # محل ذخیره تنظیمات برای انتقال

request-network/
├── api/
│   ├── setup/
│   │   └── setup_worker_settings.py  # اسکریپت راه‌اندازی اولیه
│   └── ...
└── imports/
    └── settings/                     # محل دریافت تنظیمات از شبکه پاسخ
```

## مراحل راه‌اندازی

### 1. شبکه پاسخ

1. ساخت دایرکتوری‌های مورد نیاز:
   ```powershell
   mkdir -Force response-network/exports/settings
   ```

2. راه‌اندازی تنظیمات پایه:
   ```bash
   cd response-network/api
   python setup/setup_worker_settings.py
   ```
   این اسکریپت:
   - تنظیمات پایه export_settings را در دیتابیس ثبت می‌کند
   - دایرکتوری‌های لازم را می‌سازد

3. تنظیم بقیه ورکرها از طریق API:
   ```http
   POST /api/v1/worker-settings
   {
     "worker_type": "export_results",
     "storage_type": "s3",
     "storage_path": "/exports/results",
     "storage_config": {
       "bucket": "results-bucket",
       "region": "us-east-1"
     },
     "schedule_expression": "*/15 * * * *",
     "description": "Export results to S3"
   }
   ```

### 2. شبکه درخواست

1. ساخت دایرکتوری‌های مورد نیاز:
   ```powershell
   mkdir -Force request-network/imports/settings
   ```

2. راه‌اندازی تنظیمات پایه:
   ```bash
   cd request-network/api
   python setup/setup_worker_settings.py
   ```
   این اسکریپت:
   - فایل تنظیمات پایه import_settings را ایجاد می‌کند
   - دایرکتوری‌های لازم را می‌سازد

## جزئیات تنظیمات

### انواع Storage

1. Local:
   ```json
   {
     "storage_type": "local",
     "storage_path": "/path/to/files",
     "storage_config": {
       "create_dirs": true
     }
   }
   ```

2. FTP:
   ```json
   {
     "storage_type": "ftp",
     "storage_path": "/remote/path",
     "storage_config": {
       "host": "ftp.example.com",
       "port": 21,
       "username": "user",
       "password": "pass",
       "passive_mode": true
     }
   }
   ```

3. S3:
   ```json
   {
     "storage_type": "s3",
     "storage_path": "path/in/bucket",
     "storage_config": {
       "bucket": "my-bucket",
       "aws_access_key_id": "key",
       "aws_secret_access_key": "secret",
       "region": "us-east-1"
     }
   }
   ```

## مدیریت تنظیمات

### API Endpoints

1. لیست تنظیمات:
   ```http
   GET /api/v1/worker-settings
   ```

2. دریافت تنظیمات یک ورکر:
   ```http
   GET /api/v1/worker-settings/{worker_id}
   ```

3. ایجاد تنظیمات جدید:
   ```http
   POST /api/v1/worker-settings
   ```

4. به‌روزرسانی تنظیمات:
   ```http
   PUT /api/v1/worker-settings/{worker_id}
   ```

5. فعال/غیرفعال کردن ورکر:
   ```http
   POST /api/v1/worker-settings/{worker_id}/toggle
   ```

6. تست اتصال storage:
   ```http
   POST /api/v1/worker-settings/{worker_id}/test-connection
   ```

## نکات مهم

1. **راه‌اندازی اولیه**: تنظیمات پایه فقط شامل `export_settings` در شبکه پاسخ و `import_settings` در شبکه درخواست است تا مشکل مرغ-و-تخم-مرغ حل شود.

2. **انتقال تنظیمات**: 
   - ورکر `export_settings` در شبکه پاسخ تنظیمات را صادر می‌کند
   - ورکر `import_settings` در شبکه درخواست تنظیمات را دریافت می‌کند

3. **امنیت**: 
   - تنظیمات حساس مانند رمزهای عبور باید به صورت رمزنگاری شده ذخیره شوند
   - دسترسی به API تنظیمات فقط برای کاربران admin مجاز است

4. **پشتیبان‌گیری**:
   - از تنظیمات در شبکه پاسخ به طور منظم پشتیبان‌گیری شود
   - فایل‌های انتقال تنظیمات آرشیو شوند