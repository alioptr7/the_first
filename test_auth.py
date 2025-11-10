import requests
import json
from datetime import datetime

base_url = "http://localhost:8000"

def print_response(name, response):
    print(f"\n=== {name} ===")
    print(f"Status Code: {response.status_code}")
    try:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except:
        print(f"Response: {response.text}")

# 1. Authentication Test
def test_auth():
    print("\n🔐 Testing Authentication...")
    auth_endpoint = "/api/v1/auth/login"
    data = {
        "username": "admin",
        "password": "admin"
    }
    response = requests.post(base_url + auth_endpoint, data=data)
    print_response("Authentication", response)
    if response.status_code == 200:
        return response.json()["access_token"]
    return None

# 2. User Management Tests
def test_user_endpoints(headers):
    print("\n👥 Testing User Management Endpoints...")
    
    # Get current user
    response = requests.get(f"{base_url}/api/v1/users/me", headers=headers)
    print_response("Get Current User", response)
    
    # List all users
    response = requests.get(f"{base_url}/api/v1/users/", headers=headers)
    print_response("List All Users", response)

# 3. Monitoring and Stats Tests
def test_monitoring_endpoints(headers):
    print("\n📊 Testing Monitoring Endpoints...")
    
    # System monitoring
    response = requests.get(f"{base_url}/api/v1/monitoring/health", headers=headers)
    print_response("System Health", response)
    
    # System stats
    response = requests.get(f"{base_url}/api/v1/monitoring/stats", headers=headers)
    print_response("System Stats", response)

# 4. Request Management Tests
def test_request_endpoints(headers):
    print("\n📝 Testing Request Management Endpoints...")
    
    # List requests
    response = requests.get(
        f"{base_url}/api/v1/requests",
        params={"page": 1, "size": 10},
        headers=headers
    )
    print_response("List Requests", response)
    
    # Get request stats
    response = requests.get(f"{base_url}/api/v1/requests/stats", headers=headers)
    print_response("Request Stats", response)

# 5. Search Tests
def test_search_endpoints(headers):
    print("\n🔍 Testing Search Endpoints...")
    
    # Search requests
    search_data = {
        "query": "test",
        "from_date": "2025-01-01",
        "to_date": datetime.now().strftime("%Y-%m-%d")
    }
    response = requests.post(f"{base_url}/api/v1/search", headers=headers, json=search_data)
    print_response("Search Requests", response)

# Run individual test
def run_test(test_name):
    print(f"\n🚀 Testing {test_name}...")
    
    # First get the token
    token = test_auth()
    if not token:
        print("❌ Authentication failed! Cannot proceed with test.")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    print(f"✅ Successfully got token: {token[:20]}...")
    
    # Run the specified test
    if test_name == "auth":
        pass  # Already done above
    elif test_name == "users":
        test_user_endpoints(headers)
    elif test_name == "monitoring":
        test_monitoring_endpoints(headers)
    elif test_name == "requests":
        test_request_endpoints(headers)
    elif test_name == "search":
        test_search_endpoints(headers)
    else:
        print(f"❌ Unknown test: {test_name}")
        return
    
    print(f"\n✨ {test_name} test completed!")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python test_auth.py <test_name>")
        print("Available tests: auth, users, monitoring, requests, search")
        sys.exit(1)
    run_test(sys.argv[1])