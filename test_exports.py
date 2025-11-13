#!/usr/bin/env python
"""
Testing script to verify all export tasks are working correctly.
"""
import json
import time
from pathlib import Path
import sys

def check_export_files():
    """Check if export files exist and are valid"""
    
    export_base = Path("response-network/api/exports")
    
    print("\n" + "="*60)
    print("🧪 Testing Export System")
    print("="*60)
    
    results = {
        "settings": False,
        "users": False,
        "profile_types": False
    }
    
    # 1. Check Settings Export
    print("\n1️⃣ Checking Settings Export...")
    settings_dir = export_base / "settings"
    if settings_dir.exists():
        latest_file = settings_dir / "latest.json"
        if latest_file.exists():
            try:
                with open(latest_file) as f:
                    data = json.load(f)
                print(f"   ✅ Found: {latest_file}")
                print(f"   📊 Total settings: {data.get('total_count', 0)}")
                print(f"   📅 Exported at: {data.get('exported_at', 'N/A')}")
                print(f"   Version: {data.get('version', 'N/A')}")
                
                if data.get('total_count', 0) == 0:
                    print("   ⚠️  Warning: No settings exported (is_public must be True)")
                else:
                    results["settings"] = True
                    # Show first setting
                    if data.get('settings'):
                        first = data['settings'][0]
                        print(f"   📝 Sample: {first['key']} = {first['value']}")
            except json.JSONDecodeError:
                print(f"   ❌ Invalid JSON: {latest_file}")
        else:
            print(f"   ❌ Not found: {latest_file}")
    else:
        print(f"   ❌ Directory not found: {settings_dir}")
    
    # 2. Check Users Export
    print("\n2️⃣ Checking Users Export...")
    users_dir = export_base / "users"
    if users_dir.exists():
        latest_file = users_dir / "latest.json"
        if latest_file.exists():
            try:
                with open(latest_file) as f:
                    data = json.load(f)
                print(f"   ✅ Found: {latest_file}")
                print(f"   👥 Total users: {data.get('total_count', 0)}")
                print(f"   📅 Exported at: {data.get('exported_at', 'N/A')}")
                
                if data.get('total_count', 0) > 0:
                    results["users"] = True
                    # Show first user
                    if data.get('users'):
                        first = data['users'][0]
                        print(f"   📝 Sample: {first['username']} ({first['role']})")
                else:
                    print("   ⚠️  Warning: No users exported")
            except json.JSONDecodeError:
                print(f"   ❌ Invalid JSON: {latest_file}")
        else:
            print(f"   ❌ Not found: {latest_file}")
    else:
        print(f"   ❌ Directory not found: {users_dir}")
    
    # 3. Check ProfileTypes Export
    print("\n3️⃣ Checking ProfileTypes Export...")
    profile_types_dir = export_base / "profile_types"
    if profile_types_dir.exists():
        latest_file = profile_types_dir / "latest.json"
        if latest_file.exists():
            try:
                with open(latest_file) as f:
                    data = json.load(f)
                print(f"   ✅ Found: {latest_file}")
                print(f"   🎯 Total profile types: {data.get('total_count', 0)}")
                print(f"   📅 Exported at: {data.get('exported_at', 'N/A')}")
                
                if data.get('total_count', 0) > 0:
                    results["profile_types"] = True
                    # Show first profile type
                    if data.get('profile_types'):
                        first = data['profile_types'][0]
                        allowed = first.get('allowed_request_types', [])
                        print(f"   📝 Sample: {first['name']} ({first['display_name']})")
                        print(f"      Allowed types: {', '.join(allowed) if allowed else 'All'}")
                        print(f"      Daily limit: {first.get('daily_request_limit', 'N/A')}")
                else:
                    print("   ⚠️  Warning: No profile types exported")
            except json.JSONDecodeError:
                print(f"   ❌ Invalid JSON: {latest_file}")
        else:
            print(f"   ❌ Not found: {latest_file}")
    else:
        print(f"   ❌ Directory not found: {profile_types_dir}")
    
    # Summary
    print("\n" + "="*60)
    print("📊 Results Summary:")
    print("="*60)
    
    for key, value in results.items():
        status = "✅ PASS" if value else "❌ FAIL"
        print(f"  {key.upper():20} {status}")
    
    all_passed = all(results.values())
    
    print("\n" + "="*60)
    if all_passed:
        print("🎉 All exports working correctly!")
        print("="*60)
        return 0
    else:
        print("⚠️  Some exports need attention")
        print("="*60)
        print("\ndebugging tips:")
        print("  1. Make sure Beat is running: python start_beat.py")
        print("  2. Make sure Worker is running: python start_worker.py")
        print("  3. Check logs: docker-compose logs -f beat")
        print("  4. Wait ~60 seconds for first export")
        return 1

if __name__ == "__main__":
    # Change to API directory
    import os
    api_dir = Path(__file__).parent / "response-network" / "api"
    os.chdir(api_dir)
    
    exit_code = check_export_files()
    sys.exit(exit_code)
