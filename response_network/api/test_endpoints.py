import requests
import json
import os

# Corrected BASE_URL to match the running server
BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")
API_V1_STR = "/api/v1" # Assuming v1 prefix is used, adjust if necessary

def print_response(title, response):
    """Helper function to print formatted API responses."""
    print(f"\n{'='*60}")
    print(f"TEST: {title}")
    print(f"{'='*60}")
    print(f"URL: {response.request.method} {response.request.url}")
    print(f"Status Code: {response.status_code}")
    try:
        response_json = response.json()
        print(f"Response Body:\n{json.dumps(response_json, indent=2, ensure_ascii=False)}")
    except json.JSONDecodeError:
        print(f"Response Body (non-JSON):\n{response.text}")
    print("-" * 60)

def test_auth_endpoints(session):
    """Tests authentication-related endpoints: login, me, logout."""
    print("\n--- Testing Authentication Endpoints ---")
    
    # 1. Login
    login_data = {
        "username": "admin",
        "password": "SuperSecureAdminP@ss!"
    }
    # The login endpoint expects form data, not JSON
    response = session.post(f"{BASE_URL}{API_V1_STR}/auth/login", data=login_data)
    print_response("Admin Login", response)
    
    if response.status_code != 200:
        print("Login failed. Aborting further tests.")
        return False

    # 2. Get Current User (/me)
    response = session.get(f"{BASE_URL}{API_V1_STR}/auth/me")
    print_response("Get Current User (me)", response)
    
    return True

def test_user_management_endpoints(session):
    """Tests user management CRUD endpoints."""
    print("\n--- Testing User Management Endpoints ---")
    new_user_id = None

    # 1. Create a new user
    new_user_data = {
        "username": "testuser_from_script",
        "email": "testuser_script@example.com",
        "password": "a-very-secure-password-123",
        "profile_type": "standard",
        "full_name": "Script Test User",
        "allowed_indices": ["test_index", "another_index*"]
    }
    response = session.post(f"{BASE_URL}{API_V1_STR}/users/", json=new_user_data)
    print_response("Create New User", response)
    
    if response.status_code == 200:
        new_user_id = response.json().get("id")
        print(f"--> Successfully created new user with ID: {new_user_id}")

        # 2. Get the new user to verify creation
        response = session.get(f"{BASE_URL}{API_V1_STR}/users/{new_user_id}")
        print_response(f"Get User by ID: {new_user_id}", response)

        # 3. Update the user
        update_data = {"full_name": "Script Test User Updated"}
        response = session.put(f"{BASE_URL}{API_V1_STR}/users/{new_user_id}", json=update_data)
        print_response(f"Update User by ID: {new_user_id}", response)

        # 4. List all users to see the new and updated user
        response = session.get(f"{BASE_URL}{API_V1_STR}/users/")
        print_response("List All Users", response)

        # 5. Delete the user
        response = session.delete(f"{BASE_URL}{API_V1_STR}/users/{new_user_id}")
        print_response(f"Delete User by ID: {new_user_id}", response)

        # 6. Verify user deletion by trying to get them again
        response = session.get(f"{BASE_URL}{API_V1_STR}/users/{new_user_id}")
        print_response(f"Verify Deletion of User {new_user_id} (Expecting 404)", response)

def test_monitoring_endpoints(session):
    """Tests monitoring endpoints."""
    print("\n--- Testing Monitoring Endpoints ---")
    
    response = session.get(f"{BASE_URL}{API_V1_STR}/monitoring/system/health")
    print_response("Get System Health", response)
    
    response = session.get(f"{BASE_URL}{API_V1_STR}/monitoring/logs")
    print_response("Get System Logs", response)

def test_stats_endpoints(session):
    """Tests stats endpoints."""
    print("\n--- Testing Stats Endpoints ---")
    
    response = session.get(f"{BASE_URL}{API_V1_STR}/stats/")
    print_response("Get System Stats", response)

def test_search_endpoints(session):
    """Tests search endpoints."""
    print("\n--- Testing Search Endpoints ---")
    
    search_data = {
        "indices": ["test_index"],
        "query": {"match_all": {}},
        "size": 5
    }
    response = session.post(f"{BASE_URL}{API_V1_STR}/search/", json=search_data)
    print_response("Execute Search Query", response)

