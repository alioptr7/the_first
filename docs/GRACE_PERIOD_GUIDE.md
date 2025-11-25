# Rate Limiting Grace Period - مستندات

**تاریخ**: 2025-11-25  
**نسخه**: 1.0  
**فاز**: 5 (Grace Period Implementation)

---

## 📋 خلاصه

Grace Period یک سیستم **نرم** برای Rate Limiting است که کاربران را هشدار می‌دهد قبل از block کردن:

| سطح | استفاده | وضعیت | فعالیت |
|------|---------|-------|--------|
| **OK** | 0-80% | ✅ عادی | بدون مشکل |
| **WARNING** | 80-100% | ⚠️ هشدار | grace period فعال (5 دقیقه) |
| **SOFT BLOCK** | 100-110% | 🔶 نرم | اجازه دارد اما محدود (5 دقیقه) |
| **HARD BLOCK** | +110% | ❌ مسدود | پاسخ 429 Too Many Requests |

---

## 🎯 مزایا

1. **کاربری بهتر**: کاربران هشدار می‌گیرند قبل از block شدن
2. **بدون تنش**: 5 دقیقه grace period برای خاتمه کار
3. **انعطاف‌پذیری**: Admin می‌تواند محدودیت‌های شخصی تنظیم کند
4. **شفاف**: Response headers نشان می‌دهد چه اتفاقی می‌افتد

---

## 📊 ساختار

### Profiles (Tiers)

```python
{
    "free": {
        "minute": 10,
        "hour": 100,
        "day": 1000,
    },
    "basic": {
        "minute": 30,
        "hour": 500,
        "day": 5000,
    },
    "premium": {
        "minute": 100,
        "hour": 2000,
        "day": 20000,
    },
    "enterprise": {
        "minute": 500,
        "hour": 10000,
        "day": 100000,
    },
}
```

### Thresholds

- **WARNING**: 80% از محدودیت
- **SOFT BLOCK**: +110% (اجازه دارد)
- **HARD BLOCK**: 100% (مسدود)

---

## 🔄 جریان کار

### 1️⃣ کاربر در حد عادی (0-80%)

```
درخواست → بررسی → ✅ OK → پاسخ 200
Headers: X-RateLimit-Remaining-*
```

**Response Headers:**
```
X-RateLimit-Remaining-Minute: 5
X-RateLimit-Remaining-Hour: 25
X-RateLimit-Remaining-Day: 750
X-RateLimit-Status: OK
```

---

### 2️⃣ تقریب به محدودیت (80-100%)

```
درخواست → بررسی → ⚠️ WARNING → grace period فعال (5 دقیقه)
```

**Response:**
```json
{
  "status": 200,
  "message": "Request successful but approaching limit"
}
```

**Response Headers:**
```
X-RateLimit-Status: WARNING
X-RateLimit-Message: Approaching minute limit (80% used)
X-RateLimit-Remaining-Minute: 2
X-RateLimit-Grace-Period-Ends: 2025-11-25T12:35:00Z
```

---

### 3️⃣ در دوره grace (100-110%)

```
درخواست → بررسی → 🔶 SOFT_BLOCK → اجازه (برای 5 دقیقه)
```

**Response:**
```json
{
  "status": 200,
  "message": "Request processed - soft block active (grace period)"
}
```

**Response Headers:**
```
X-RateLimit-Status: SOFT_BLOCK
X-RateLimit-Grace-Period-Ends: 2025-11-25T12:35:00Z
X-RateLimit-Remaining-Minute: -2
```

---

### 4️⃣ Hard block (+110%)

```
درخواست → بررسی → ❌ EXCEEDED → پاسخ 429
```

**Response (429 Too Many Requests):**
```json
{
  "detail": "Rate limit exceeded for minute",
  "retry_after": 60,
  "limit_exceeded": "minute",
  "remaining": {
    "minute": 0,
    "hour": 50,
    "day": 1500
  }
}
```

**Response Headers:**
```
X-RateLimit-Status: EXCEEDED
Retry-After: 60
X-RateLimit-Remaining-Minute: 0
```

---

## 🛠️ Admin Endpoints

### 1. مشاهده آمار Rate Limit کاربر

```bash
GET /admin/rate-limit/user/{user_id}/stats
```

