"""پردازشگر پاسخ‌ها از Redis به PostgreSQL"""
import json
from datetime import datetime
from typing import Dict, Any

from sqlalchemy.orm import Session

from workers.celery_app import celery_app
from workers.database import get_db_session
from workers.redis_client import redis_client
from ...api.models.request import Request
from ...api.models.response import Response


@celery_app.task(name="process_response_from_redis")
def process_response_from_redis() -> Dict[str, Any]:
    """پردازش پاسخ‌های ذخیره شده در Redis و انتقال به PostgreSQL"""
    processed_count = 0
    failed_count = 0
    
    with get_db_session() as db:
        # دریافت همه پاسخ‌های در صف
        while True:
            # برداشتن یک پاسخ از صف
            raw_response = redis_client.lpop("responses_queue")
            if not raw_response:
                break
                
            try:
                # تبدیل داده‌های JSON به دیکشنری
                response_data = json.loads(raw_response)
                
                # بررسی وجود درخواست مرتبط
                request = db.query(Request).filter(Request.id == response_data["request_id"]).first()
                if not request:
                    raise ValueError(f"درخواست با شناسه {response_data['request_id']} یافت نشد")
                
                # ایجاد پاسخ در دیتابیس
                response = Response(
                    request_id=response_data["request_id"],
                    status_code=response_data["status_code"],
                    response_time=response_data["response_time"],
                    results=response_data["results"],
                    created_at=datetime.fromisoformat(response_data["created_at"]),
                    error_message=response_data.get("error_message")
                )
                
                db.add(response)
                
                # به‌روزرسانی وضعیت درخواست
                request.status = "completed" if response.status_code == 200 else "failed"
                request.error_message = response.error_message
                request.results_count = len(response.results) if response.results else 0
                
                db.commit()
                processed_count += 1
                
            except Exception as e:
                failed_count += 1
                # ذخیره پاسخ‌های ناموفق در یک صف جداگانه برای بررسی
                redis_client.rpush("failed_responses", raw_response)
                redis_client.rpush("failed_responses_errors", str(e))
    
    return {
        "processed_count": processed_count,
        "failed_count": failed_count,
        "timestamp": datetime.utcnow().isoformat()
    }