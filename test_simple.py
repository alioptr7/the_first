"""Simple API test script"""
import requests
import json

BASE_URL = "http://localhost:8000"
API_V1 = f"{BASE_URL}/api/v1"

# Test login with form data
print("Testing login endpoint...")
login_data = {
    "username": "admin",
    "password": "admin123"
}

# Use data parameter instead of json for form data
response = requests.post(
    f"{API_V1}/auth/login",
    data=login_data
)

print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}")

if response.status_code == 200:
    token = response.json().get("access_token")
    print(f"\nToken obtained: {token[:20]}...")
    
    # Test auth me
    print("\nTesting /auth/me endpoint...")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{API_V1}/auth/me", headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
else:
    print("Login failed!")
