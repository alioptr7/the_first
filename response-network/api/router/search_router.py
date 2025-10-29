from typing import List, Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from auth.dependencies import get_current_active_user, check_user_limits, check_index_access
from core.dependencies import get_db_session
from models.user import User
from models.request import Request
from schemas.request import QueryRequest, QueryResponse

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
async def execute_search(
    query: QueryRequest,
    current_user: Annotated[User, Depends(check_user_limits)],  # This will check request limits
    _: Annotated[User, Depends(check_index_access(query.indices))],  # This will check index access
    db: AsyncSession = Depends(get_db_session),
):
    """
    Execute a search query against Elasticsearch.
    - Validates request limits
    - Validates index access
    - Enforces max results limit
    """
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