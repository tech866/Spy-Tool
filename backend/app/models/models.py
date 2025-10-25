"""
SQLAlchemy models matching the spec schema
"""
import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Text, Integer, Boolean, DateTime, ForeignKey,
    CheckConstraint, Index, JSON
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from ..core.database import Base


class Creator(Base):
    __tablename__ = "creators"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(Text, nullable=False)
    avatar_url = Column(Text, nullable=True)
    source_handle = Column(Text, nullable=True)
    bio = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    ads = relationship("Ad", back_populates="creator", cascade="all, delete-orphan")

    __table_args__ = (
        Index('idx_creators_name', 'name', postgresql_using='gin', postgresql_ops={'name': 'gin_trgm_ops'}),
    )


class Ad(Base):
    __tablename__ = "ads"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    creator_id = Column(UUID(as_uuid=True), ForeignKey('creators.id', ondelete='CASCADE'), nullable=False)
    platform = Column(Text, CheckConstraint("platform IN ('meta', 'tiktok', 'youtube')"), nullable=False)
    title = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    detected_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    duration_seconds = Column(Integer, nullable=True)
    engagement_count = Column(Integer, default=0, nullable=False)
    external_url = Column(Text, nullable=True)
    funnel_url = Column(Text, nullable=True)
    thumb_url = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

    # Relationships
    creator = relationship("Creator", back_populates="ads")
    ad_tags = relationship("AdTag", back_populates="ad", cascade="all, delete-orphan")

    __table_args__ = (
        Index('idx_ads_platform', 'platform'),
        Index('idx_ads_detected_at', 'detected_at'),
        Index('idx_ads_text',
              'title', 'description',
              postgresql_using='gin',
              postgresql_ops={'title': 'gin_trgm_ops', 'description': 'gin_trgm_ops'}),
    )


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Text, unique=True, nullable=False)

    # Relationships
    ad_tags = relationship("AdTag", back_populates="tag", cascade="all, delete-orphan")


class AdTag(Base):
    __tablename__ = "ad_tags"

    ad_id = Column(UUID(as_uuid=True), ForeignKey('ads.id', ondelete='CASCADE'), primary_key=True)
    tag_id = Column(Integer, ForeignKey('tags.id', ondelete='CASCADE'), primary_key=True)

    # Relationships
    ad = relationship("Ad", back_populates="ad_tags")
    tag = relationship("Tag", back_populates="ad_tags")


class Job(Base):
    __tablename__ = "jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_type = Column(Text, nullable=False)  # 'ingest_meta', 'ingest_tiktok', 'thumb_snap'
    status = Column(Text, nullable=False, default='queued')  # 'queued', 'running', 'success', 'failed'
    started_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    finished_at = Column(DateTime(timezone=True), nullable=True)
    meta = Column(JSON, nullable=True)

    __table_args__ = (
        Index('idx_jobs_status', 'status'),
        Index('idx_jobs_started_at', 'started_at'),
    )
