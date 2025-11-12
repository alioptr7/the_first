import subprocess
import time
import sys

# Start Uvicorn server
print("Starting Uvicorn server...")
process = subprocess.Popen(
    [sys.executable, "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"],
    cwd="c:\\Users\\win\\the_first\\response-network\\api",
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    bufsize=1
)

print("Server started. Waiting for it to be ready...")
time.sleep(5)
print("Server should be running on http://0.0.0.0:8000")
print("Press Ctrl+C to stop the server")

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\nStopping server...")
    process.terminate()
    process.wait()
    print("Server stopped")
