# backend/app/core/rate_limit.py
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Dict, Optional, Tuple, Any
import time
import logging
from datetime import datetime
from collections import defaultdict
import asyncio
from .config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

class RateLimiter:
    """Rate limiter implementation using sliding window algorithm"""

    def __init__(self):
        # Structure: {key: [(timestamp, count)]}
        self._windows: Dict[str, list] = defaultdict(list)
        # Default limits
        self.default_rate_limits = {
            "general": (100, 60),     # 100 requests per minute for general endpoints
            "auth": (20, 60),         # 20 requests per minute for auth endpoints
            "api": (1000, 3600),      # 1000 requests per hour for API endpoints
        }
        # Cleanup task
        self._cleanup_task = None

    async def start_cleanup(self):
        """Start the cleanup task"""
        if self._cleanup_task is None:
            self._cleanup_task = asyncio.create_task(self._cleanup_loop())

    async def stop_cleanup(self):
        """Stop the cleanup task"""
        if self._cleanup_task is not None:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
            self._cleanup_task = None

    async def _cleanup_loop(self):
        """Periodically clean up expired windows"""
        while True:
            try:
                self._cleanup_expired_windows()
                await asyncio.sleep(60)  # Run cleanup every minute
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cleanup loop: {e}")
                await asyncio.sleep(60)  # Wait before retrying

    def _cleanup_expired_windows(self):
        """Remove expired windows"""
        now = time.time()
        for key in list(self._windows.keys()):
            # Get the maximum window size for this key
            _, window = self._get_limit_for_key(key)
            # Remove windows older than the window size
            self._windows[key] = [
                w for w in self._windows[key]
                if now - w[0] < window
            ]
            # Remove empty lists
            if not self._windows[key]:
                del self._windows[key]

    def _get_limit_for_key(self, key: str) -> Tuple[int, int]:
        """Get rate limit for a specific key"""
        if key.startswith("auth:"):
            return self.default_rate_limits["auth"]
        elif key.startswith("api:"):
            return self.default_rate_limits["api"]
        return self.default_rate_limits["general"]

    async def is_allowed(
        self,
        key: str,
        window_size: Optional[int] = None,
        max_requests: Optional[int] = None
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Check if request is allowed based on rate limiting rules
        
        Args:
            key: Identifier for the rate limit bucket
            window_size: Optional override for window size in seconds
            max_requests: Optional override for maximum requests
            
        Returns:
            Tuple of (is_allowed, limit_info)
        """
        now = time.time()

        # Get limits
        if max_requests is None or window_size is None:
            max_requests, window_size = self._get_limit_for_key(key)

        # Clean up old requests for this key
        self._windows[key] = [
            w for w in self._windows[key]
            if now - w[0] < window_size
        ]

        # Count requests in current window
        current_count = sum(w[1] for w in self._windows[key])

        # Calculate remaining quota and reset time
        remaining = max(0, max_requests - current_count)
        if self._windows[key]:
            oldest_timestamp = min(w[0] for w in self._windows[key])
            reset_time = oldest_timestamp + window_size
        else:
            reset_time = now + window_size

        limit_info = {
            "limit": max_requests,
            "remaining": remaining,
            "reset": datetime.fromtimestamp(reset_time).isoformat(),
            "window_size": window_size
        }

        if current_count >= max_requests:
            return False, limit_info

        # Add new request
        self._windows[key].append((now, 1))
        return True, limit_info

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware for rate limiting requests"""

    def __init__(self, app, limiter: RateLimiter = None):
        super().__init__(app)
        self.limiter = limiter or RateLimiter()

    async def dispatch(self, request: Request, call_next):
        try:
            # Start cleanup task if not running
            await self.limiter.start_cleanup()

            # Determine rate limit key based on request
            limit_key = self._get_limit_key(request)

            # Check rate limit
            is_allowed, limit_info = await self.limiter.is_allowed(limit_key)

            if not is_allowed:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail={
                        "error": "Rate limit exceeded",
                        "limit_info": limit_info
                    }
                )

            # Process request
            response = await call_next(request)

            # Add rate limit headers
            response.headers["X-RateLimit-Limit"] = str(limit_info["limit"])
            response.headers["X-RateLimit-Remaining"] = str(limit_info["remaining"])
            response.headers["X-RateLimit-Reset"] = limit_info["reset"]

            return response

        except HTTPException as exc:
            raise exc
        except Exception as e:
            logger.error(f"Error in rate limit middleware: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error during rate limiting"
            )

    def _get_limit_key(self, request: Request) -> str:
        """Generate rate limit key based on request characteristics"""
        # Get client IP
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            ip = forwarded.split(",")[0].strip()
        else:
            ip = request.client.host

        # Check if it's an API request
        if "X-API-Key" in request.headers:
            return f"api:{ip}"

        # Check if it's an auth endpoint
        if request.url.path.startswith("/auth"):
            return f"auth:{ip}"

        # General requests
        return f"general:{ip}"

    async def cleanup(self):
        """Cleanup rate limiter resources"""
        await self.limiter.stop_cleanup()