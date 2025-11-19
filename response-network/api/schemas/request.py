from pydantic import BaseModel
from datetime import datetime
from typing import List, Dict, Any, Optional


class RequestItem(BaseModel):
    id: str
    query: Optional[str] = None
    parameters: Dict[str, Any] = {}
    priority: int = 5
    created_at: datetime


class RequestImport(BaseModel):
    requests: List[RequestItem]


class RequestExport(BaseModel):
    requests: List[Dict[str, Any]]
    exported_at: datetime
    version: int
