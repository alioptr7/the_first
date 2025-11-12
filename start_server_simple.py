#!/usr/bin/env python3
"""
Simple server startup script
Keeps server running
"""

import subprocess
import sys
import os
import time
from pathlib import Path

API_DIR = Path(__file__).parent / "response-network" / "api"
SERVER_LOG = Path(__file__).parent / "server.log"

print(f"Starting Uvicorn server from: {API_DIR}")
print(f"Logs will be written to: {SERVER_LOG}")

env = os.environ.copy()
env['PYTHONUNBUFFERED'] = '1'

try:
    process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "main:app", "--host", "127.0.0.1", "--port", "8000"],
        cwd=str(API_DIR),
        stdout=open(str(SERVER_LOG), "a"),
        stderr=subprocess.STDOUT,
        env=env
    )
    
    print(f"Server started (PID: {process.pid})")
    print("Press Ctrl+C to stop\n")
    
    # Keep the server running
    while True:
        time.sleep(1)
        if process.poll() is not None:
            print("Server process exited!")
            break
            
except KeyboardInterrupt:
    print("\nStopping server...")
    process.terminate()
    try:
        process.wait(timeout=5)
    except:
        process.kill()
    print("Server stopped")
