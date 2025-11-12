#!/usr/bin/env python3
"""
Script to run server and tests with proper logging
"""

import subprocess
import sys
import time
import os
from pathlib import Path
import requests

API_DIR = Path(__file__).parent / "response-network" / "api"
SERVER_LOG = Path(__file__).parent / "server.log"

def start_server_subprocess():
    """Start server in subprocess with clean logging."""
    print("\n" + "=" * 80)
    print("[*] Starting API Server...")
    print("=" * 80 + "\n")
    
    # Remove old log
    if SERVER_LOG.exists():
        try:
            SERVER_LOG.unlink()
        except:
            pass
    
    env = os.environ.copy()
    env['PYTHONUNBUFFERED'] = '1'
    
    process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"],
        cwd=str(API_DIR),
        stdout=open(str(SERVER_LOG), "w"),
        stderr=subprocess.STDOUT,
        env=env
    )
    
    print(f"[+] Server started (PID: {process.pid})")
    print(f"[+] Logs: {SERVER_LOG}")
    print("\nWaiting for server to be ready...")
    
    # Wait for server to start
    for i in range(30):
        try:
            response = requests.get("http://localhost:8000/docs", timeout=1)
            if response.status_code == 200:
                print("[+] Server is ready!\n")
                return process
        except:
            pass
        
        time.sleep(0.5)
        if i % 6 == 0:
            print(f"  ... waiting ({i}s)")
    
    print("[-] Server did not start in time")
    return process

def test_login():
    """Test login endpoint."""
    print("[*] Testing login endpoint...")
    
    try:
        data = {"username": "admin", "password": "admin123"}
        response = requests.post("http://localhost:8000/api/v1/auth/login", data=data, timeout=5)
        
        print(f"  Status: {response.status_code}")
        if response.status_code == 200:
            print("  [+] Login successful!")
            print(f"  Token: {response.json()['access_token'][:20]}...")
            return True
        else:
            print(f"  [-] Login failed")
            print(f"  Response: {response.text[:200]}")
            return False
    except Exception as e:
        print(f"  [-] Error: {e}")
        return False

def show_logs():
    """Show server logs."""
    print("\n" + "=" * 80)
    print("[*] Server Logs:")
    print("=" * 80)
    
    if SERVER_LOG.exists():
        with open(SERVER_LOG, 'r') as f:
            print(f.read())

def main():
    process = start_server_subprocess()
    
    try:
        success = test_login()
        show_logs()
        
        print("\n" + "=" * 80)
        if success:
            print("[+] Test passed!")
        else:
            print("[-] Test failed - check logs above")
        print("=" * 80)
        print(f"\nServer still running (PID: {process.pid})")
        print("Press Ctrl+C to stop\n")
        
        # Keep running
        while True:
            time.sleep(1)
    
    except KeyboardInterrupt:
        print("\n\nStopping server...")
        process.terminate()
        process.wait()
        print("Server stopped")

if __name__ == "__main__":
    main()
