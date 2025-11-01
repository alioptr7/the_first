"""پردازشگر درخواست‌ها از Redis به PostgreSQL"""
import json
from datetime import datetime
from typing import Dict, Any

from sqlalchemy.orm import Session

from workers.celery_app import celery_app
from workers.database import get_db_session
from workers.redis_client import redis_client
from api.models.request import Request
from api.models.user import User


@celery_app.task(name="process_request_from_redis")
def process_request_from_redis() -> Dict[str, Any]:
    """پردازش درخواست‌های ذخیره شده در Redis و انتقال به PostgreSQL"""
    processed_count = 0
    failed_count = 0
    
    with get_db_session() as db:
        # دریافت همه درخواست‌های در صف
        while True:
            # برداشتن یک درخواست از صف
            raw_request = redis_client.lpop("requests_queue")
            if not raw_request:
                break
                
            try:
                # تبدیل داده‌های JSON به دیکشنری
                request_data = json.loads(raw_request)
                
                # بررسی وجود کاربر
                user = db.query(User).filter(User.id == request_data["user_id"]).first()
                if not user:
                    raise ValueError(f"کاربر با شناسه {request_data['user_id']} یافت نشد")
                
                # ایجاد درخواست در دیتابیس
                request = Request(
                    user_id=request_data["user_id"],
                    request_type_id=request_data["request_type_id"],
                    target_indices=request_data["target_indices"],
                    query_params=request_data["query_params"],
                    created_at=datetime.fromisoformat(request_data["created_at"]),
                    status=request_data["status"],
                    error_message=request_data.get("error_message"),
                    results_count=request_data.get("results_count", 0)
                )
                
                db.add(request)
                db.commit()
                processed_count += 1
                
            except Exception as e:
                failed_count += 1
                # ذخیره درخواست‌های ناموفق در یک صف جداگانه برای بررسی
                redis_client.rpush("failed_requests", raw_request)
                redis_client.rpush("failed_requests_errors", str(e))
    
    return {
        "processed_count": processed_count,
        "failed_count": failed_count,
        "timestamp": datetime.utcnow().isoformat()
    }