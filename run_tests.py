#!/usr/bin/env python3
"""
Script to run the API server in a separate terminal and execute tests in the current terminal.
"""

import subprocess
import time
import sys
import os
from pathlib import Path

# Paths
API_DIR = Path(__file__).parent / "response-network" / "api"
SERVER_LOG = API_DIR / "server.log"
TEST_SCRIPT = Path(__file__).parent / "test_simple.py"

def start_server():
    """Start the Uvicorn server in a new PowerShell window."""
    print("=" * 80)
    print("📡 Starting API Server in a new terminal...")
    print("=" * 80)
    
    # PowerShell command to start server
    ps_command = f"""
$ErrorActionPreference = 'Continue'
cd '{API_DIR}'
Write-Host 'Starting Uvicorn server...' -ForegroundColor Cyan
Write-Host 'Server will be running on http://0.0.0.0:8000' -ForegroundColor Green
Write-Host 'Press Ctrl+C in this window to stop the server' -ForegroundColor Yellow
python -m uvicorn main:app --host 0.0.0.0 --port 8000 2>&1 | Tee-Object -FilePath server.log -Append
"""
    
    # Start new PowerShell window
    try:
        subprocess.Popen([
            "powershell", "-NoProfile", "-Command", ps_command
        ])
        print("✓ Server terminal opened")
        print(f"✓ Logs will be saved to: {SERVER_LOG}")
        print("\nWaiting for server to start...")
        time.sleep(5)
        print("✓ Server should be ready now!")
    except Exception as e:
        print(f"✗ Error starting server: {e}")
        sys.exit(1)

def run_tests():
    """Run test script."""
    print("\n" + "=" * 80)
    print("🧪 Running API Tests...")
    print("=" * 80 + "\n")
    
    try:
        result = subprocess.run(
            [sys.executable, str(TEST_SCRIPT)],
            cwd=Path(__file__).parent
        )
        return result.returncode == 0
    except Exception as e:
        print(f"✗ Error running tests: {e}")
        return False

def show_logs(lines=30):
    """Show recent server logs."""
    print("\n" + "=" * 80)
    print(f"📋 Recent Server Logs (last {lines} lines):")
    print("=" * 80)
    
    if SERVER_LOG.exists():
        try:
            with open(SERVER_LOG, 'r', encoding='utf-8', errors='ignore') as f:
                all_lines = f.readlines()
                recent_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
                print(''.join(recent_lines))
        except Exception as e:
            print(f"✗ Error reading logs: {e}")
    else:
        print(f"Log file not found: {SERVER_LOG}")

def main():
    """Main function."""
    print("\n" + "=" * 80)
    print("🚀 API Server Testing Suite")
    print("=" * 80 + "\n")
    
    # Start server in new terminal
    start_server()
    
    # Run tests
    test_passed = run_tests()
    
    # Show logs
    show_logs(50)
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 Test Summary:")
    print("=" * 80)
    print(f"Server running on: http://0.0.0.0:8000")
    print(f"Logs location: {SERVER_LOG}")
    if test_passed:
        print("✓ Tests completed successfully!")
    else:
        print("✗ Tests encountered issues - check logs above")
    print("\nNote: Server is still running in the separate terminal.")
    print("Close that terminal to stop the server.")
    print("=" * 80 + "\n")

if __name__ == "__main__":
    main()
