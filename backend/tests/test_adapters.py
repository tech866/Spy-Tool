"""
Tests for platform adapters
"""
import pytest
from app.adapters.base import NormalizedAd
from app.adapters.meta import MetaAdapter
from app.adapters.tiktok import TikTokAdapter
from app.adapters.youtube import YouTubeAdapter


@pytest.mark.asyncio
async def test_meta_adapter_interface():
    """Test Meta adapter implements correct interface"""
    adapter = MetaAdapter()
    assert adapter.name == "meta"
    assert hasattr(adapter, 'fetch')
    assert hasattr(adapter, 'close')


@pytest.mark.asyncio
async def test_tiktok_adapter_interface():
    """Test TikTok adapter implements correct interface"""
    adapter = TikTokAdapter()
    assert adapter.name == "tiktok"
    assert hasattr(adapter, 'fetch')
    assert hasattr(adapter, 'close')


@pytest.mark.asyncio
async def test_youtube_adapter_interface():
    """Test YouTube adapter implements correct interface"""
    adapter = YouTubeAdapter()
    assert adapter.name == "youtube"
    assert hasattr(adapter, 'fetch')
    assert hasattr(adapter, 'close')


def test_normalized_ad_validation():
    """Test NormalizedAd validation"""
    # Valid ad
    ad = NormalizedAd(
        creator_name="Test Creator",
        creator_handle="test_creator",
        platform="meta",
        title="Test Ad",
        description="Test description",
        is_active=True
    )
    assert ad.creator_name == "Test Creator"
    assert ad.platform == "meta"

    # Invalid platform should raise error
    with pytest.raises(ValueError):
        NormalizedAd(
            creator_name="Test Creator",
            platform="invalid_platform",  # Should fail validation
            title="Test Ad"
        )
