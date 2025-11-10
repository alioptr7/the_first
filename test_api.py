import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_create_request():
    # ایجاد یک درخواست جدید
    data = {
        "title": "درخواست تست",
        "description": "این یک درخواست تست است",
        "priority": 1,
        "status": "pending"
    }
    
    response = requests.post(f"{BASE_URL}/requests/", json=data)
    print(f"\nCreate Request Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    return response.json()

def test_get_request(request_id):
    # دریافت یک درخواست با شناسه
    response = requests.get(f"{BASE_URL}/requests/{request_id}")
    print(f"\nGet Request Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    return response.json()

def test_update_request(request_id):
    # به‌روزرسانی یک درخواست
    data = {
        "title": "درخواست به‌روز شده",
        "description": "توضیحات به‌روز شده",
        "status": "in_progress"
    }
    
    response = requests.put(f"{BASE_URL}/requests/{request_id}", json=data)
    print(f"\nUpdate Request Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    return response.json()

def test_list_requests():
    # دریافت لیست درخواست‌ها
    response = requests.get(f"{BASE_URL}/requests")
    print(f"\nList Requests Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    return response.json()

def run_tests():
    print("=== شروع تست‌ها ===")
    
    # تست ایجاد درخواست جدید
    created_request = test_create_request()
    request_id = created_request.get("id")
    
    if request_id:
        # تست دریافت درخواست
        test_get_request(request_id)
        
        # تست به‌روزرسانی درخواست
        test_update_request(request_id)
    
    # تست لیست درخواست‌ها
    test_list_requests()
    
    print("\n=== پایان تست‌ها ===")

if __name__ == "__main__":
    run_tests()