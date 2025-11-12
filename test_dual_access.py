#!/usr/bin/env python3
"""
Test script to verify dual access management for UserRequestAccess
"""

import requests
import json
import sys
from pathlib import Path

# Configuration
API_BASE = "http://localhost:8000/api/v1"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

def login():
    """Login and get access token"""
    print("[*] Logging in...")
    data = {"username": ADMIN_USERNAME, "password": ADMIN_PASSWORD}
    response = requests.post(f"{API_BASE}/auth/login", data=data, timeout=5)
    
    if response.status_code != 200:
        print(f"[-] Login failed: {response.text}")
        sys.exit(1)
    
    token = response.json()['access_token']
    print(f"[+] Login successful, token: {token[:20]}...")
    return token

def get_headers(token):
    """Get headers with token"""
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

def test_user_request_access_endpoint(token):
    """Test /user-request-access endpoints"""
    print("\n" + "=" * 80)
    print("[*] Testing /user-request-access endpoint")
    print("=" * 80)
    
    headers = get_headers(token)
    
    # List user request access
    print("\n[*] GET /user-request-access - List all user request access")
    response = requests.get(f"{API_BASE}/user-request-access", headers=headers)
    print(f"  Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"  [+] Found {len(data)} access records")
        for record in data:
            print(f"      - User: {record['user_id']}, RequestType: {record['request_type_id']}")
    else:
        print(f"  [-] Error: {response.text}")

def test_request_type_access_endpoint(token):
    """Test /request-types/{id}/access endpoints"""
    print("\n" + "=" * 80)
    print("[*] Testing /request-types/{id}/access endpoint")
    print("=" * 80)
    
    headers = get_headers(token)
    
    # First, get request types to test with
    print("\n[*] GET /request-types - List request types")
    response = requests.get(f"{API_BASE}/request-types", headers=headers)
    print(f"  Status: {response.status_code}")
    
    if response.status_code != 200:
        print(f"  [-] Error: {response.text}")
        return
    
    request_types = response.json()
    if not request_types:
        print("  [-] No request types found")
        return
    
    request_type = request_types[0]
    request_type_id = request_type['id']
    print(f"  [+] Using request type: {request_type['name']} ({request_type_id})")
    
    # List access for this request type
    print(f"\n[*] GET /request-types/{request_type_id}/access - List access for request type")
    response = requests.get(f"{API_BASE}/request-types/{request_type_id}/access", headers=headers)
    print(f"  Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"  [+] Found {len(data)} access records for this request type")
        for record in data:
            print(f"      - User: {record['user_id']}")
    else:
        print(f"  [-] Error: {response.text}")

def verify_consistency(token):
    """Verify that both endpoints show consistent data"""
    print("\n" + "=" * 80)
    print("[*] Verifying data consistency between endpoints")
    print("=" * 80)
    
    headers = get_headers(token)
    
    # Get all access from /user-request-access
    print("\n[*] Getting all access from /user-request-access")
    response1 = requests.get(f"{API_BASE}/user-request-access", headers=headers)
    
    if response1.status_code != 200:
        print(f"  [-] Error: {response1.text}")
        return
    
    user_access_data = response1.json()
    print(f"  [+] Found {len(user_access_data)} records")
    
    # Get request types and their access
    print("\n[*] Getting access from /request-types/{id}/access")
    response2 = requests.get(f"{API_BASE}/request-types", headers=headers)
    
    if response2.status_code != 200:
        print(f"  [-] Error: {response2.text}")
        return
    
    request_types = response2.json()
    rt_access_data = []
    
    for rt in request_types:
        response = requests.get(f"{API_BASE}/request-types/{rt['id']}/access", headers=headers)
        if response.status_code == 200:
            for record in response.json():
                rt_access_data.append(record)
    
    print(f"  [+] Found {len(rt_access_data)} records across all request types")
    
    # Compare
    print("\n[*] Comparing data consistency...")
    print(f"  Records from /user-request-access: {len(user_access_data)}")
    print(f"  Records from /request-types/*/access: {len(rt_access_data)}")
    
    if len(user_access_data) == len(rt_access_data):
        print("  [+] Data is consistent!")
        return True
    else:
        print("  [-] Data mismatch!")
        print(f"\nFrom /user-request-access:")
        for r in user_access_data:
            print(f"  - {r['user_id'][:8]}... -> {r['request_type_id'][:8]}...")
        print(f"\nFrom /request-types/*/access:")
        for r in rt_access_data:
            print(f"  - {r['user_id'][:8]}... -> {r['request_type_id'][:8]}...")
        return False

def main():
    """Main test function"""
    print("\n" + "=" * 80)
    print("Testing Dual User Request Access Management")
    print("=" * 80)
    
    try:
        token = login()
        test_user_request_access_endpoint(token)
        test_request_type_access_endpoint(token)
        is_consistent = verify_consistency(token)
        
        print("\n" + "=" * 80)
        if is_consistent:
            print("[+] All tests passed! Dual access management is working correctly.")
        else:
            print("[-] Tests revealed data inconsistency.")
        print("=" * 80 + "\n")
        
    except Exception as e:
        print(f"\n[-] Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
