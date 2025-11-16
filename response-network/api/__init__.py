import sys
from pathlib import Path

# Ensure Response Network API directory is in sys.path
_api_dir = Path(__file__).resolve().parent
if str(_api_dir) not in sys.path:
    sys.path.insert(0, str(_api_dir))
