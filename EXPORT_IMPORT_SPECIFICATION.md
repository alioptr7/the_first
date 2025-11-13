# 📊 Export/Import Architecture - Complete Specification

## 🎯 سوال: دقیقا کدوم تنظیمات رو اکسپورت میکنیم؟

---

## ✅ جواب: هر 3 نوع اکسپورت:

### 1️⃣ **Settings Export** (هر 60 ثانیه)
**From:** Response Network → Settings Table
**To:** Request Network → settings JSON file
**Location:** `exports/settings/settings_YYYYMMDD_HHMMSS.json`

#### فیلدهای Export شده:
```json
{
  "settings": [
    {
      "key": "app.name",
      "value": "Response Network",
      "description": "نام اپلیکیشن",
      "is_public": true,
      "created_at": "2025-11-12T10:00:00.000000",
      "updated_at": "2025-11-12T10:00:00.000000"
    },
    {
      "key": "max_concurrent_requests",
      "value": 100,
      "description": "حداکثر درخواست‌های concurrent",
      "is_public": true,
      "created_at": "2025-11-12T10:00:00.000000",
      "updated_at": "2025-11-12T10:00:00.000000"
    }
  ],
  "exported_at": "2025-11-12T10:29:01.475658",
  "version": 1,
  "total_count": 2
}
```

#### کوالیفاسیون:
- ✅ فقط `is_public == true`
- ✅ تمام فیلدها شامل value، description، timestamps
- ✅ JSON format
- ✅ UTF-8 encoding

---

### 2️⃣ **Users Export** (هر 60 ثانیه)
**From:** Response Network → Users Table
**To:** Request Network → users JSON file
**Location:** `exports/users/users_YYYYMMDD_HHMMSS.json`

#### فیلدهای Export شده:
```json
{
  "users": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "username": "john_sales",
      "email": "john@company.com",
      "role": "user",
      "is_active": true,
      "created_at": "2025-11-01T09:00:00.000000",
      "updated_at": "2025-11-12T10:00:00.000000"
    },
    {
      "id": "550e8400-e29b-41d4-a716-446655440001",
      "username": "admin_user",
      "email": "admin@company.com",
      "role": "admin",
      "is_active": true,
      "created_at": "2025-10-01T09:00:00.000000",
      "updated_at": "2025-11-12T10:00:00.000000"
    }
  ],
  "exported_at": "2025-11-12T10:29:01.475658",
  "version": 1,
  "total_count": 2
}
```

#### کوالیفاسیون:
- ✅ تمام users (admin + user)
- ✅ فقط: id, username, email, role, is_active, timestamps
- ✅ JSON format

---

### 3️⃣ **ProfileTypes Export** (هر 60 ثانیه)
**From:** Response Network → ProfileTypeConfig Table
**To:** Request Network → profile_types JSON file
**Location:** `exports/profile_types/profile_types_YYYYMMDD_HHMMSS.json`

#### فیلدهای Export شده:
```json
{
  "profile_types": [
    {
      "name": "sales",
      "display_name": "Sales Team",
      "description": "تیم فروش",
      "allowed_request_types": ["customer_lookup", "transaction_history"],
      "blocked_request_types": [],
      "daily_request_limit": 100,
      "monthly_request_limit": 2000,
      "rate_limit_per_minute": 10,
      "rate_limit_per_hour": 100,
      "is_builtin": false,
      "updated_at": "2025-11-12T10:00:00.000000"
    },
    {
      "name": "admin",
      "display_name": "Administrators",
      "description": "مدیران سیستم",
      "allowed_request_types": [],
      "blocked_request_types": [],
      "daily_request_limit": 10000,
      "monthly_request_limit": 200000,
      "rate_limit_per_minute": 1000,
      "rate_limit_per_hour": 10000,
      "is_builtin": true,
      "updated_at": "2025-11-01T10:00:00.000000"
    }
  ],
  "exported_at": "2025-11-12T10:29:01.475658",
  "version": 1,
  "total_count": 2
}
```

#### کوالیفاسیون:
- ✅ فقط `is_active == true`
- ✅ تمام ProfileTypes با permissions و limits
- ✅ JSON format

---

## 🔄 How It Works:

### Flow 1: Settings
```
Response Network                Request Network
    ↓                                 ↓
[Settings Table]         (هر 60 ثانیه)
- key, value                  ↓
- description          [export_settings_exporter]
- is_public                   ↓
    ↓                    [exports/settings/latest.json]
[Beat Scheduler]              ↓
    ↓                    [Import Task - TODO]
[export_settings...]
```

### Flow 2: Users
```
Response Network                Request Network
    ↓                                 ↓
[Users Table]          (هر 60 ثانیه)
- id, username               ↓
- email, role         [export_users_exporter]
- is_active                  ↓
    ↓                    [exports/users/latest.json]
[Beat Scheduler]             ↓
    ↓                   [Sync to Request Network]
[export_users...]            ↓
                      [User.profile_type assigned]
```

### Flow 3: ProfileTypes
```
Response Network                Request Network
    ↓                                 ↓
[ProfileTypeConfig]  (هر 60 ثانیه)
- name, permissions          ↓
- allowed/blocked      [export_profile_types_exporter]
- limits                      ↓
    ↓                    [exports/profile_types/latest.json]
[Beat Scheduler]             ↓
    ↓                   [Sync to User Model]
[export_profile_types...]     ↓
                      [User inherits permissions]
```

---

## 📝 Examples of What Gets Exported:

### Settings Example:
```json
{
  "key": "api.timeout",
  "value": 30,
  "description": "API request timeout in seconds",
  "is_public": true
}
```

### User Example:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "username": "john_sales",
  "email": "john@company.com",
  "role": "user",
  "is_active": true
}
```

### ProfileType Example:
```json
{
  "name": "sales",
  "allowed_request_types": [
    "customer_lookup",
    "transaction_history",
    "billing_info"
  ],
  "blocked_request_types": [],
  "daily_request_limit": 100,
  "rate_limit_per_minute": 10
}
```

---

## 🚀 Export Task Status:

| Task | Status | فایل | Schedule |
|------|--------|------|----------|
| export_settings_exporter | ✅ Implemented | `workers/tasks/settings_exporter.py` | ✅ in Beat |
| export_users_exporter | ✅ Implemented | `workers/tasks/users_exporter.py` | ✅ in Beat |
| export_profile_types_exporter | ✅ Implemented | `workers/tasks/profile_types_exporter.py` | ✅ in Beat |

---

## 📥 Import Tasks (TODO):

Request Network باید import کند:

| Task | Status | Purpose |
|------|--------|---------|
| import_settings | ❌ TODO | اپلیکیشن settings را apply کند |
| import_users | ❌ TODO | Users را sync کند + ProfileType assign کند |
| import_profile_types | ❌ TODO | ProfileTypes + Permissions را sync کند |

---

## ✅ Testing Checklist:

بعد از شروع Beat و Worker:

- [ ] Settings export در `exports/settings/latest.json` وجود دارد
- [ ] Users export در `exports/users/latest.json` وجود دارد
- [ ] ProfileTypes export در `exports/profile_types/latest.json` وجود دارد
- [ ] هر 60 ثانیه timestamp جدید ایجاد می‌شود
- [ ] JSON files معتبر هستند
- [ ] `latest.json` همیشه آخرین data را دارد

---

## 🎯 اگر همه چیز صحیح کار می‌کند:

✅ Ready برای Docker
✅ Ready برای Import Tasks
✅ Ready برای Request Network sync
