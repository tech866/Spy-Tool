"""
TikTok Creative Center adapter
"""
import structlog
from typing import AsyncIterator
from datetime import datetime

from .base import Adapter, NormalizedAd

logger = structlog.get_logger()


class TikTokAdapter:
    """
    Adapter for TikTok Creative Center

    Note: TikTok Creative Center requires authentication and has strict ToS
    This is a placeholder implementation for MVP
    """
    name = "tiktok"

    async def fetch(self, limit: int = 200) -> AsyncIterator[NormalizedAd]:
        """
        Fetch ads from TikTok Creative Center

        For MVP: Returns demo/mock data
        In production: Use TikTok for Business API or Creative Center export
        """
        logger.info("tiktok_adapter_fetch_start", limit=limit)

        # Placeholder - in production, implement TikTok API integration
        # TikTok Creative Center API would require:
        # - Business account credentials
        # - Proper API integration
        # - Rate limiting

        logger.info("tiktok_adapter_fetch_complete", limit=limit)
        return
        yield  # Make this a generator

    def _normalize(self, raw_data: dict) -> NormalizedAd:
        """Normalize TikTok API response to NormalizedAd"""
        return NormalizedAd(
            creator_name=raw_data.get("advertiser_name", "Unknown"),
            creator_handle=raw_data.get("advertiser_id"),
            creator_avatar_url=raw_data.get("profile_image"),
            platform="tiktok",
            title=raw_data.get("ad_text"),
            description=raw_data.get("caption"),
            started_at=datetime.fromtimestamp(raw_data["create_time"]) if raw_data.get("create_time") else None,
            duration_seconds=raw_data.get("video_duration"),
            engagement_count=raw_data.get("engagement", 0),
            external_url=raw_data.get("click_url"),
            funnel_url=raw_data.get("landing_page_url"),
            thumb_url=raw_data.get("video_cover_url"),
            is_active=raw_data.get("status") == "ACTIVE"
        )

    async def close(self):
        """Clean up resources"""
        pass
