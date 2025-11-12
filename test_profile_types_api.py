#!/usr/bin/env python
"""Test profile types API"""

import requests
import json

BASE_URL = "http://127.0.0.1:8000/api/v1"

# 1. Login
print("1. Logging in as admin...")
response = requests.post(
    f"{BASE_URL}/auth/login",
    data={"username": "admin", "password": "admin123"}
)
print(f"Login status: {response.status_code}")
if response.status_code != 200:
    print(f"Login failed: {response.text}")
    exit(1)

token = response.json()["access_token"]
print(f"Token: {token[:20]}...")

headers = {"Authorization": f"Bearer {token}"}

# 2. List profile types (should be empty initially)
print("\n2. Listing profile types (should be empty)...")
response = requests.get(f"{BASE_URL}/profile-types", headers=headers)
print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}")

# 3. Create a custom profile type
print("\n3. Creating custom profile type: 'power_user'...")
new_type = {
    "name": "power_user",
    "display_name": "Power User",
    "description": "User with enhanced permissions",
    "permissions": {
        "read": True,
        "write": True,
        "export": True,
        "manage_users": False
    },
    "daily_request_limit": 500,
    "monthly_request_limit": 10000,
    "max_results_per_request": 5000,
    "is_active": True,
    "config_metadata": {
        "category": "enterprise",
        "priority": 1
    }
}
response = requests.post(f"{BASE_URL}/profile-types", json=new_type, headers=headers)
print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}")

# 4. List profile types again
print("\n4. Listing profile types after creating one...")
response = requests.get(f"{BASE_URL}/profile-types", headers=headers)
print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}")

# 5. Get specific profile type
print("\n5. Getting profile type 'power_user'...")
response = requests.get(f"{BASE_URL}/profile-types/power_user", headers=headers)
print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}")

# 6. Update profile type
print("\n6. Updating profile type 'power_user'...")
update_data = {
    "display_name": "Power User (Updated)",
    "daily_request_limit": 750,
    "permissions": {
        "read": True,
        "write": True,
        "export": True,
        "manage_users": True
    }
}
response = requests.put(f"{BASE_URL}/profile-types/power_user", json=update_data, headers=headers)
print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}")

# 7. Try to create profile type with builtin name (should fail)
print("\n7. Trying to create profile type with builtin name 'admin' (should fail)...")
admin_type = {
    "name": "admin",
    "display_name": "Admin Copy",
    "description": "Copy of admin",
    "is_active": True
}
response = requests.post(f"{BASE_URL}/profile-types", json=admin_type, headers=headers)
print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}")

# 8. Delete profile type
print("\n8. Deleting profile type 'power_user'...")
response = requests.delete(f"{BASE_URL}/profile-types/power_user", headers=headers)
print(f"Status: {response.status_code}")
if response.text:
    print(f"Response: {response.text}")
else:
    print("Deleted successfully (no response body)")

# 9. Try to delete builtin type (should fail)
print("\n9. Trying to delete builtin profile type 'admin' (should fail)...")
response = requests.delete(f"{BASE_URL}/profile-types/admin", headers=headers)
print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}")

# 10. List profile types after deletion
print("\n10. Listing profile types after deletion...")
response = requests.get(f"{BASE_URL}/profile-types", headers=headers)
print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}")

print("\n✅ Profile types API tests completed!")
