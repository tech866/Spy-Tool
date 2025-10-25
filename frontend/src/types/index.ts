/**
 * TypeScript types matching backend API schemas
 */

export interface Creator {
  id: string;
  name: string;
  avatar_url?: string;
  source_handle?: string;
  bio?: string;
  created_at: string;
  updated_at: string;
}

export interface CreatorWithAds extends Creator {
  tags: string[];
  ad_count: number;
}

export interface Ad {
  id: string;
  creator: Creator;
  platform: 'meta' | 'tiktok' | 'youtube';
  title?: string;
  description?: string;
  started_at?: string;
  detected_at: string;
  duration_seconds?: number;
  engagement_count: number;
  external_url?: string;
  funnel_url?: string;
  thumb_url?: string;
  is_active: boolean;
  tags: string[];
}

export interface CreatorListResponse {
  items: CreatorWithAds[];
  total: number;
  limit: number;
  offset: number;
}

export interface AdListResponse {
  items: Ad[];
  total: number;
  limit: number;
  offset: number;
}

export interface Job {
  id: string;
  job_type: string;
  status: 'queued' | 'running' | 'success' | 'failed';
  started_at: string;
  finished_at?: string;
  meta?: any;
}

export type Platform = 'meta' | 'tiktok' | 'youtube' | 'all';

export interface FilterState {
  query: string;
  platform: Platform;
  tag?: string;
  since?: string;
  until?: string;
}
