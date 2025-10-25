/**
 * Ad card component
 */
'use client';

import { Ad } from '@/types';
import Tag from './Tag';
import { formatRelativeTime, formatDuration, getPlatformColor, getPlatformLabel } from '@/lib/utils';

interface AdCardProps {
  ad: Ad;
  onTagClick?: (tag: string) => void;
}

export default function AdCard({ ad, onTagClick }: AdCardProps) {
  return (
    <div className="p-6 bg-card border border-border rounded-2xl hover:border-primary/30 transition">
      {/* Header */}
      <div className="flex items-start justify-between gap-4 mb-4">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-2">
            <span className={`px-2 py-1 rounded text-xs font-medium text-white ${getPlatformColor(ad.platform)}`}>
              {getPlatformLabel(ad.platform)}
            </span>
            {ad.is_active && (
              <span className="px-2 py-1 rounded text-xs font-medium bg-green-500/20 text-green-400">
                Active
              </span>
            )}
          </div>

          <h3 className="text-lg font-semibold text-foreground mb-1 line-clamp-2">
            {ad.title || 'Untitled Ad'}
          </h3>

          <p className="text-sm text-gray-400">
            by {ad.creator.name}
          </p>
        </div>

        {/* Thumbnail */}
        {ad.thumb_url && (
          <div className="w-24 h-24 rounded-lg overflow-hidden bg-card flex-shrink-0">
            <img
              src={ad.thumb_url}
              alt={ad.title || 'Ad thumbnail'}
              className="w-full h-full object-cover"
            />
          </div>
        )}
      </div>

      {/* Description */}
      {ad.description && (
        <p className="text-sm text-gray-300 mb-4 line-clamp-3">{ad.description}</p>
      )}

      {/* Tags */}
      {ad.tags.length > 0 && (
        <div className="flex flex-wrap gap-2 mb-4">
          {ad.tags.map((tag) => (
            <Tag
              key={tag}
              name={tag}
              clickable={!!onTagClick}
              onClick={() => onTagClick?.(tag)}
            />
          ))}
        </div>
      )}

      {/* Meta info */}
      <div className="flex items-center gap-4 text-xs text-gray-400 mb-4">
        {ad.started_at && <span>{formatRelativeTime(ad.started_at)}</span>}
        {ad.duration_seconds && <span>{formatDuration(ad.duration_seconds)}</span>}
        {ad.engagement_count > 0 && <span>{ad.engagement_count.toLocaleString()} engagements</span>}
      </div>

      {/* Actions */}
      <div className="flex gap-3">
        {ad.funnel_url && (
          <a
            href={ad.funnel_url}
            target="_blank"
            rel="noopener noreferrer"
            className="flex-1 px-4 py-2 bg-primary text-white text-sm font-medium rounded-lg hover:bg-primary/90 transition text-center"
          >
            Go to Funnel
          </a>
        )}
        {ad.external_url && (
          <a
            href={ad.external_url}
            target="_blank"
            rel="noopener noreferrer"
            className="flex-1 px-4 py-2 bg-card border border-border text-foreground text-sm font-medium rounded-lg hover:border-primary/50 transition text-center"
          >
            View Live Ad
          </a>
        )}
      </div>
    </div>
  );
}