**Response:**
```json
{
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "profile": "basic",
  "limits": {
    "minute": 30,
    "hour": 500,
    "day": 5000
  },
  "usage": {
    "minute": 24,
    "hour": 450,
    "day": 4500
  },
  "percentages": {
    "minute": 80.0,
    "hour": 90.0,
    "day": 90.0
  },
  "reset_at": {
    "minute": "2025-11-25 12:35:00",
    "hour": "2025-11-25 13:00:00",
    "day": "2025-11-26 00:00:00"
  }
}
```

---

### 2. Reset محدودیت کاربر

```bash
POST /admin/rate-limit/user/{user_id}/reset?window=minute
```

**Parameters:**
- `window`: minute, hour, day, all (default: all)

**Response:**
```json
{
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "window": "minute",
  "reset_count": 1,
  "message": "Rate limit reset for minute"
}
```

---

### 3. تنظیم محدودیت‌های Custom

```bash
POST /admin/rate-limit/user/{user_id}/custom-limits?minute=50&hour=1000&day=10000
```

**Parameters:**
- `minute`: محدودیت دقیقه‌ای (اختیاری)
- `hour`: محدودیت ساعتی (اختیاری)
- `day`: محدودیت روزانه (اختیاری)

**Response:**
```json
{
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "custom_limits": {
    "minute": 50,
    "hour": 1000,
    "day": 10000
  }
}
```

---

### 4. دیدن تمام Profiles

```bash
GET /admin/rate-limit/all
```

**Response:**
```json
{
  "limits": {
    "free": {"minute": 10, "hour": 100, "day": 1000},
    "basic": {"minute": 30, "hour": 500, "day": 5000},
    "premium": {"minute": 100, "hour": 2000, "day": 20000},
    "enterprise": {"minute": 500, "hour": 10000, "day": 100000}
  },
  "thresholds": {
    "warning": "80%",
    "soft_block": "110%",
    "hard_block": "100%"
  },
  "grace_period_duration": "5 minutes"
}
```

---

## 💻 مثال Client-Side Integration

### Python

```python
import requests
from datetime import datetime

API_URL = "http://localhost:8000"
USER_ID = "123e4567-e89b-12d3-a456-426614174000"

# درخواست عادی
response = requests.post(
    f"{API_URL}/requests",
    headers={"X-User-ID": USER_ID},
    json={"query_type": "elasticsearch", "query_params": {...}}
)

# بررسی Rate Limit Headers
remaining_min = response.headers.get("X-RateLimit-Remaining-Minute")
remaining_hour = response.headers.get("X-RateLimit-Remaining-Hour")
status = response.headers.get("X-RateLimit-Status")

print(f"Remaining requests (minute): {remaining_min}")
print(f"Rate limit status: {status}")

# در صورت WARNING، هشدار نمایش دهید
if status == "WARNING":
    print("⚠️ You are approaching rate limit!")
    grace_period = response.headers.get("X-RateLimit-Grace-Period-Ends")
    print(f"Grace period ends at: {grace_period}")

# در صورت EXCEEDED
if response.status_code == 429:
    print("❌ Rate limit exceeded!")
    retry_after = response.headers.get("Retry-After")
    print(f"Retry after: {retry_after} seconds")
```

### JavaScript/TypeScript

```typescript
interface RateLimitInfo {
  status: "OK" | "WARNING" | "SOFT_BLOCK" | "EXCEEDED";
  remainingMinute: number;
  remainingHour: number;
  remainingDay: number;
  gracePeriodEnds?: string;
}

async function checkRateLimit(userId: string): Promise<RateLimitInfo> {
  const response = await fetch("/api/requests", {
    method: "GET",
    headers: {
      "X-User-ID": userId,
    },
  });

  return {
    status: response.headers.get("X-RateLimit-Status") as any,
    remainingMinute: parseInt(response.headers.get("X-RateLimit-Remaining-Minute") || "0"),
    remainingHour: parseInt(response.headers.get("X-RateLimit-Remaining-Hour") || "0"),
    remainingDay: parseInt(response.headers.get("X-RateLimit-Remaining-Day") || "0"),
    gracePeriodEnds: response.headers.get("X-RateLimit-Grace-Period-Ends") || undefined,
  };
}

// استفاده
const info = await checkRateLimit(userId);

if (info.status === "WARNING") {
  console.warn("⚠️ Approaching rate limit!");
  console.log(`Grace period ends: ${info.gracePeriodEnds}`);
}

if (info.status === "EXCEEDED") {
  console.error("❌ Rate limit exceeded!");
  alert(`Please retry after ${info.remainingMinute * 60} seconds`);
}
```

