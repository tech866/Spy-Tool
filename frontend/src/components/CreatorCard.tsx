/**
 * Creator card component
 */
'use client';

import Link from 'next/link';
import { CreatorWithAds } from '@/types';
import Tag from './Tag';

interface CreatorCardProps {
  creator: CreatorWithAds;
}

export default function CreatorCard({ creator }: CreatorCardProps) {
  return (
    <Link href={`/creator/${creator.id}`}>
      <div className="group p-6 bg-card border border-border rounded-2xl hover:border-primary/50 transition cursor-pointer">
        <div className="flex items-start gap-4">
          {/* Avatar */}
          <div className="w-16 h-16 rounded-full bg-gradient-to-br from-primary to-secondary flex items-center justify-center text-2xl font-bold flex-shrink-0">
            {creator.avatar_url ? (
              <img
                src={creator.avatar_url}
                alt={creator.name}
                className="w-full h-full rounded-full object-cover"
              />
            ) : (
              creator.name.charAt(0).toUpperCase()
            )}
          </div>

          {/* Content */}
          <div className="flex-1 min-w-0">
            <h3 className="text-lg font-semibold text-foreground group-hover:text-primary transition truncate">
              {creator.name}
            </h3>
            {creator.source_handle && (
              <p className="text-sm text-gray-400 truncate">@{creator.source_handle}</p>
            )}

            {/* Stats */}
            <div className="mt-2 flex items-center gap-4 text-sm text-gray-400">
              <span>{creator.ad_count} ads</span>
            </div>

            {/* Tags */}
            {creator.tags.length > 0 && (
              <div className="mt-3 flex flex-wrap gap-2">
                {creator.tags.slice(0, 3).map((tag) => (
                  <Tag key={tag} name={tag} />
                ))}
                {creator.tags.length > 3 && (
                  <span className="text-xs text-gray-400 self-center">
                    +{creator.tags.length - 3} more
                  </span>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </Link>
  );
}
