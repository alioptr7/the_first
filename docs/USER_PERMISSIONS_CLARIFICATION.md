# 🔐 User Permissions Architecture - Clarification

## سوال: ProfileType چه ارتباطی با User Permissions دارد؟

---

## ✅ جواب صحیح (طبق توضیح شما):

```
ProfileType → تعریف کننده دسترسی‌های یک کلاس از کاربران
User → تخصیص یک ProfileType برای هر کاربر
User Permissions → مشخص می‌کند که User چه RequestTypes قابل دسترسی دارد
```

### مثال:

```
ProfileType: "sales"
├─ Daily Limit: 100 requests
├─ Monthly Limit: 2000 requests
├─ Allowed Request Types: [type_A, type_B, type_C]
└─ Blocked Request Types: [type_sensitive]

User: john@company.com
├─ Profile Type: "sales"
├─ Limits: inherited from ProfileType
└─ Allowed Request Types: inherited from ProfileType
```

---

## 📊 الان وضعیت سیستم:

### Response Network (داده‌ها را تعریف می‌کند):

#### 1. ProfileTypeConfig Model ✅
```python
# models/profile_type_config.py
class ProfileTypeConfig:
    name: str = "sales"
    display_name: str = "Sales Team"
    permissions: dict = {}  # TODO: چی باید اینجا باشد؟
    daily_request_limit: int = 100
    monthly_request_limit: int = 2000
    max_results_per_request: int = 1000
    is_active: bool = True
    is_builtin: bool = False
```

**مشکل:** `permissions` خالی است! باید RequestType access تعریف کنیم.

#### 2. User Model ✅
```python
# models/user.py
class User:
    id: UUID
    username: str
    profile_type: str  # "sales"
    # rate limits از ProfileType می‌گیرد
```

#### 3. Export شدن ✅
```python
# workers/tasks/users_exporter.py
# Users به Request Network export می‌شوند
```

---

### Request Network (داده‌ها را مصرف می‌کند):

#### 1. User Model (Replica) ✅
```python
# models/user.py
class User:
    id: UUID
    username: str
    profile_type: str
    rate_limit_per_minute: int
    rate_limit_per_hour: int
    rate_limit_per_day: int
    allowed_indices: list  # ["index_1", "index_2"]  ← مشکل!
```

**مشکل:** `allowed_indices` اسم اشتباه است! باید `allowed_request_types` باشد.

#### 2. Request Create Endpoint ✅
```python
# routers/request_router.py
@router.post("/")
async def submit_request(request_data: RequestCreate, current_user: User):
    # بررسی می‌کند که user در allowed_indices هست
    # اما allowed_indices برای elasticsearch است، نه request types!
```

---

## ❌ مشکلات موجود:

| مشکل | جایگاه | حالت |
|------|--------|------|
| ProfileTypeConfig.permissions خالی | Response | ⚠️ نیاز تعمیر |
| allowed_indices اسم غلط است | Request | ⚠️ نیاز تعمیر |
| نمی‌دانیم RequestTypes چه هستند | Response | ❓ ابهام |
| Export نمی‌کند ProfileType permissions | Response | ⚠️ نیاز اضافه |

---

## 🎯 جواب سوالات:

### 1️⃣ **RequestType چیست؟**

**جواب:** `RequestType` همان `serviceName` است!

**مثال:**
```python
# وقتی user یک request می‌فرستد:
{
    "name": "my_request_1",
    "request": {
        "serviceName": "customer_lookup",  # ← این RequestType است!
        "fieldRequest": {
            "msisdn": "989121234567",
            "fromTime": "2025-01-01",
            "toTime": "2025-01-31"
        }
    }
}
```

**RequestTypes در سیستم:**
- `customer_lookup` - جستجوی اطلاعات مشتری
- `transaction_history` - تاریخ تراکنش‌ها
- `billing_info` - اطلاعات صورتحساب
- `support_tickets` - درخواست‌های پشتیبانی
- و غیره...

**معنی:** هر `serviceName` یک نوع درخواست است که user می‌تواند بفرستد.

---

### 2️⃣ **ProfileType permissions چی باید شامل کند؟**

**جواب شما:** ✅ کاملا صحیح!

```json
{
  "allowed_request_types": ["customer_lookup", "transaction_history"],
  "blocked_request_types": [],
  "max_results_per_request": 1000
}
```

**مثال:**

