#!/usr/bin/env python3
"""
Test script for profile type endpoints
"""

import requests
import json
import sys

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
    print(f"[+] Login successful")
    return token

def get_headers(token):
    """Get headers with token"""
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

def test_profile_types(token):
    """Test profile type endpoints"""
    print("\n" + "=" * 80)
    print("[*] Testing Profile Type Endpoints")
    print("=" * 80)
    
    headers = get_headers(token)
    
    # List all profile types
    print("\n[*] GET /profile-types - List all profile types")
    response = requests.get(f"{API_BASE}/profile-types", headers=headers)
    print(f"  Status: {response.status_code}")
    
    if response.status_code == 200:
        types = response.json()
        print(f"  [+] Found {len(types)} profile types:")
        for ptype in types:
            print(f"      - {ptype}")
    else:
        print(f"  [-] Error: {response.text}")
        return
    
    # Get info for each profile type
    print("\n[*] GET /profile-types/{type} - Get info for each profile type")
    for ptype in types:
        response = requests.get(f"{API_BASE}/profile-types/{ptype}", headers=headers)
        print(f"\n  Profile Type: {ptype}")
        print(f"  Status: {response.status_code}")
        
        if response.status_code == 200:
            info = response.json()
            print(f"  Name: {info.get('name')}")
            print(f"  Description: {info.get('description')}")
            print(f"  Permissions: {', '.join(info.get('permissions', []))}")
        else:
            print(f"  [-] Error: {response.text}")

def main():
    """Main test function"""
    print("\n" + "=" * 80)
    print("Testing Profile Type Management")
    print("=" * 80)
    
    try:
        token = login()
        test_profile_types(token)
        
        print("\n" + "=" * 80)
        print("[+] Profile type tests completed!")
        print("=" * 80 + "\n")
        
    except Exception as e:
        print(f"\n[-] Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
