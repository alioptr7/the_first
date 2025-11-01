# تست‌های شبکه درخواست

این مستندات نحوه اجرای تست‌های شبکه درخواست را توضیح می‌دهد.

## پیش‌نیازها

1. پایتون 3.8 یا بالاتر
2. محیط مجازی پایتون
3. PostgreSQL
4. دسترسی به دیتابیس تست

## نصب وابستگی‌ها

```bash
# فعال‌سازی محیط مجازی
.\.venv\Scripts\Activate.ps1

# نصب وابستگی‌های تست
pip install -r requirements-test.txt
```

## تنظیمات محیط تست

1. یک فایل `.env.test` در مسیر اصلی پروژه ایجاد کنید:

```env
TEST_DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/request_network_test
```

2. اطمینان حاصل کنید که دیتابیس تست وجود دارد:

```sql
CREATE DATABASE request_network_test;
```

## اجرای تست‌ها

برای اجرای تمام تست‌ها:

```bash
# با استفاده از اسکریپت
.\scripts\run_tests.ps1

# یا مستقیماً با pytest
pytest tests/ -v --cov=api --cov-report=term-missing
```

برای اجرای یک فایل تست خاص:

```bash
pytest tests/api/test_admin_routes.py -v
```

برای اجرای یک تست خاص:

```bash
pytest tests/api/test_admin_routes.py::test_get_request_stats -v
```

## گزارش پوشش کد

گزارش پوشش کد به صورت خودکار در هنگام اجرای تست‌ها تولید می‌شود. برای تولید گزارش HTML:

```bash
pytest tests/ --cov=api --cov-report=html
```

گزارش در پوشه `htmlcov` قابل مشاهده خواهد بود.

## ساختار تست‌ها

```
tests/
├── conftest.py           # فیکسچرهای مشترک
├── api/                  # تست‌های API
│   ├── test_admin_routes.py
│   └── test_monitoring_routes.py
└── README.md            # این فایل
```

## نکات مهم

1. تست‌ها از یک دیتابیس جداگانه استفاده می‌کنند
2. قبل از هر تست، جداول به صورت خودکار ایجاد می‌شوند
3. بعد از هر تست، تغییرات rollback می‌شوند
4. برای هر تست یک نشست دیتابیس جدید ایجاد می‌شود