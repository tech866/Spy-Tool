/**
 * Filters bar component
 */
'use client';

import { Platform } from '@/types';

interface FiltersBarProps {
  platform: Platform;
  onPlatformChange: (platform: Platform) => void;
  tags?: string[];
  selectedTag?: string;
  onTagChange?: (tag: string | undefined) => void;
}

export default function FiltersBar({
  platform,
  onPlatformChange,
  tags = [],
  selectedTag,
  onTagChange,
}: FiltersBarProps) {
  const platforms: Platform[] = ['all', 'meta', 'tiktok', 'youtube'];

  return (
    <div className="flex flex-col gap-4">
      {/* Platform filter */}
      <div className="flex gap-2">
        <span className="text-sm text-gray-400 mr-2 self-center">Platform:</span>
        {platforms.map((p) => (
          <button
            key={p}
            onClick={() => onPlatformChange(p)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition ${
              platform === p
                ? 'bg-primary text-white'
                : 'bg-card text-gray-400 hover:text-foreground'
            }`}
          >
            {p === 'all' ? 'All' : p.charAt(0).toUpperCase() + p.slice(1)}
          </button>
        ))}
      </div>

      {/* Tag filter */}
      {tags.length > 0 && onTagChange && (
        <div className="flex gap-2 flex-wrap">
          <span className="text-sm text-gray-400 mr-2 self-center">Tags:</span>
          <button
            onClick={() => onTagChange(undefined)}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition ${
              !selectedTag
                ? 'bg-primary text-white'
                : 'bg-card text-gray-400 hover:text-foreground'
            }`}
          >
            All
          </button>
          {tags.map((tag) => (
            <button
              key={tag}
              onClick={() => onTagChange(tag)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition ${
                selectedTag === tag
                  ? 'bg-primary text-white'
                  : 'bg-card text-gray-400 hover:text-foreground'
              }`}
            >
              {tag}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
