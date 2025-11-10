# تعریف انواع کاربران مجاز در settings
user_types_setting = {
    "key": "user_types",
    "value": {
        "types": [
            {
                "code": "agent",
                "name": "نماینده فروش",
                "description": "کارمند آژانس با دسترسی محدود",
                "permissions": ["flight_search", "booking_create", "booking_view"],
                "max_requests_per_hour": 100
            },
            {
                "code": "supervisor",
                "name": "سرپرست",
                "description": "سرپرست آژانس با دسترسی گسترده‌تر",
                "permissions": [
                    "flight_search", 
                    "booking_create", 
                    "booking_view",
                    "booking_cancel",
                    "reports_view"
                ],
                "max_requests_per_hour": 200
            },
            {
                "code": "admin",
                "name": "مدیر سیستم",
                "description": "مدیر با دسترسی کامل",
                "permissions": ["*"],
                "max_requests_per_hour": 1000
            }
        ],
        "version": 1
    },
    "description": "انواع کاربران مجاز در سیستم"
}