#!/usr/bin/env python
"""
Beat Launcher - Starts Celery Beat scheduler
"""
import sys
import os
import subprocess

def start_beat():
    """شروع Celery Beat Scheduler"""
    
    # Change to API directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    cmd = [
        sys.executable,
        "-m",
        "celery",
        "-A",
        "workers.celery_app",
        "beat",
        "--loglevel=info",
    ]
    
    print(f"\n{'='*60}")
    print(f"⏰ Starting Celery Beat Scheduler")
    print(f"{'='*60}")
    print(f"Command: {' '.join(cmd)}\n")
    print("📋 Scheduled Tasks:")
    print("   - export_settings_to_request_network (every 60 seconds)\n")
    
    # Start beat
    subprocess.run(cmd)

if __name__ == "__main__":
    start_beat()
