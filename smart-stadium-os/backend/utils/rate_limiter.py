"""Rate Limiter Middleware for Smart Stadium OS."""

import time
from collections import defaultdict, deque
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

MAX_REQUESTS: int = 30   # Max requests per window per IP
WINDOW_SECONDS: int = 60  # Sliding window size in seconds


class RateLimiterMiddleware(BaseHTTPMiddleware):
    """
    Sliding-window rate limiter middleware.
    Allows MAX_REQUESTS per WINDOW_SECONDS per unique client IP.
    Returns HTTP 429 with Retry-After header on breach.
    """

    def __init__(self, app) -> None:
        super().__init__(app)
        # Maps IP → deque of request timestamps
        self._records: dict[str, deque] = defaultdict(deque)

    async def dispatch(self, request: Request, call_next):
        client_ip: str = request.client.host if request.client else "unknown"
        now: float = time.monotonic()

        window: deque = self._records[client_ip]

        # Evict timestamps outside the sliding window
        while window and now - window[0] > WINDOW_SECONDS:
            window.popleft()

        if len(window) >= MAX_REQUESTS:
            retry_after = int(WINDOW_SECONDS - (now - window[0]))
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Rate limit exceeded",
                    "retry_after_seconds": retry_after,
                },
                headers={"Retry-After": str(retry_after)},
            )

        window.append(now)
        return await call_next(request)
