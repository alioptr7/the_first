"""
مثال عملی: تغییرات در جدول Users
نمایش اینکه چگونه Alembic از داده‌های قبلی محافظت می‌کند
"""

# ============================================================================
# مثال 1: اضافه کردن ستون (ایمن) ✅
# ============================================================================

# migration_001_add_phone_to_users.py
from alembic import op
import sqlalchemy as sa

def upgrade():
    """اضافه کردن phone field"""
    op.add_column('users', sa.Column('phone', sa.String(20), nullable=True))

def downgrade():
    """حذف phone field"""
    op.drop_column('users', 'phone')

"""
مثال دیتا:

قبل:
┌────┬──────────┬─────────────────┐
│ id │ username │ email           │
├────┼──────────┼─────────────────┤
│ 1  │ "admin"  │ "admin@ex.com"  │
│ 2  │ "user1"  │ "user1@ex.com"  │
└────┴──────────┴─────────────────┘

بعد (migration):
┌────┬──────────┬─────────────────┬────────┐
│ id │ username │ email           │ phone  │
├────┼──────────┼─────────────────┼────────┤
│ 1  │ "admin"  │ "admin@ex.com"  │ NULL   │
│ 2  │ "user1"  │ "user1@ex.com"  │ NULL   │
└────┴──────────┴─────────────────┴────────┘

✅ داده‌های قبلی محفوظ!
✅ nullable=True بنابراین خطا نی‌ست!
"""

# ============================================================================
# مثال 2: اضافه کردن NOT NULL field (نیاز به data migration) ⚠️
# ============================================================================

# migration_002_add_required_age.py

def upgrade():
    """
    NOT NULL field اضافه کردن - درست
    """
    # مرحله 1: field را nullable اضافه کنید
    op.add_column('users', sa.Column('age', sa.Integer, nullable=True))
    
    # مرحله 2: مقادیر پیش‌فرض تنظیم کنید
    connection = op.get_bind()
    connection.execute(sa.text("UPDATE users SET age = 18 WHERE age IS NULL"))
    
    # مرحله 3: الآن NOT NULL کنید
    op.alter_column('users', 'age', nullable=False)

def downgrade():
    """حذف age field"""
    op.drop_column('users', 'age')

"""
مثال دیتا:

مرحله 1 (بعد از ADD COLUMN):
┌────┬──────────┬─────────────────┬────────┐
│ id │ username │ email           │ age    │
├────┼──────────┼─────────────────┼────────┤
│ 1  │ "admin"  │ "admin@ex.com"  │ NULL   │
│ 2  │ "user1"  │ "user1@ex.com"  │ NULL   │
└────┴──────────┴─────────────────┴────────┘

مرحله 2 (بعد از UPDATE):
┌────┬──────────┬─────────────────┬────────┐
│ id │ username │ email           │ age    │
├────┼──────────┼─────────────────┼────────┤
│ 1  │ "admin"  │ "admin@ex.com"  │ 18     │
│ 2  │ "user1"  │ "user1@ex.com"  │ 18     │
└────┴──────────┴─────────────────┴────────┘

مرحله 3 (بعد از ALTER COLUMN):
✅ age NOT NULL (الآن محدودیت اعمال می‌شود)
✅ تمام داده‌ها معتبر هستند!
"""

# ============================================================================
# مثال 3: Rename field (نیاز به دقت) ⚠️
# ============================================================================

# migration_003_rename_phone_to_mobile.py

def upgrade():
    """phone → mobile"""
    op.alter_column('users', 'phone', new_column_name='mobile')

def downgrade():
    """mobile → phone"""
    op.alter_column('users', 'mobile', new_column_name='phone')

"""
مثال دیتا:

قبل:
┌────┬────────┐
│ id │ phone  │
├────┼────────┤
│ 1  │ "0911" │
│ 2  │ "0912" │
└────┴────────┘

بعد (migration):
┌────┬────────┐
│ id │ mobile │
├────┼────────┤
│ 1  │ "0911" │
│ 2  │ "0912" │
└────┴────────┘

⚠️ اهتمام: اگر کد کامل `user.phone` را استفاده می‌کند:
   AttributeError: User has no attribute 'phone'
   
   ✅ حل: کد را هم تغییر دهید!
"""

