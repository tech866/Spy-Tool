"""
Pydantic schemas for API requests and responses
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime
from uuid import UUID


# Creator schemas
class CreatorBase(BaseModel):
    name: str
    avatar_url: Optional[str] = None
    source_handle: Optional[str] = None
    bio: Optional[str] = None


class CreatorCreate(CreatorBase):
    pass


class CreatorResponse(CreatorBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CreatorWithAds(CreatorResponse):
    tags: list[str] = []
    ad_count: int = 0


# Ad schemas
class AdBase(BaseModel):
    platform: str = Field(..., pattern="^(meta|tiktok|youtube)$")
    title: Optional[str] = None
    description: Optional[str] = None
    started_at: Optional[datetime] = None
    duration_seconds: Optional[int] = None
    engagement_count: int = 0
    external_url: Optional[str] = None
    funnel_url: Optional[str] = None
    thumb_url: Optional[str] = None
    is_active: bool = True


class AdCreate(AdBase):
    creator_id: UUID


class AdResponse(AdBase):
    id: UUID
    creator: CreatorResponse
    detected_at: datetime
    tags: list[str] = []

    model_config = ConfigDict(from_attributes=True)


# Tag schemas
class TagBase(BaseModel):
    name: str


class TagResponse(TagBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class TagUpdate(BaseModel):
    add: list[str] = []
    remove: list[str] = []


# Job schemas
class JobResponse(BaseModel):
    id: UUID
    job_type: str
    status: str
    started_at: datetime
    finished_at: Optional[datetime] = None
    meta: Optional[dict] = None

    model_config = ConfigDict(from_attributes=True)


# List responses
class CreatorListResponse(BaseModel):
    items: list[CreatorWithAds]
    total: int
    limit: int
    offset: int


class AdListResponse(BaseModel):
    items: list[AdResponse]
    total: int
    limit: int
    offset: int


class JobListResponse(BaseModel):
    items: list[JobResponse]
    total: int


# Health check
class HealthResponse(BaseModel):
    ok: bool
    version: str
    timestamp: datetime


# Import schema
class ImportRequest(BaseModel):
    creators: list[dict] = []
    ads: list[dict] = []
