"""
Base adapter interface and normalized ad structure
"""
from typing import Protocol, AsyncIterator, Optional
from pydantic import BaseModel
from datetime import datetime


class NormalizedAd(BaseModel):
    """Normalized ad structure across all platforms"""
    creator_name: str
    creator_handle: Optional[str] = None
    creator_avatar_url: Optional[str] = None
    platform: str  # 'meta', 'tiktok', 'youtube'
    title: Optional[str] = None
    description: Optional[str] = None
    started_at: Optional[datetime] = None
    duration_seconds: Optional[int] = None
    engagement_count: int = 0
    external_url: Optional[str] = None
    funnel_url: Optional[str] = None
    thumb_url: Optional[str] = None
    is_active: bool = True


class Adapter(Protocol):
    """
    Platform adapter interface
    Each adapter must implement fetch() to return normalized ads
    """
    name: str

    async def fetch(self, limit: int = 200) -> AsyncIterator[NormalizedAd]:
        """
        Fetch and normalize ads from the platform

        Args:
            limit: Maximum number of ads to fetch

        Yields:
            NormalizedAd objects
        """
        ...

    async def close(self):
        """Clean up resources (browser, sessions, etc.)"""
        ...
