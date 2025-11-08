import sys
import os
import uvicorn

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

if __name__ == "__main__":
    uvicorn.run("response-network.api.main:app", host="127.0.0.1", port=8000, reload=True)
