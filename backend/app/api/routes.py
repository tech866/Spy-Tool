"""
FastAPI routes and endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, and_
from typing import Optional
from datetime import datetime
from uuid import UUID

from ..core.database import get_db
from ..core.config import settings
from ..models.models import Creator, Ad, Tag, AdTag, Job
from .schemas import (
    HealthResponse, CreatorListResponse, CreatorResponse, CreatorWithAds,
    AdListResponse, AdResponse, TagUpdate, JobListResponse, JobResponse,
    ImportRequest
)

router = APIRouter()


@router.get("/healthz", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        ok=True,
        version=settings.VERSION,
        timestamp=datetime.utcnow()
    )


@router.get("/creators", response_model=CreatorListResponse)
async def list_creators(
    query: Optional[str] = None,
    tag: Optional[str] = None,
    limit: int = Query(default=50, le=200),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    """List creators with optional filtering"""
    # Build query
    stmt = select(Creator)

    # Text search on name
    if query:
        stmt = stmt.where(Creator.name.ilike(f"%{query}%"))

    # Filter by tag
    if tag:
        stmt = stmt.join(Ad).join(AdTag).join(Tag).where(Tag.name == tag).distinct()

    # Count total
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = await db.scalar(count_stmt)

    # Get paginated results
    stmt = stmt.limit(limit).offset(offset).order_by(Creator.created_at.desc())
    result = await db.execute(stmt)
    creators = result.scalars().all()

    # Enrich with tags and ad count
    items = []
    for creator in creators:
        # Get tags for this creator
        tag_stmt = select(Tag.name).join(AdTag).join(Ad).where(
            Ad.creator_id == creator.id
        ).distinct()
        tag_result = await db.execute(tag_stmt)
        tags = [row[0] for row in tag_result]

        # Get ad count
        ad_count_stmt = select(func.count(Ad.id)).where(Ad.creator_id == creator.id)
        ad_count = await db.scalar(ad_count_stmt)

        items.append(CreatorWithAds(
            id=creator.id,
            name=creator.name,
            avatar_url=creator.avatar_url,
            source_handle=creator.source_handle,
            bio=creator.bio,
            created_at=creator.created_at,
            updated_at=creator.updated_at,
            tags=tags,
            ad_count=ad_count or 0
        ))

    return CreatorListResponse(
        items=items,
        total=total or 0,
        limit=limit,
        offset=offset
    )


@router.get("/creators/{creator_id}", response_model=CreatorWithAds)
async def get_creator(
    creator_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get creator by ID with aggregated tags"""
    stmt = select(Creator).where(Creator.id == creator_id)
    result = await db.execute(stmt)
    creator = result.scalar_one_or_none()

    if not creator:
        raise HTTPException(status_code=404, detail="Creator not found")

    # Get tags
    tag_stmt = select(Tag.name).join(AdTag).join(Ad).where(
        Ad.creator_id == creator.id
    ).distinct()
    tag_result = await db.execute(tag_stmt)
    tags = [row[0] for row in tag_result]

    # Get ad count
    ad_count_stmt = select(func.count(Ad.id)).where(Ad.creator_id == creator.id)
    ad_count = await db.scalar(ad_count_stmt)

    return CreatorWithAds(
        id=creator.id,
        name=creator.name,
        avatar_url=creator.avatar_url,
        source_handle=creator.source_handle,
        bio=creator.bio,
        created_at=creator.created_at,
        updated_at=creator.updated_at,
        tags=tags,
        ad_count=ad_count or 0
    )


