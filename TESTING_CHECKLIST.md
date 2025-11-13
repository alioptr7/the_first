# ✅ System Testing Checklist

## الف. قبل از شروع:

- [ ] Redis running: `redis-cli -p 6380 ping`
- [ ] PostgreSQL running: `psql -U postgres -d response_network`
- [ ] API directory: `cd c:\Users\win\the_first\response-network\api`

---

## ب. شروع Services:

### Terminal 1 - Beat Scheduler
```bash
cd c:\Users\win\the_first\response-network\api
python start_beat.py
```
**Expected Output:**
```
celery beat v5.5.3 (shield)
⏰ Starting Celery Beat Scheduler
[tasks]
  - export-settings-every-minute
  - export-users-every-minute
  - export-profile-types-every-minute
```

### Terminal 2 - Worker
```bash
cd c:\Users\win\the_first\response-network\api
python start_worker.py
```
**Expected Output:**
```
🪟 Windows detected - using --pool=solo
✅ Connected to redis://localhost:6380/0
✅ celery@pc ready
[tasks]
  . workers.tasks.settings_exporter.export_settings_to_request_network
  . workers.tasks.users_exporter.export_users_to_request_network
  . workers.tasks.profile_types_exporter.export_profile_types_to_request_network
```

### Terminal 3 - API Server
```bash
cd c:\Users\win\the_first\response-network\api
python -m uvicorn main:app --reload
```
**Expected Output:**
```
Uvicorn running on http://127.0.0.1:8000
```

---

## ج. منتظر شوید 60 ثانیه:

Beat باید این پیام‌ها بفرستد:
```
[02:22:00] Scheduler: Sending due task export-settings-every-minute
[02:22:00] Scheduler: Sending due task export-users-every-minute
[02:22:00] Scheduler: Sending due task export-profile-types-every-minute
```

Worker باید آن‌ها اجرا کند:
```
[02:22:00] Task export_settings_to_request_network received
[02:22:01] Task export_settings_to_request_network succeeded in 0.45s
[02:22:00] Task export_users_to_request_network received
[02:22:01] Task export_users_to_request_network succeeded in 0.23s
[02:22:00] Task export_profile_types_to_request_network received
[02:22:01] Task export_profile_types_to_request_network succeeded in 0.18s
```

---

## د. تست Exports:

### Option 1: Automated Test
```bash
python test_exports.py
```

Expected Output:
```
============================================================
🧪 Testing Export System
============================================================

1️⃣ Checking Settings Export...
   ✅ Found: exports/settings/latest.json
   📊 Total settings: 2
   📅 Exported at: 2025-11-12T10:29:01.475658

2️⃣ Checking Users Export...
   ✅ Found: exports/users/latest.json
   👥 Total users: 2
   📝 Sample: john_sales (user)

3️⃣ Checking ProfileTypes Export...
   ✅ Found: exports/profile_types/latest.json
   🎯 Total profile types: 2
   📝 Sample: sales (Sales Team)

============================================================
📊 Results Summary:
============================================================
  SETTINGS            ✅ PASS
  USERS               ✅ PASS
  PROFILE_TYPES       ✅ PASS

🎉 All exports working correctly!
============================================================
```

### Option 2: Manual Check
```bash
# Check settings
type response-network\api\exports\settings\latest.json

# Check users
type response-network\api\exports\users\latest.json

# Check profile types
type response-network\api\exports\profile_types\latest.json
```

---

## ه. Troubleshooting:

### Problem: No export files created
**Check:**
1. Beat is running and shows "Sending due task"
   ```bash
   # Check Beat logs for errors
   ```

2. Worker is running and shows "Task succeeded"
   ```bash
   # Check Worker logs for errors
   ```

3. Wait at least 60 seconds after Beat start

### Problem: Files exist but empty
**Check:**
1. Settings with `is_public=true` exist in database
   ```bash
   # In API shell:
   db = get_db()
   settings = db.query(Settings).filter(Settings.is_public==True).all()
   print(len(settings))  # Should be > 0
   ```

2. Users exist in database
   ```bash
   users = db.query(User).all()
   print(len(users))  # Should be > 0
   ```

3. ProfileTypes exist and are active
   ```bash
   profile_types = db.query(ProfileTypeConfig).filter(ProfileTypeConfig.is_active==True).all()
   print(len(profile_types))  # Should be > 0
   ```

### Problem: JSON parse error
**Solution:**
- Delete export files and wait 60 seconds for re-export
- Check that Celery task completed successfully

---

## و. Database Checks:

### Check if data exists:
```python
from models.settings import Settings
from models.user import User
from models.profile_type_config import ProfileTypeConfig
from core.dependencies import get_db_sync

db = next(get_db_sync())

# Settings
settings = db.query(Settings).filter(Settings.is_public==True).all()
print(f"Public Settings: {len(settings)}")

# Users
users = db.query(User).all()
print(f"Users: {len(users)}")

# ProfileTypes
profile_types = db.query(ProfileTypeConfig).filter(ProfileTypeConfig.is_active==True).all()
print(f"Active ProfileTypes: {len(profile_types)}")
```

---

## ز. API Endpoints Check:

### Test Settings Endpoint:
```bash
curl -X GET http://localhost:8000/api/v1/settings \
  -H "Authorization: Bearer ADMIN_TOKEN"
```

### Test Users Endpoint:
```bash
curl -X GET http://localhost:8000/api/v1/users \
  -H "Authorization: Bearer ADMIN_TOKEN"
```

### Test ProfileTypes Endpoint:
```bash
curl -X GET http://localhost:8000/api/v1/profile-types \
  -H "Authorization: Bearer ADMIN_TOKEN"
```

---

## ح. Final Verification:

- [ ] Beat is sending tasks every 60 seconds
- [ ] Worker is executing tasks successfully
- [ ] Settings file has `is_public=true` entries
- [ ] Users file has all users
- [ ] ProfileTypes file has allowed_request_types
- [ ] All JSON files are valid
- [ ] No errors in Beat/Worker logs
- [ ] Timestamps update every 60 seconds

---

## ی. اگر همه چیز OK بود:

✅ Exports working correctly
✅ Ready for Docker deployment
✅ Ready for Import Tasks implementation
✅ Ready for Request Network sync

---

## تنظیمات Sample برای Testing:

### Create sample Settings:
```bash
curl -X POST http://localhost:8000/api/v1/settings \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -d '{
    "key": "app.name",
    "value": "My App",
    "description": "Application name",
    "is_public": true
  }'
```

### Create sample ProfileType:
```bash
curl -X POST http://localhost:8000/api/v1/profile-types \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -d '{
    "name": "sales",
    "display_name": "Sales Team",
    "description": "Sales team profile",
    "permissions": {
      "allowed_request_types": ["customer_lookup"],
      "blocked_request_types": [],
      "max_results_per_request": 1000
    },
    "daily_request_limit": 100
  }'
```

