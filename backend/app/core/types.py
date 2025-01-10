# backend/app/core/types.py
from typing import Optional
from fastapi import FastAPI
from ..core.rate_limit import RateLimitMiddleware

# Create a custom type that extends FastAPI's state
class AppState:
    rate_limit_middleware: Optional[RateLimitMiddleware] = None

# Create a custom typed FastAPI class
class TypedFastAPI(FastAPI):
    state: AppState