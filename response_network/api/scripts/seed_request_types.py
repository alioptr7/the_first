"""اسکریپت برای افزودن انواع درخواست به پایگاه داده"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from shared.models import RequestType
from workers.config import settings

def main():
    """تابع اصلی برای افزودن انواع درخواست"""
    # ایجاد اتصال به پایگاه داده
    engine = create_engine(settings.RESPONSE_DB_URL)
    Session = sessionmaker(bind=engine)
    session = Session()

    # تعریف انواع درخواست
    request_types = [
        RequestType(name="text_generation", description="تولید متن با استفاده از هوش مصنوعی"),
        RequestType(name="image_generation", description="تولید تصویر با استفاده از هوش مصنوعی"),
        RequestType(name="code_completion", description="تکمیل کد با استفاده از هوش مصنوعی"),
        RequestType(name="translation", description="ترجمه متن به زبان‌های مختلف"),
        RequestType(name="summarization", description="خلاصه‌سازی متن‌های طولانی")
    ]

    # افزودن انواع درخواست به پایگاه داده
    for request_type in request_types:
        existing = session.query(RequestType).filter_by(name=request_type.name).first()
        if not existing:
            session.add(request_type)
    
    # ذخیره تغییرات
    session.commit()
    session.close()

if __name__ == "__main__":
    main()
    print("انواع درخواست با موفقیت به پایگاه داده اضافه شدند.")