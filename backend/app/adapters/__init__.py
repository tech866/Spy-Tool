"""
Platform adapters for ad ingestion
"""
from .base import Adapter, NormalizedAd
from .meta import MetaAdapter
from .tiktok import TikTokAdapter
from .youtube import YouTubeAdapter

__all__ = [
    "Adapter",
    "NormalizedAd",
    "MetaAdapter",
    "TikTokAdapter",
    "YouTubeAdapter"
]
