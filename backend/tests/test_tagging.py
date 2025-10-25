"""
Tests for AI tagging service
"""
import pytest
from app.services.tagging import TaggingService


@pytest.mark.asyncio
async def test_heuristic_tagging_vsl():
    """Test VSL tag detection"""
    service = TaggingService()

    tags = await service.suggest_tags(
        title="Free Webinar: How to Scale Your Business",
        description="Join our video sales letter training",
        platform="meta"
    )

    assert "VSL" in tags
    assert "Webinar" in tags
    assert "Lead Generation" in tags


@pytest.mark.asyncio
async def test_heuristic_tagging_ecom():
    """Test Ecom tag detection"""
    service = TaggingService()

    tags = await service.suggest_tags(
        title="Build Your Shopify Store Today",
        description="Start dropshipping and make money with ecommerce",
        platform="meta"
    )

    assert "Ecom" in tags


@pytest.mark.asyncio
async def test_heuristic_tagging_coaching():
    """Test Coaching tag detection"""
    service = TaggingService()

    tags = await service.suggest_tags(
        title="1-on-1 Coaching Available",
        description="Transform your life with our mentorship program",
        platform="meta"
    )

    assert "Coaching" in tags
    assert "Mentorship" in tags


@pytest.mark.asyncio
async def test_heuristic_tagging_saas():
    """Test SaaS tag detection"""
    service = TaggingService()

    tags = await service.suggest_tags(
        title="All-in-One Marketing Automation Platform",
        description="Software that helps you scale your business",
        platform="meta"
    )

    assert "SaaS" in tags


@pytest.mark.asyncio
async def test_heuristic_tagging_ugc():
    """Test UGC tag detection"""
    service = TaggingService()

    tags = await service.suggest_tags(
        title="Real Customer Testimonial",
        description="See what our users are saying about us",
        platform="meta"
    )

    assert "UGC" in tags


@pytest.mark.asyncio
async def test_empty_text():
    """Test with empty text"""
    service = TaggingService()

    tags = await service.suggest_tags(
        title=None,
        description=None,
        platform="meta"
    )

    assert tags == []
