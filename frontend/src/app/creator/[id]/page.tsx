/**
 * Creator detail page: Profile, Active Ads, CTAs
 */
'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import AdCard from '@/components/AdCard';
import EmptyState from '@/components/EmptyState';
import Tag from '@/components/Tag';
import { api } from '@/lib/api';
import { CreatorWithAds, Ad, AdListResponse } from '@/types';

export default function CreatorDetailPage() {
  const params = useParams();
  const router = useRouter();
  const creatorId = params.id as string;

  const [creator, setCreator] = useState<CreatorWithAds | null>(null);
  const [ads, setAds] = useState<Ad[]>([]);
  const [platformFilter, setPlatformFilter] = useState<string | undefined>();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchCreatorData();
  }, [creatorId, platformFilter]);

  const fetchCreatorData = async () => {
    setLoading(true);
    setError(null);

    try {
      // Fetch creator info
      const creatorData: CreatorWithAds = await api.getCreator(creatorId);
      setCreator(creatorData);

      // Fetch creator's ads
      const adsData: AdListResponse = await api.getCreatorAds(creatorId, {
        platform: platformFilter,
        active: true,
        limit: 100,
      });
      setAds(adsData.items);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch creator data');
      console.error('Fetch error:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-16 text-center">
        <div className="inline-block w-8 h-8 border-4 border-primary border-t-transparent rounded-full animate-spin"></div>
        <p className="mt-4 text-gray-400">Loading...</p>
      </div>
    );
  }

  if (error || !creator) {
    return (
      <div className="container mx-auto px-4 py-16 text-center">
        <p className="text-red-400">Error: {error || 'Creator not found'}</p>
        <button
          onClick={() => router.push('/')}
          className="mt-4 px-6 py-2 bg-primary text-white rounded-lg hover:bg-primary/90 transition"
        >
          Back to Home
        </button>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Back button */}
      <button
        onClick={() => router.push('/')}
        className="mb-6 text-sm text-gray-400 hover:text-foreground transition flex items-center gap-2"
      >
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
        </svg>
        Back to Home
      </button>

      {/* Creator profile */}
      <div className="bg-card border border-border rounded-2xl p-8 mb-8">
        <div className="flex items-start gap-6">
          {/* Avatar */}
          <div className="w-24 h-24 rounded-full bg-gradient-to-br from-primary to-secondary flex items-center justify-center text-3xl font-bold flex-shrink-0">
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

          {/* Info */}
          <div className="flex-1">
            <h1 className="text-3xl font-bold text-foreground mb-2">{creator.name}</h1>

            {creator.source_handle && (
              <p className="text-lg text-gray-400 mb-4">@{creator.source_handle}</p>
            )}

            {creator.bio && (
              <p className="text-gray-300 mb-4">{creator.bio}</p>
            )}

            {/* Stats */}
            <div className="flex items-center gap-6 text-sm text-gray-400 mb-4">
              <span className="font-medium">{creator.ad_count} total ads</span>
              <span>•</span>
              <span>{ads.length} active ads</span>
            </div>

            {/* Tags */}
            {creator.tags.length > 0 && (
              <div className="flex flex-wrap gap-2">
                {creator.tags.map((tag) => (
                  <Tag key={tag} name={tag} />
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Platform filter */}
      <div className="mb-6">
        <div className="flex gap-2">
          <span className="text-sm text-gray-400 mr-2 self-center">Filter by platform:</span>
          <button
            onClick={() => setPlatformFilter(undefined)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition ${
              !platformFilter
                ? 'bg-primary text-white'
                : 'bg-card text-gray-400 hover:text-foreground'
            }`}
          >
            All
          </button>
          {['meta', 'tiktok', 'youtube'].map((p) => (
            <button
              key={p}
              onClick={() => setPlatformFilter(p)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition ${
                platformFilter === p
                  ? 'bg-primary text-white'
                  : 'bg-card text-gray-400 hover:text-foreground'
              }`}
            >
              {p.charAt(0).toUpperCase() + p.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {/* Active ads */}
      <div>
        <h2 className="text-2xl font-bold text-foreground mb-6">Active Ads</h2>

        {ads.length > 0 ? (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {ads.map((ad) => (
              <AdCard key={ad.id} ad={ad} />
            ))}
          </div>
        ) : (
          <EmptyState
            title="No active ads found"
            description={
              platformFilter
                ? `No active ads on ${platformFilter} for this creator`
                : 'This creator has no active ads at the moment'
            }
          />
        )}
      </div>
    </div>
  );
}
