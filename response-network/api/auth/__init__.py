import sys
from pathlib import Path

# Ensure Response Network API is in sys.path FIRST
_api_dir = Path(__file__).resolve().parent.parent
if str(_api_dir) not in sys.path:
    sys.path.insert(0, str(_api_dir))
