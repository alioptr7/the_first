from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class QueryRequest(BaseModel):
    """Schema for a search request."""
    indices: List[str] = Field(..., description="List of indices to search in")
    query: Dict[str, Any] = Field(..., description="Elasticsearch query DSL")
    size: int = Field(default=10, ge=1, le=10000, description="Maximum number of results to return")
    from_: Optional[int] = Field(default=0, ge=0, alias="from", description="Starting offset for pagination")
    source: Optional[List[str]] = Field(default=None, description="List of fields to return")
    sort: Optional[List[Dict[str, Any]]] = Field(default=None, description="Sort criteria")

class QueryHit(BaseModel):
    """Schema for a single search result hit."""
    _index: str
    _id: str
    _score: float
    _source: Dict[str, Any]

class QueryTotal(BaseModel):
    """Schema for total hits information."""
    value: int
    relation: str

class QueryResponse(BaseModel):
    """Schema for a search response."""
    took: int
    timed_out: bool
    total: QueryTotal
    hits: List[QueryHit]
    aggregations: Optional[Dict[str, Any]] = None