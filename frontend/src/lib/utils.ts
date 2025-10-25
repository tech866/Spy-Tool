/**
 * Utility functions
 */
import clsx, { ClassValue } from 'clsx';
import { format, formatDistanceToNow } from 'date-fns';

export function cn(...inputs: ClassValue[]) {
  return clsx(inputs);
}

export function formatDate(date: string | Date): string {
  const d = typeof date === 'string' ? new Date(date) : date;
  return format(d, 'MMM d, yyyy');
}

export function formatRelativeTime(date: string | Date): string {
  const d = typeof date === 'string' ? new Date(date) : date;
  return formatDistanceToNow(d, { addSuffix: true });
}

export function formatDuration(seconds?: number): string {
  if (!seconds) return 'N/A';

  const mins = Math.floor(seconds / 60);
  const secs = seconds % 60;

  if (mins === 0) return `${secs}s`;
  if (secs === 0) return `${mins}m`;
  return `${mins}m ${secs}s`;
}

export function getPlatformColor(platform: string): string {
  switch (platform) {
    case 'meta':
      return 'bg-blue-500';
    case 'tiktok':
      return 'bg-pink-500';
    case 'youtube':
      return 'bg-red-500';
    default:
      return 'bg-gray-500';
  }
}

export function getPlatformLabel(platform: string): string {
  switch (platform) {
    case 'meta':
      return 'Meta';
    case 'tiktok':
      return 'TikTok';
    case 'youtube':
      return 'YouTube';
    default:
      return platform;
  }
}
