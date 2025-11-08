"""Models for system monitoring."""
from datetime import datetime
from typing import Dict, Any
from pydantic import BaseModel


class SystemHealth(BaseModel):
    """System health status model."""
    status: str  # overall system status: healthy, degraded, down
    components: Dict[str, str]  # component name -> status
    components_stats: Dict[str, Dict[str, Any]]  # component name -> detailed stats
    last_check: datetime