# ============================================================================
# مثال 4: Drop field (خطرناک!) ❌
# ============================================================================

# migration_004_remove_old_field.py

def upgrade():
    """حذف old_data field"""
    op.drop_column('users', 'old_data')

def downgrade():
    """دوباره old_data اضافه کنید"""
    op.add_column('users', sa.Column('old_data', sa.String(255), nullable=True))

"""
مثال دیتا:

قبل:
┌────┬──────────┬────────────┐
│ id │ username │ old_data   │
├────┼──────────┼────────────┤
│ 1  │ "admin"  │ "value123" │
│ 2  │ "user1"  │ "value456" │
└────┴──────────┴────────────┘

بعد (migration):
┌────┬──────────┐
│ id │ username │
├────┼──────────┤
│ 1  │ "admin"  │
│ 2  │ "user1"  │
└────┴──────────┘

❌ "value123" و "value456" برای همیشه حذف شدند!
❌ downgrade می‌تواند فقط ستون را دوباره ایجاد کند، نه داده!

عبرت: تا جایی که ممکن است از DROP کنید!
"""

# ============================================================================
# مثال 5: تغییر Data Type (خطرناک!) ❌
# ============================================================================

# migration_005_change_email_length.py

def upgrade():
    """VARCHAR(255) → VARCHAR(100)"""
    op.alter_column('users', 'email',
                    existing_type=sa.String(255),
                    type_=sa.String(100))

def downgrade():
    """VARCHAR(100) → VARCHAR(255)"""
    op.alter_column('users', 'email',
                    existing_type=sa.String(100),
                    type_=sa.String(255))

"""
مثال دیتا:

قبل:
┌────┬──────────────────────────────────────────┐
│ id │ email                                    │
├────┼──────────────────────────────────────────┤
│ 1  │ "very.long.email.address@subdomain...   │
│    │  company.co.uk" (150 chars)              │
│ 2  │ "short@ex.com" (12 chars)                │
└────┴──────────────────────────────────────────┘

بعد (migration):
┌────┬────────────────────────────┐
│ id │ email                      │
├────┼────────────────────────────┤
│ 1  │ "very.long.email.address@s │ ← TRUNCATED! ❌
│    │  udomain.compan..." (100)  │
│ 2  │ "short@ex.com"             │
└────┴────────────────────────────┘

❌ داده اول حذف شد!
❌ الان invalid email در database است!

عبرت: تغییر type به احتیاط!
"""

# ============================================================================
# مثال 6: صحیح ✅ - Complex Migration
# ============================================================================

# migration_006_restructure_users.py

def upgrade():
    """
    1. email_confirmed field اضافه کنید
    2. داده‌ها را migrate کنید
    3. محدودیت‌ها اضافه کنید
    """
    # مرحله 1: field اضافه کنید
    op.add_column('users', sa.Column('email_confirmed', sa.Boolean, nullable=True))
    
    # مرحله 2: داده‌ها را migrate کنید (پایه: email_verified داشتند)
    connection = op.get_bind()
    connection.execute(sa.text("""
        UPDATE users 
        SET email_confirmed = CASE 
            WHEN email_verified = true THEN true 
            ELSE false 
        END
    """))
    
    # مرحله 3: محدودیت اضافه کنید
    op.alter_column('users', 'email_confirmed', nullable=False)

def downgrade():
    """rollback"""
    op.drop_column('users', 'email_confirmed')

"""
نتیجه:
✅ داده‌ها محفوظ اند
✅ email_confirmed = email_verified (migrate شد)
✅ NOT NULL محدودیت اعمال شد
✅ همه چیز reversible است
"""

# ============================================================================
# فلو صحیح
# ============================================================================

"""
1. Development میں:
   - Migration ایجاد کنید
   - Test کنید
   - Downgrade/Upgrade تست کنید

2. Testing میں:
   - تمام scenarios تست کنید
   - Performance test
   - Data integrity check

3. Production میں (زمان کم ترافیک):
   - Backup گرفتید؟
   - Alembic upgrade head
   - Monitoring
"""

