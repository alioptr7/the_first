import sys
from pathlib import Path
api_dir = Path(__file__).parent
sys.path.insert(0, str(api_dir))
project_root = api_dir.parent.parent
sys.path.insert(0, str(project_root))

print("Testing model imports...")

from db.base_class import Base
print(f"Base from db.base_class: {Base}")

import models
print(f"\nModels imported: {dir(models)}")

print(f"\nSubclasses of Base: {[c.__name__ for c in Base.__subclasses__()]}")
print(f"\nTables in metadata: {list(Base.metadata.tables.keys())}")
