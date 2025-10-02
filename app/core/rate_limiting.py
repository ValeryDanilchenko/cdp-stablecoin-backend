import time
from typing import Dict, Tuple

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse


class RateLimiter:
    """Simple in-memory rate limiter for API endpoints."""
    
    def __init__(self, requests_per_minute: int = 60, requests_per_hour: int = 1000):
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        self.minute_requests: Dict[str, list[float]] = {}
        self.hour_requests: Dict[str, list[float]] = {}
    
    def _get_client_id(self, request: Request) -> str:
        """Get client identifier from request."""
        # In production, use proper client identification (API key, IP, etc.)
        client_ip = request.client.host if request.client else "unknown"
        return f"client_{client_ip}"
    
    def _cleanup_old_requests(self, requests: list[float], window_seconds: int) -> None:
        """Remove requests older than the time window."""
        current_time = time.time()
        cutoff_time = current_time - window_seconds
        while requests and requests[0] < cutoff_time:
            requests.pop(0)
    
    def is_allowed(self, request: Request) -> Tuple[bool, str]:
        """
        Check if request is allowed based on rate limits.
        
        Returns:
            Tuple of (is_allowed, error_message)
        """
        client_id = self._get_client_id(request)
        current_time = time.time()
        
        # Initialize client tracking if needed
        if client_id not in self.minute_requests:
            self.minute_requests[client_id] = []
        if client_id not in self.hour_requests:
            self.hour_requests[client_id] = []
        
        # Clean up old requests
        self._cleanup_old_requests(self.minute_requests[client_id], 60)
        self._cleanup_old_requests(self.hour_requests[client_id], 3600)
        
        # Check minute limit
        if len(self.minute_requests[client_id]) >= self.requests_per_minute:
            return False, f"Rate limit exceeded: {self.requests_per_minute} requests per minute"
        
        # Check hour limit
        if len(self.hour_requests[client_id]) >= self.requests_per_hour:
            return False, f"Rate limit exceeded: {self.requests_per_hour} requests per hour"
        
        # Record this request
        self.minute_requests[client_id].append(current_time)
        self.hour_requests[client_id].append(current_time)
        
        return True, ""


# Global rate limiter instance
rate_limiter = RateLimiter()


async def rate_limit_middleware(request: Request, call_next):
    """Rate limiting middleware for FastAPI."""
    # Skip rate limiting for health checks
    if request.url.path.startswith("/health"):
        return await call_next(request)
    
    is_allowed, error_message = rate_limiter.is_allowed(request)
    
    if not is_allowed:
        return JSONResponse(
            status_code=429,
            content={
                "detail": error_message,
                "retry_after": 60  # seconds
            },
            headers={
                "Retry-After": "60",
                "X-RateLimit-Limit": str(rate_limiter.requests_per_minute),
                "X-RateLimit-Remaining": "0"
            }
        )
    
    response = await call_next(request)
    
    # Add rate limit headers to response
    client_id = rate_limiter._get_client_id(request)
    remaining_minute = rate_limiter.requests_per_minute - len(rate_limiter.minute_requests.get(client_id, []))
    remaining_hour = rate_limiter.requests_per_hour - len(rate_limiter.hour_requests.get(client_id, []))
    
    response.headers["X-RateLimit-Limit"] = str(rate_limiter.requests_per_minute)
    response.headers["X-RateLimit-Remaining"] = str(max(0, remaining_minute))
    response.headers["X-RateLimit-Reset"] = str(int(time.time() + 60))
    
    return response
