from typing import Any, Dict, List
from pydantic import BaseModel, Field, validator


class BaseQueryParam(BaseModel):
    """Base model for all query parameter schemas."""
    index: str = Field(..., description="The name of the Elasticsearch index to query.")


class MatchQueryParam(BaseQueryParam):
    field: str
    query: str


class TermQueryParam(BaseQueryParam):
    field: str
    value: Any


class RangeQueryParam(BaseQueryParam):
    field: str
    gte: int | str | None = None
    gt: int | str | None = None
    lte: int | str | None = None
    lt: int | str | None = None

    @validator('*', pre=True, always=True)
    def check_at_least_one_range_value(cls, v, values):
        if 'gte' not in values and 'gt' not in values and 'lte' not in values and 'lt' not in values:
             if values.get('field'): # Check if validation has passed field
                raise ValueError("At least one of 'gte', 'gt', 'lte', or 'lt' must be provided for a range query.")
        return v


class MultiMatchQueryParam(BaseQueryParam):
    fields: List[str]
    query: str


# A mapping from query_type string to its corresponding Pydantic model.
QUERY_PARAM_SCHEMAS: Dict[str, type[BaseModel]] = {
    "match": MatchQueryParam,
    "term": TermQueryParam,
    "range": RangeQueryParam,
    "multi_match": MultiMatchQueryParam,
    # TODO: Add schemas for 'bool', 'wildcard', 'fuzzy', 'aggregation'
}