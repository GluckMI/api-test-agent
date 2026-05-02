"""
API Test Agent GUI - Rate limiting middleware

Sliding window rate limiter that tracks requests per IP per endpoint group.
- Execution endpoints: 10 requests/minute/IP
- CRUD endpoints: 30 requests/minute/IP
- Returns HTTP 429 when limit exceeded
"""
import time
import threading
from collections import defaultdict
from typing import Dict, List, Tuple
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse


EXECUTION_LIMIT = 10
CRUD_LIMIT = 30
WINDOW_SECONDS = 60


EXECUTION_PATHS = [
    "/api/execution/",
]

CRUD_PATHS = [
    "/api/projects/",
    "/api/tests/",
    "/api/environments/",
    "/api/reports/",
]


class RateLimiter:
    """Sliding window rate limiter."""

    def __init__(self):
        self._lock = threading.Lock()
        self._requests: Dict[str, List[float]] = defaultdict(list)

    def _get_client_key(self, request: Request) -> str:
        client_host = request.client.host if request.client else "unknown"
        return f"{client_host}"

    def _get_endpoint_group(self, path: str) -> Tuple[str, int]:
        if path.startswith("/ws/"):
            return None, 0
        for p in EXECUTION_PATHS:
            if path.startswith(p):
                return "execution", EXECUTION_LIMIT
        for p in CRUD_PATHS:
            if path.startswith(p):
                return "crud", CRUD_LIMIT
        return None, 0

    def is_allowed(self, request: Request) -> Tuple[bool, int, int]:
        client_key = self._get_client_key(request)
        group, limit = self._get_endpoint_group(request.url.path)

        if group is None:
            return True, 0, 0

        now = time.time()
        window_start = now - WINDOW_SECONDS
        bucket_key = f"{client_key}:{group}"

        with self._lock:
            timestamps = self._requests[bucket_key]
            self._requests[bucket_key] = [t for t in timestamps if t > window_start]
            current_count = len(self._requests[bucket_key])

            if current_count >= limit:
                return False, current_count, limit

            self._requests[bucket_key].append(now)
            return True, current_count + 1, limit

    def cleanup(self):
        now = time.time()
        window_start = now - WINDOW_SECONDS
        with self._lock:
            for key in list(self._requests.keys()):
                self._requests[key] = [t for t in self._requests[key] if t > window_start]
                if not self._requests[key]:
                    del self._requests[key]


rate_limiter = RateLimiter()


def _get_endpoint_group(path: str) -> Tuple[str, int]:
    """Get the endpoint group and limit for a given path."""
    if path.startswith("/ws/"):
        return None, 0
    for p in EXECUTION_PATHS:
        if path.startswith(p):
            return "execution", EXECUTION_LIMIT
    for p in CRUD_PATHS:
        if path.startswith(p):
            return "crud", CRUD_LIMIT
    return None, 0


class RateLimitMiddleware(BaseHTTPMiddleware):
    """FastAPI middleware that applies rate limiting."""

    async def dispatch(self, request: Request, call_next):
        group, limit = _get_endpoint_group(request.url.path)
        if group is not None and limit > 0:
            allowed, current, max_limit = rate_limiter.is_allowed(request)

            if not allowed:
                return JSONResponse(
                    status_code=429,
                    content={
                        "detail": "Rate limit exceeded",
                        "limit": max_limit,
                        "window_seconds": WINDOW_SECONDS,
                        "retry_after": WINDOW_SECONDS,
                    },
                    headers={
                        "Retry-After": str(WINDOW_SECONDS),
                        "X-RateLimit-Limit": str(max_limit),
                        "X-RateLimit-Remaining": "0",
                        "X-RateLimit-Window": str(WINDOW_SECONDS),
                    },
                )

            response = await call_next(request)
            response.headers["X-RateLimit-Limit"] = str(max_limit)
            response.headers["X-RateLimit-Remaining"] = str(max(0, max_limit - current))
            response.headers["X-RateLimit-Window"] = str(WINDOW_SECONDS)
            return response

        return await call_next(request)
