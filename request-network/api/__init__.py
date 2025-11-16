import sys
from pathlib import Path

# FIRST - Ensure Request Network API directory is in sys.path
_req_api_dir = Path(__file__).resolve().parent
if str(_req_api_dir) not in sys.path:
    sys.path.insert(0, str(_req_api_dir))

# SECOND - Then shared can be added
_shared_dir = Path(__file__).resolve().parents[1]
if str(_shared_dir) not in sys.path:
    sys.path.insert(1, str(_shared_dir))
