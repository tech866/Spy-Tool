"""
Admin endpoints for ingestion and import
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
from uuid import uuid4

from ..core.database import get_db
from ..models.models import Creator, Ad, Tag, AdTag, Job
from .schemas import ImportRequest, JobResponse
from ..services.ingestion import run_ingestion_pipeline

router = APIRouter(prefix="/ingest", tags=["admin"])


@router.post("/run", response_model=JobResponse)
async def trigger_ingestion(
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    Trigger ingestion pipeline for all enabled adapters
    Runs asynchronously in background
    """
    # Create job record
    job = Job(
        id=uuid4(),
        job_type="ingest_all",
        status="queued",
        started_at=datetime.utcnow(),
        meta={"triggered_by": "api"}
    )
    db.add(job)
    await db.commit()
    await db.refresh(job)

    # Schedule background task
    background_tasks.add_task(run_ingestion_pipeline, str(job.id))

    return JobResponse.model_validate(job)


@router.post("/import", response_model=dict)
async def import_data(
    data: ImportRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Import creators and ads from JSON dump
    Useful for seeding demo data
    """
    imported_creators = 0
    imported_ads = 0

    try:
        # Import creators
        for creator_data in data.creators:
            # Check if creator exists by name/handle
            name = creator_data.get("name")
            handle = creator_data.get("source_handle")

            stmt = select(Creator).where(Creator.name == name)
            if handle:
                stmt = stmt.where(Creator.source_handle == handle)

            result = await db.execute(stmt)
            existing = result.scalar_one_or_none()

            if not existing:
                creator = Creator(
                    name=name,
                    avatar_url=creator_data.get("avatar_url"),
                    source_handle=handle,
                    bio=creator_data.get("bio")
                )
                db.add(creator)
                imported_creators += 1
            else:
                creator = existing

            await db.flush()

        # Import ads
        for ad_data in data.ads:
            # Find creator by name
            creator_name = ad_data.get("creator_name")
            creator_stmt = select(Creator).where(Creator.name == creator_name)
            creator_result = await db.execute(creator_stmt)
            creator = creator_result.scalar_one_or_none()

            if not creator:
                continue  # Skip ads for unknown creators

            # Check if ad exists by external_url
            external_url = ad_data.get("external_url")
            if external_url:
                ad_stmt = select(Ad).where(Ad.external_url == external_url)
                ad_result = await db.execute(ad_stmt)
                existing_ad = ad_result.scalar_one_or_none()

                if existing_ad:
                    continue  # Skip duplicate

            # Create ad
            ad = Ad(
                creator_id=creator.id,
                platform=ad_data.get("platform", "meta"),
                title=ad_data.get("title"),
                description=ad_data.get("description"),
                started_at=ad_data.get("started_at"),
                duration_seconds=ad_data.get("duration_seconds"),
                engagement_count=ad_data.get("engagement_count", 0),
                external_url=external_url,
                funnel_url=ad_data.get("funnel_url"),
                thumb_url=ad_data.get("thumb_url"),
                is_active=ad_data.get("is_active", True)
            )
            db.add(ad)
            await db.flush()

            # Add tags
            tag_names = ad_data.get("tags", [])
            for tag_name in tag_names:
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

            imported_ads += 1

        await db.commit()

        return {
            "success": True,
            "imported_creators": imported_creators,
            "imported_ads": imported_ads
        }

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Import failed: {str(e)}")
