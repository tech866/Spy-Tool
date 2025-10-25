"""
YouTube promoted content adapter
"""
import structlog
from typing import AsyncIterator, Optional
from datetime import datetime

from .base import Adapter, NormalizedAd

logger = structlog.get_logger()


class YouTubeAdapter:
    """
    Adapter for YouTube promoted/sponsored content

    Note: YouTube doesn't have a public ad library like Meta
    This adapter would need to identify promoted content through:
    - YouTube Data API (limited ad info)
    - Monitoring promoted video labels
    - Partner with ad intelligence providers
    """
    name = "youtube"

    async def fetch(self, limit: int = 200) -> AsyncIterator[NormalizedAd]:
        """
        Fetch promoted content from YouTube

        For MVP: Returns demo/mock data
        In production: Use YouTube Data API v3 with proper credentials
        """
        logger.info("youtube_adapter_fetch_start", limit=limit)

        # Placeholder - in production, implement YouTube Data API integration
        # Would require:
        # - YouTube Data API key
        # - Identifying promoted content (limited in public API)
        # - Monitoring specific channels

        logger.info("youtube_adapter_fetch_complete", limit=limit)
        return
        yield  # Make this a generator

    def _normalize(self, raw_data: dict) -> NormalizedAd:
        """Normalize YouTube API response to NormalizedAd"""
        snippet = raw_data.get("snippet", {})

        return NormalizedAd(
            creator_name=snippet.get("channelTitle", "Unknown"),
            creator_handle=snippet.get("channelId"),
            creator_avatar_url=snippet.get("thumbnails", {}).get("default", {}).get("url"),
            platform="youtube",
            title=snippet.get("title"),
            description=snippet.get("description"),
            started_at=datetime.fromisoformat(snippet["publishedAt"].replace("Z", "+00:00")) if snippet.get("publishedAt") else None,
            duration_seconds=self._parse_duration(raw_data.get("contentDetails", {}).get("duration")),
            engagement_count=int(raw_data.get("statistics", {}).get("viewCount", 0)),
            external_url=f"https://youtube.com/watch?v={raw_data.get('id')}",
            funnel_url=None,  # Extract from description if available
            thumb_url=snippet.get("thumbnails", {}).get("high", {}).get("url"),
            is_active=True  # YouTube doesn't expose ad status publicly
        )

    def _parse_duration(self, iso_duration: str) -> Optional[int]:
        """Parse ISO 8601 duration to seconds (e.g., 'PT4M13S' -> 253)"""
        if not iso_duration:
            return None

        import re
        match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', iso_duration)
        if not match:
            return None

        hours = int(match.group(1) or 0)
        minutes = int(match.group(2) or 0)
        seconds = int(match.group(3) or 0)

        return hours * 3600 + minutes * 60 + seconds

    async def close(self):
        """Clean up resources"""
        pass
