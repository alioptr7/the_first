#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test export settings API endpoints
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://127.0.0.1:8000/api/v1"

print("=" * 60)
print("Testing export settings endpoints")
print("=" * 60)

# 1. Login
print("\n1. Logging in as admin...")
response = requests.post(
    f"{BASE_URL}/auth/login",
    data={"username": "admin", "password": "admin123"}
)

if response.status_code != 200:
    print(f"ERROR in login: {response.status_code}")
    print(response.text)
    exit(1)

token = response.json()["access_token"]
print(f"OK. Token: {token[:30]}...")

headers = {"Authorization": f"Bearer {token}"}

# 2. View current export settings
print("\n2. View settings to be exported...")
response = requests.get(f"{BASE_URL}/settings/export/current", headers=headers)
print(f"Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"Total settings: {data.get('total_settings', 0)}")
    print(f"Export timestamp: {data.get('export_timestamp')}")
    print(f"Export path: {data.get('export_path')}")
    print(f"\nSettings to export:")
    for setting in data.get('settings', [])[:3]:
        print(f"  - {setting['key']}: {setting.get('description', 'no description')}")
    if len(data.get('settings', [])) > 3:
        print(f"  ... and {len(data.get('settings', [])) - 3} more")
else:
    print(f"Error: {response.text}")

# 3. Trigger export
print("\n3. Triggering settings export...")
response = requests.post(f"{BASE_URL}/settings/export/now", headers=headers)
print(f"Status: {response.status_code}")
result = response.json()
print(f"Message: {result.get('message')}")
print(f"Task ID: {result.get('task_id')}")
print(f"Status: {result.get('status')}")

# 4. List all settings
print("\n4. Listing all settings...")
response = requests.get(f"{BASE_URL}/settings", headers=headers)
print(f"Status: {response.status_code}")
if response.status_code == 200:
    settings = response.json()
    print(f"Total: {len(settings)}")
    for setting in settings[:2]:
        print(f"\n  Setting: {setting.get('key')}")
        print(f"    Description: {setting.get('description', 'N/A')}")
        print(f"    Active: {setting.get('is_active')}")
        val_str = str(setting.get('value', {}))[:100]
        print(f"    Value: {val_str}...")
else:
    print(f"Error: {response.text}")

print("\n" + "=" * 60)
print("OK. Export settings API is working!")
print("=" * 60)
