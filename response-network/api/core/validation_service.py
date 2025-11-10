from datetime import datetime
import re
from typing import Any, Dict

from fastapi import HTTPException, status
from pydantic import ValidationError


class ValidationService:
    @staticmethod
    def validate_parameter(value: Any, rules: Dict[str, Any]) -> None:
        """Validates a parameter value against provided rules."""
        
        # Pattern validation (regex)
        if "pattern" in rules:
            pattern = rules["pattern"]
            if not isinstance(value, str) or not re.match(pattern, value):
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Value does not match pattern {pattern}"
                )
                
        # Format validation (e.g., date)
        if "format" in rules:
            fmt = rules["format"]
            if fmt == "YYYY-MM-DD":
                try:
                    datetime.strptime(value, "%Y-%m-%d")
                except (ValueError, TypeError):
                    raise HTTPException(
                        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                        detail=f"Invalid date format. Expected {fmt}"
                    )
                    
        # Length validation
        if isinstance(value, str):
            if "min_length" in rules and len(value) < rules["min_length"]:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Length must be at least {rules['min_length']}"
                )
            if "max_length" in rules and len(value) > rules["max_length"]:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Length must be at most {rules['max_length']}"
                )
                
        # Range validation (for numbers)
        if isinstance(value, (int, float)):
            if "minimum" in rules and value < rules["minimum"]:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Value must be at least {rules['minimum']}"
                )
            if "maximum" in rules and value > rules["maximum"]:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Value must be at most {rules['maximum']}"
                )
                
        # Enumeration validation
        if "enum" in rules and value not in rules["enum"]:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Value must be one of: {', '.join(map(str, rules['enum']))}"
            )


validation_service = ValidationService()