```python
# ProfileType: "sales"
ProfileTypeConfig(
    name="sales",
    permissions={
        "allowed_request_types": [
            "customer_lookup",
            "transaction_history"
        ],
        "blocked_request_types": [],
        "max_results_per_request": 1000
    },
    daily_request_limit=100,
    monthly_request_limit=2000
)
```

**معنی:**
- Sales team فقط می‌تواند customer_lookup و transaction_history بفرستد
- بقیه request types برایشان blocked است
- حداکثر 1000 نتیجه در هر request

---

### 3️⃣ **آیا User می‌تواند restrictions اضافی داشته باشد؟**

**بله! اما اینطوری:**

```
ProfileType: "sales" 
├─ allowed: [customer_lookup, transaction_history, billing_info]
│
└─ User: john@company.com
   ├─ ProfileType: sales
   └─ Extra restrictions: [billing_info]
      ↓
      نتیجه نهایی: john فقط می‌تواند [customer_lookup, transaction_history] بفرستد
```

**نه اینطوری نه:**
```
ProfileType: allowed = [A, B]
User: allowed = [A]    ❌ اینطوری نیست!
```

**بلکه این‌طوری:**
```
ProfileType: allowed = [A, B, C]
User: blocked = [C]
↓
نتیجه نهایی: [A, B]
```

**مثال واقعی:**

```python
# Database
class User:
    id = "user_123"
    username = "john"
    profile_type = "sales"  # allowed: [customer_lookup, transaction_history, billing_info]
    blocked_request_types = ["billing_info"]  # اضافی!

# نتیجه:
allowed_types = ["customer_lookup", "transaction_history"]
```

**وقتی john یک request می‌فرستد:**
```python
# درخواست از john
{
    "serviceName": "billing_info",  # ❌ نه! john نمی‌تواند
    ...
}

# سیستم:
✗ Access Denied! "billing_info" در blocked_request_types تو است
```

---

### 4️⃣ **Rate Limiting کجا enforce می‌شود؟**

**جواب شما:** ✅ در Request Network وقت submit request!

```
User می‌فرستد: POST /requests/
    ↓
Request Network بررسی می‌کند:
    1. آیا user فعال است؟
    2. آیا request_type در allowed_types است؟
    3. آیا user به rate_limit رسیده؟
    4. آیا user امروز حد روزانه‌اش را رد کرده؟
    ↓
اگر همه چک بشوند: ✅ Request قبول شود
اگر یکی fail شود: ❌ Request رد شود
```

---

## 📊 خلاصه نهایی:

| موضوع | جواب |
|--------|------|
| **RequestType** | `serviceName` در درخواست |
| **Permissions** | allowed_request_types + blocked_request_types |
| **User Extra Restrictions** | User می‌تواند بعضی types رو برای خود block کند |
| **Rate Limiting** | در Request Network، وقت submit |



---

---

## �️ اکنون باید این‌ها را implement کنیم:

### Step 1: ProfileTypeConfig را تعمیر کنیم
```python
# response-network/api/models/profile_type_config.py

class ProfileTypeConfig:
    permissions: dict = {
        "allowed_request_types": ["customer_lookup", "transaction_history"],
        "blocked_request_types": [],
        "max_results_per_request": 1000
    }
```

### Step 2: User Model در Request Network
```python
# request-network/api/models/user.py

class User:
    # FROM ProfileType (inherited):
    profile_type: str  # "sales"
    allowed_request_types: list  # ["customer_lookup", "transaction_history"]
    
    # EXTRA USER-LEVEL RESTRICTIONS:
    blocked_request_types: list  # ["billing_info"]
    
    # RATE LIMITS:
    rate_limit_per_minute: int
    rate_limit_per_hour: int
    rate_limit_per_day: int
```

### Step 3: Export ProfileTypes و Permissions
```python
# response-network/api/workers/tasks/profile_types_exporter.py

# Export هر ProfileType با permissions آن
{
    "name": "sales",
    "allowed_request_types": [...],
    "daily_request_limit": 100,
    "monthly_request_limit": 2000
}
```

### Step 4: در Request Network - Access Check
```python
# request-network/api/routers/request_router.py

async def submit_request(request_data: RequestCreate, current_user: User):
    # 1. Check: user active?
    # 2. Check: serviceName در allowed_request_types?
    # 3. Check: serviceName در blocked_request_types?
    # 4. Check: rate limit exceeded?
    # 5. Create request
```

---

## 📋 اکنون شروع کنیم؟

**بیایید یک TODO list ایجاد کنیم و یک به یک implement کنیم:** 🚀
