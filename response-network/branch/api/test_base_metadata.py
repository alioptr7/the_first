import sys
from pathlib import Path

# Setup paths like in alembic env.py
api_dir = Path(__file__).parent
sys.path.insert(0, str(api_dir))

response_network_dir = api_dir.parent
sys.path.insert(0, str(response_network_dir))

project_root = response_network_dir.parent
sys.path.insert(0, str(project_root))

print("=== Testing Base metadata ===\n")

# Import Base like in env.py
from db.base_class import Base as LocalBase
print(f"LocalBase: {LocalBase}")
print(f"LocalBase metadata tables (before models import): {list(LocalBase.metadata.tables.keys())}\n")

# Import all models
from models import (
    User, Request, IncomingRequest, QueryResult,
    ExportBatch, ImportBatch, ExportableSettings,
    RequestType, Settings, SystemHealth, SystemLog,
    UserRequestAccess
)

print(f"LocalBase metadata tables (after models import): {list(LocalBase.metadata.tables.keys())}\n")

# Also check shared Base
from shared.database.base import Base as SharedBase
print(f"SharedBase: {SharedBase}")
print(f"SharedBase metadata tables: {list(SharedBase.metadata.tables.keys())}\n")

# Check if they are the same
print(f"Are they the same Base? {LocalBase is SharedBase}")

# Check each model's Base
print("\n=== Checking each model's __mro__ (inheritance chain) ===")
for model_class in [User, Request, IncomingRequest, QueryResult,
                     ExportBatch, ImportBatch, ExportableSettings,
                     RequestType, Settings, SystemHealth, SystemLog,
                     UserRequestAccess]:
    print(f"{model_class.__name__}: {model_class.__mro__[:3]}")
    print(f"  - Uses LocalBase? {any(LocalBase in cls.__mro__ for cls in [model_class])}")
    print(f"  - Uses SharedBase? {any(SharedBase in cls.__mro__ for cls in [model_class])}")