---

## 🚀 Best Practices

### برای Developers

1. **بررسی Response Headers**
   ```python
   status = response.headers.get("X-RateLimit-Status")
   if status == "WARNING":
       # اطلاع دهید به کاربر
       # کاری کنید برای کاهش درخواست‌ها
   ```

2. **Exponential Backoff**
   ```python
   import time
   
   retry_after = int(response.headers.get("Retry-After", 60))
   time.sleep(retry_after)
   # retry کنید
   ```

3. **Batch Requests**
   ```python
   # بجای 100 درخواست جداگانه
   # یک batch request بسازید
   batch_response = requests.post(
       f"{API_URL}/requests/batch",
       json=[req1, req2, ..., req100]
   )
   ```

### برای Admins

1. **مانیتورینگ منظم**
   ```bash
   # هر روز یکبار چک کنید
   GET /admin/rate-limit/all
   ```

2. **تنظیم محدودیت‌ها برای VIPs**
   ```bash
   # یک کاربر خاص به VIP تبدیل کنید
   POST /admin/rate-limit/user/{vip_user_id}/custom-limits?minute=1000&hour=10000&day=100000
   ```

3. **Reset در موارد اضطراری**
   ```bash
   # اگر کاربر در وسط کار مهم بود
   POST /admin/rate-limit/user/{user_id}/reset?window=minute
   ```

---

## 📈 مثال سناریو

### سناریو: کاربر Basic Profile

```
تنظیمات: 30 درخواست/دقیقه، 500 درخواست/ساعت

دقیقه 0: 0 درخواست  ✅
دقیقه 0-5: 25 درخواست  ✅ (83% استفاده)
              → ⚠️ WARNING: 80% threshold رسیده
              → Grace period فعال برای 5 دقیقه

دقیقه 5: 28 درخواست  🔶 SOFT_BLOCK
              → 93% استفاده
              → اجازه دارد (در دوره grace)
              → Response 200 + هشدار

دقیقه 10: 35 درخواست  ❌ EXCEEDED
              → 116% استفاده
              → Grace period تمام شد
              → Response 429
              → Retry-After: 60 (ثانیه)
              → منتظر reset دقیقه بعدی
```

---

## 🔧 Configuration

تمام تنظیمات در `RateLimitConfig` class قابل تغییر هستند:

```python
class RateLimitConfig:
    LIMITS = {...}
    WARNING_THRESHOLD = 0.80  # ⚠️
    SOFT_BLOCK_THRESHOLD = 1.10  # 🔶
    HARD_BLOCK_THRESHOLD = 1.0  # ❌
```

---

## 📝 Logging

تمام events لاگ می‌شوند:

```
WARNING: User 123 reached minute warning threshold
WARNING: User 123 in soft block grace period for hour
WARNING: User 123 exceeded rate limit for day
INFO: Rate limit reset for user 456: minute
```

---

## 🐛 Troubleshooting

### مشکل: درخواست block می‌شود بدون warning

**راه‌حل**: بررسی کنید که Redis متصل است
```bash
curl http://localhost:6379
```

### مشکل: Grace period کار نمی‌کند

**راه‌حل**: بررسی کنید که Redis TTL صحیح تنظیم شده است
```python
redis_client.ttl("rate_limit:soft_block:user_id:minute")
# باید بین 1-300 ثانیه باشد
```

### مشکل: Custom limits درست اعمال نمی‌شود

**راه‌حل**: بررسی کنید که user_id و profile صحیح هستند
```bash
GET /admin/rate-limit/user/{user_id}/stats
```

---

## 📊 Metrics برای Monitoring

معیارهایی که می‌توان ردیابی کرد:

- تعداد WARNING events برای هر کاربر
- تعداد SOFT_BLOCK events
- تعداد EXCEEDED events
- میانگین grace period duration
- Top users by rate limit usage

---

## 🔒 Security Notes

1. **Rate limit headers خود-شناختی هستند** - برای transparency
2. **Custom limits فقط توسط admin قابل تنظیم** - محفوظ
3. **Redis connection امن است** - محفوظ
4. **Grace period خودکار expire می‌شود** - secure

---

## 📞 Support

برای سوالات:
1. بررسی کنید که Redis متصل است
2. بررسی کنید admin endpoints
3. لاگ‌های server را ببینید

---

**نسخه**: 1.0  
**آخرین به‌روزرسانی**: 2025-11-25