@router.get("/creators/{creator_id}/ads", response_model=AdListResponse)
async def get_creator_ads(
    creator_id: UUID,
    platform: Optional[str] = None,
    active: Optional[bool] = None,
    since: Optional[datetime] = None,
    until: Optional[datetime] = None,
    limit: int = Query(default=50, le=200),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    """Get ads for a specific creator"""
    # Verify creator exists
    creator_stmt = select(Creator).where(Creator.id == creator_id)
    creator_result = await db.execute(creator_stmt)
    creator = creator_result.scalar_one_or_none()

    if not creator:
        raise HTTPException(status_code=404, detail="Creator not found")

    # Build query
    stmt = select(Ad).where(Ad.creator_id == creator_id)

    if platform:
        stmt = stmt.where(Ad.platform == platform)
    if active is not None:
        stmt = stmt.where(Ad.is_active == active)
    if since:
        stmt = stmt.where(Ad.detected_at >= since)
    if until:
        stmt = stmt.where(Ad.detected_at <= until)

    # Count total
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = await db.scalar(count_stmt)

    # Get paginated results
    stmt = stmt.limit(limit).offset(offset).order_by(Ad.detected_at.desc())
    result = await db.execute(stmt)
    ads = result.scalars().all()

    # Enrich with creator and tags
    items = await _enrich_ads(ads, db)

    return AdListResponse(
        items=items,
        total=total or 0,
        limit=limit,
        offset=offset
    )


@router.get("/ads", response_model=AdListResponse)
async def list_ads(
    query: Optional[str] = None,
    platform: Optional[str] = None,
    tag: Optional[str] = None,
    since: Optional[datetime] = None,
    until: Optional[datetime] = None,
    limit: int = Query(default=50, le=200),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    """Global ad feed with filtering"""
    # Build query
    stmt = select(Ad)

    # Text search
    if query:
        stmt = stmt.where(
            or_(
                Ad.title.ilike(f"%{query}%"),
                Ad.description.ilike(f"%{query}%")
            )
        )

    # Filter by platform
    if platform:
        stmt = stmt.where(Ad.platform == platform)

    # Filter by tag
    if tag:
        stmt = stmt.join(AdTag).join(Tag).where(Tag.name == tag)

    # Filter by date range
    if since:
        stmt = stmt.where(Ad.detected_at >= since)
    if until:
        stmt = stmt.where(Ad.detected_at <= until)

    # Count total
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = await db.scalar(count_stmt)

    # Get paginated results
    stmt = stmt.limit(limit).offset(offset).order_by(Ad.detected_at.desc())
    result = await db.execute(stmt)
    ads = result.scalars().all()

    # Enrich with creator and tags
    items = await _enrich_ads(ads, db)

    return AdListResponse(
        items=items,
        total=total or 0,
        limit=limit,
        offset=offset
    )


@router.post("/ads/{ad_id}/tags")
async def update_ad_tags(
    ad_id: UUID,
    tag_update: TagUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Add or remove tags from an ad"""
    # Verify ad exists
    ad_stmt = select(Ad).where(Ad.id == ad_id)
    ad_result = await db.execute(ad_stmt)
    ad = ad_result.scalar_one_or_none()

    if not ad:
        raise HTTPException(status_code=404, detail="Ad not found")

    # Add tags
    for tag_name in tag_update.add:
        # Get or create tag
        tag_stmt = select(Tag).where(Tag.name == tag_name)
        tag_result = await db.execute(tag_stmt)
        tag = tag_result.scalar_one_or_none()

        if not tag:
            tag = Tag(name=tag_name)
            db.add(tag)
            await db.flush()

        # Check if relation exists
        ad_tag_stmt = select(AdTag).where(
            and_(AdTag.ad_id == ad_id, AdTag.tag_id == tag.id)
        )
        ad_tag_result = await db.execute(ad_tag_stmt)
        existing = ad_tag_result.scalar_one_or_none()

        if not existing:
            ad_tag = AdTag(ad_id=ad_id, tag_id=tag.id)
            db.add(ad_tag)

    # Remove tags
    for tag_name in tag_update.remove:
        tag_stmt = select(Tag).where(Tag.name == tag_name)
        tag_result = await db.execute(tag_stmt)
        tag = tag_result.scalar_one_or_none()

        if tag:
            ad_tag_stmt = select(AdTag).where(
                and_(AdTag.ad_id == ad_id, AdTag.tag_id == tag.id)
            )
            ad_tag_result = await db.execute(ad_tag_stmt)
            ad_tag = ad_tag_result.scalar_one_or_none()

            if ad_tag:
                await db.delete(ad_tag)

    await db.commit()

    # Return updated tags
    tag_stmt = select(Tag.name).join(AdTag).where(AdTag.ad_id == ad_id)
    tag_result = await db.execute(tag_stmt)
    tags = [row[0] for row in tag_result]

    return {"tags": tags}


@router.get("/jobs", response_model=JobListResponse)
async def list_jobs(
    limit: int = Query(default=50, le=200),
    db: AsyncSession = Depends(get_db)
):
    """List recent jobs"""
    stmt = select(Job).order_by(Job.started_at.desc()).limit(limit)
    result = await db.execute(stmt)
    jobs = result.scalars().all()

    return JobListResponse(
        items=[JobResponse.model_validate(job) for job in jobs],
        total=len(jobs)
    )


@router.get("/jobs/{job_id}", response_model=JobResponse)
async def get_job(
    job_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get job status by ID"""
    stmt = select(Job).where(Job.id == job_id)
    result = await db.execute(stmt)
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return JobResponse.model_validate(job)


# Helper function to enrich ads with creator and tags
async def _enrich_ads(ads: list[Ad], db: AsyncSession) -> list[AdResponse]:
    """Enrich ads with creator info and tags"""
    items = []

    for ad in ads:
        # Get creator
        creator_stmt = select(Creator).where(Creator.id == ad.creator_id)
        creator_result = await db.execute(creator_stmt)
        creator = creator_result.scalar_one()

        # Get tags
        tag_stmt = select(Tag.name).join(AdTag).where(AdTag.ad_id == ad.id)
        tag_result = await db.execute(tag_stmt)
        tags = [row[0] for row in tag_result]

        items.append(AdResponse(
            id=ad.id,
            creator=CreatorResponse.model_validate(creator),
            platform=ad.platform,
            title=ad.title,
            description=ad.description,
            started_at=ad.started_at,
            detected_at=ad.detected_at,
            duration_seconds=ad.duration_seconds,
            engagement_count=ad.engagement_count,
            external_url=ad.external_url,
            funnel_url=ad.funnel_url,
            thumb_url=ad.thumb_url,
            is_active=ad.is_active,
            tags=tags
        ))

    return items
