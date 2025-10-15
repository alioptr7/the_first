from fastapi import HTTPException, status
from pydantic import ValidationError

from ..schemas.request import RequestCreate
from ..models.user import User
from ..schemas.query_params import QUERY_PARAM_SCHEMAS

# --- Whitelists ---
# These should ideally be loaded from a config file or database.
# The ALLOWED_INDICES is now defined per-user.

ALLOWED_QUERY_TYPES = {
    "match",
    "term",
    "range",
    "multi_match",
    # "bool", "wildcard", "fuzzy", "aggregation" # Add as they are implemented
}


def validate_request_payload(data: RequestCreate, user: User):
    """
    Performs a series of validations on the incoming request data.
    Raises HTTPException if any validation fails.
    """
    # 1. Validate Query Type
    if data.query_type not in ALLOWED_QUERY_TYPES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid query_type: '{data.query_type}'.")

    # 2. Validate Query Params Structure
    param_schema = QUERY_PARAM_SCHEMAS.get(data.query_type)
    try:
        validated_params = param_schema(**data.query_params)
    except (ValidationError, TypeError) as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"Invalid query_params for type '{data.query_type}': {e}")

    # 3. Validate Elasticsearch Index Whitelist (from user profile)
    user_allowed_indices = user.allowed_indices or []
    
    # Special case: ["*"] means access to all validated query types' indices.
    # This is a powerful permission and should be used with care.
    if "*" in user_allowed_indices:
        return # User has access to everything, skip index check.

    if validated_params.index not in user_allowed_indices:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Querying index '{validated_params.index}' is not allowed.")