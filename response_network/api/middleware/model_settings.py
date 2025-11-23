from typing import Callable
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from core.config import settings

class ModelSettingsMiddleware(BaseHTTPMiddleware):
    """Middleware for handling model settings like Claude Sonnet 3.5 availability"""
    
    async def dispatch(self, request: Request, call_next: Callable):
        # Before the request is processed
        # Add Claude Sonnet 3.5 flag to request state
        request.state.enable_claude_sonnet_3_5 = settings.ENABLE_CLAUDE_SONNET_3_5
        
        # Process the request
        response = await call_next(request)
        
        return response