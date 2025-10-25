"""
Rate limiting middleware using Redis
"""
import structlog
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
import redis.asyncio as aioredis
from typing import Optional
import time

from ..core.config import settings

logger = structlog.get_logger()


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Token bucket rate limiting middleware
    """

    def __init__(self, app, redis_client: Optional[aioredis.Redis] = None):
        super().__init__(app)
        self.redis_client = redis_client

    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for health check
        if request.url.path == "/api/v1/healthz":
            return await call_next(request)

        # Get client IP
        client_ip = request.client.host if request.client else "unknown"

        # Check rate limit
        if self.redis_client:
            try:
                allowed = await self._check_rate_limit(client_ip)
                if not allowed:
                    raise HTTPException(
                        status_code=429,
                        detail="Rate limit exceeded. Please try again later."
                    )
            except Exception as e:
                logger.error("rate_limit_check_failed", error=str(e))
                # Allow request if rate limiting fails

        response = await call_next(request)
        return response

    async def _check_rate_limit(self, client_ip: str) -> bool:
        """
        Check if client is within rate limit using token bucket algorithm

        Args:
            client_ip: Client IP address

        Returns:
            True if allowed, False if rate limited
        """
        key = f"rate_limit:{client_ip}"
        now = time.time()

        # Get current bucket state
        pipe = self.redis_client.pipeline()
        pipe.hget(key, "tokens")
        pipe.hget(key, "last_update")
        tokens_str, last_update_str = await pipe.execute()

        tokens = float(tokens_str) if tokens_str else settings.RATE_LIMIT_BURST
        last_update = float(last_update_str) if last_update_str else now

        # Calculate new tokens based on time elapsed
        time_elapsed = now - last_update
        new_tokens = min(
            settings.RATE_LIMIT_BURST,
            tokens + (time_elapsed * settings.RATE_LIMIT_PER_MINUTE / 60)
        )

        # Check if we have at least 1 token
        if new_tokens >= 1:
            # Consume 1 token
            new_tokens -= 1

            # Update bucket
            pipe = self.redis_client.pipeline()
            pipe.hset(key, "tokens", str(new_tokens))
            pipe.hset(key, "last_update", str(now))
            pipe.expire(key, 3600)  # Expire after 1 hour
            await pipe.execute()

            return True
        else:
            logger.warning("rate_limit_exceeded", client_ip=client_ip)
            return False
