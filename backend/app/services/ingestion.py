"""
Ingestion pipeline orchestrator
"""
import structlog
from datetime import datetime
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import select

from ..core.config import settings
from ..core.database import AsyncSessionLocal
from ..models.models import Creator, Ad, Tag, AdTag, Job
from ..adapters import MetaAdapter, TikTokAdapter, YouTubeAdapter
from ..services.tagging import TaggingService
from ..services.storage import StorageService

logger = structlog.get_logger()


async def run_ingestion_pipeline(job_id: str):
    """
    Run the full ingestion pipeline for all enabled adapters

    Args:
        job_id: Job UUID to track progress
    """
    logger.info("ingestion_pipeline_start", job_id=job_id)

    # Create fresh DB session for this background task
    async with AsyncSessionLocal() as db:
        # Update job status
        job_stmt = select(Job).where(Job.id == job_id)
        job_result = await db.execute(job_stmt)
        job = job_result.scalar_one_or_none()

        if not job:
            logger.error("ingestion_job_not_found", job_id=job_id)
            return

        job.status = "running"
        await db.commit()

        try:
            # Initialize services
            tagging_service = TaggingService()
            storage_service = StorageService()

            # Track stats
            stats = {
                "meta": 0,
                "tiktok": 0,
                "youtube": 0,
                "total": 0,
                "errors": []
            }

            # Run adapters
            adapters = []

            if settings.ENABLE_META_ADAPTER:
                adapters.append(("meta", MetaAdapter()))

            if settings.ENABLE_TIKTOK_ADAPTER:
                adapters.append(("tiktok", TikTokAdapter()))

            if settings.ENABLE_YOUTUBE_ADAPTER:
                adapters.append(("youtube", YouTubeAdapter()))

            for platform, adapter in adapters:
                try:
                    count = await ingest_from_adapter(
                        adapter,
                        db,
                        tagging_service,
                        storage_service
                    )
                    stats[platform] = count
                    stats["total"] += count
                    logger.info("adapter_ingest_complete", platform=platform, count=count)

                except Exception as e:
                    error_msg = f"{platform}: {str(e)}"
                    stats["errors"].append(error_msg)
                    logger.error("adapter_ingest_failed", platform=platform, error=str(e))

                finally:
                    await adapter.close()

            # Update job as success
            job.status = "success"
            job.finished_at = datetime.utcnow()
            job.meta = stats
            await db.commit()

            logger.info("ingestion_pipeline_complete", job_id=job_id, stats=stats)

        except Exception as e:
            # Update job as failed
            job.status = "failed"
            job.finished_at = datetime.utcnow()
            job.meta = {"error": str(e)}
            await db.commit()

            logger.error("ingestion_pipeline_failed", job_id=job_id, error=str(e))


async def ingest_from_adapter(
    adapter,
    db: AsyncSession,
    tagging_service: TaggingService,
    storage_service: StorageService
) -> int:
    """
    Ingest ads from a single adapter

    Args:
        adapter: Platform adapter instance
        db: Database session
        tagging_service: AI tagging service
        storage_service: S3 storage service

    Returns:
        Number of ads ingested
    """
    count = 0

    async for normalized_ad in adapter.fetch(limit=settings.INGEST_MAX_ADS_PER_RUN):
        try:
            # Get or create creator
            creator_stmt = select(Creator).where(Creator.name == normalized_ad.creator_name)
            creator_result = await db.execute(creator_stmt)
            creator = creator_result.scalar_one_or_none()

            if not creator:
                creator = Creator(
                    name=normalized_ad.creator_name,
                    source_handle=normalized_ad.creator_handle,
                    avatar_url=normalized_ad.creator_avatar_url
                )
                db.add(creator)
                await db.flush()

            # Check if ad already exists (by external_url)
            if normalized_ad.external_url:
                ad_stmt = select(Ad).where(Ad.external_url == normalized_ad.external_url)
                ad_result = await db.execute(ad_stmt)
                existing_ad = ad_result.scalar_one_or_none()

                if existing_ad:
                    continue  # Skip duplicate

            # Create ad
            ad = Ad(
                creator_id=creator.id,
                platform=normalized_ad.platform,
                title=normalized_ad.title,
                description=normalized_ad.description,
                started_at=normalized_ad.started_at,
                duration_seconds=normalized_ad.duration_seconds,
                engagement_count=normalized_ad.engagement_count,
                external_url=normalized_ad.external_url,
                funnel_url=normalized_ad.funnel_url,
                thumb_url=normalized_ad.thumb_url,
                is_active=normalized_ad.is_active
            )
            db.add(ad)
            await db.flush()

            # AI tagging
            suggested_tags = await tagging_service.suggest_tags(
                normalized_ad.title,
                normalized_ad.description,
                normalized_ad.platform
            )

            for tag_name in suggested_tags:
                # Get or create tag
                tag_stmt = select(Tag).where(Tag.name == tag_name)
                tag_result = await db.execute(tag_stmt)
                tag = tag_result.scalar_one_or_none()

                if not tag:
                    tag = Tag(name=tag_name)
                    db.add(tag)
                    await db.flush()

                # Create ad_tag relation
                ad_tag = AdTag(ad_id=ad.id, tag_id=tag.id)
                db.add(ad_tag)

            await db.commit()
            count += 1

        except Exception as e:
            logger.error("ad_ingest_failed", error=str(e), ad=normalized_ad.dict())
            await db.rollback()
            continue

    return count