def test_settings_endpoints(session):
    """Tests settings CRUD endpoints."""
    print("\n--- Testing Settings Endpoints ---")
    setting_id = None

    # 1. Create a new setting
    new_setting_data = {
        "key": "test_setting_from_script",
        "value": {"enabled": True, "level": 5},
        "is_user_specific": False
    }
    response = session.post(f"{BASE_URL}{API_V1_STR}/settings/", json=new_setting_data)
    print_response("Create New System Setting", response)

    if response.status_code == 200:
        setting_id = response.json().get("id")
        print(f"--> Successfully created new setting with ID: {setting_id}")

        # 2. Get the new setting
        response = session.get(f"{BASE_URL}{API_V1_STR}/settings/{setting_id}")
        print_response(f"Get Setting by ID: {setting_id}", response)

        # 3. Update the setting
        update_data = {"value": {"enabled": False, "level": 10}}
        response = session.put(f"{BASE_URL}{API_V1_STR}/settings/{setting_id}", json=update_data)
        print_response(f"Update Setting by ID: {setting_id}", response)

        # 4. List all settings
        response = session.get(f"{BASE_URL}{API_V1_STR}/settings/")
        print_response("List All Settings", response)

        # 5. Delete is not implemented in the original script, assuming no delete endpoint for now

def test_request_type_endpoints(session):
    """Tests request type CRUD endpoints."""
    print("\n--- Testing Request Type Endpoints ---")
    request_type_id = None

    # 1. Create a new request type
    new_request_type_data = {
        "name": "Test Request Type",
        "description": "A request type created from the test script.",
        "is_active": True,
        "parameters": [
            {"name": "param1", "description": "First parameter", "is_required": True, "param_type": "string"},
            {"name": "param2", "description": "Second parameter", "is_required": False, "param_type": "integer"}
        ],
        "access_rules": []
    }
    response = session.post(f"{BASE_URL}{API_V1_STR}/request-types/", json=new_request_type_data)
    print_response("Create New Request Type", response)

    if response.status_code == 200:
        request_type_id = response.json().get("id")
        print(f"--> Successfully created new request type with ID: {request_type_id}")

        # 2. Get the new request type
        response = session.get(f"{BASE_URL}{API_V1_STR}/request-types/{request_type_id}")
        print_response(f"Get Request Type by ID: {request_type_id}", response)

        # 3. Update the request type
        update_data = {"description": "An updated description."}
        response = session.put(f"{BASE_URL}{API_V1_STR}/request-types/{request_type_id}", json=update_data)
        print_response(f"Update Request Type by ID: {request_type_id}", response)

        # 4. List all request types
        response = session.get(f"{BASE_URL}{API_V1_STR}/request-types/")
        print_response("List All Request Types", response)

        # 5. Delete the request type
        response = session.delete(f"{BASE_URL}{API_V1_STR}/request-types/{request_type_id}")
        print_response(f"Delete Request Type by ID: {request_type_id}", response, expect_no_content=True)

        # 6. Verify deletion
        response = session.get(f"{BASE_URL}{API_V1_STR}/request-types/{request_type_id}")
        print_response(f"Verify Deletion of Request Type {request_type_id} (Expecting 404)", response)

def test_request_endpoints(session):
    """Tests request endpoints."""
    print("\n--- Testing Request Endpoints ---")

    # 1. List all requests (admin user)
    response = session.get(f"{BASE_URL}{API_V1_STR}/requests")
    print_response("List All Requests", response)

    # 2. Get request stats
    response = session.get(f"{BASE_URL}{API_V1_STR}/requests/stats")
    print_response("Get Request Stats", response)

    # Note: Cannot test get by ID without knowing a valid ID.
    # This would require creating a request first, but there is no create endpoint.

def main():
    """Main function to run all endpoint tests."""
    print("🚀 Starting Response Network API Endpoint Tests...")
    
    with requests.Session() as session:
        # Run auth tests first to get the token in the session
        if not test_auth_endpoints(session):
            return

        # Run other tests
        test_user_management_endpoints(session)
        test_monitoring_endpoints(session)
        test_stats_endpoints(session)
        test_search_endpoints(session)
        test_settings_endpoints(session)
        test_request_type_endpoints(session)
        test_request_endpoints(session)

    print("\n✅ Testing Complete")
    print("="*60)

if __name__ == "__main__":
    main()




