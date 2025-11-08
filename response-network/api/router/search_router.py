from typing import List, Annotated
import json

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from response_network.api.auth.dependencies import get_current_active_user, check_user_limits, check_index_access
from response_network.api.core.dependencies import get_db
from response_network.api.models.user import User
from response_network.api.models.request import Request
from response_network.api.schemas.search import QueryRequest, QueryResponse

router = APIRouter(
    prefix="/search",
    tags=["Search"],
)

@router.post(
    "/",
    response_model=QueryResponse,
    status_code=status.HTTP_200_OK,
    description="Execute a search query against Elasticsearch"
)
def get_indices_from_query(query: QueryRequest) -> list[str]:
    """Extract indices from query for index access check."""
    return query.indices

async def execute_search(
    query: QueryRequest,
    current_user: Annotated[User, Depends(check_user_limits)],  # This will check request limits
    db: AsyncSession = Depends(get_db)
):
    """
    Execute a search query against Elasticsearch.
    - Validates request limits
    - Validates index access
    - Enforces max results limit
    """
    # Check index access
    allowed_indices = json.loads(current_user.allowed_indices)
    unauthorized_indices = [idx for idx in query.indices if idx not in allowed_indices]
    if unauthorized_indices:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied to indices: {', '.join(unauthorized_indices)}"
        )
    # Ensure max results limit is respected
    if query.size > current_user.max_results_per_request:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Results size exceeds maximum allowed ({current_user.max_results_per_request})"
        )
    
    # TODO: Implement actual Elasticsearch query execution
    # For now, return a mock response
    return QueryResponse(
        took=100,
        timed_out=False,
        total={"value": 0, "relation": "eq"},
        hits=[]
    )