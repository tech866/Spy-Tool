/**
 * Home page: Search, filters, Creator Grid, Global Ad Feed
 */
'use client';

import { useState, useEffect } from 'react';
import SearchBar from '@/components/SearchBar';
import FiltersBar from '@/components/FiltersBar';
import CreatorCard from '@/components/CreatorCard';
import AdCard from '@/components/AdCard';
import EmptyState from '@/components/EmptyState';
import { api } from '@/lib/api';
import { CreatorWithAds, Ad, Platform, AdListResponse, CreatorListResponse } from '@/types';

export default function HomePage() {
  const [view, setView] = useState<'creators' | 'ads'>('creators');
  const [query, setQuery] = useState('');
  const [platform, setPlatform] = useState<Platform>('all');
  const [selectedTag, setSelectedTag] = useState<string | undefined>();

  const [creators, setCreators] = useState<CreatorWithAds[]>([]);
  const [ads, setAds] = useState<Ad[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Fetch data
  useEffect(() => {
    fetchData();
  }, [view, query, platform, selectedTag]);

  const fetchData = async () => {
    setLoading(true);
    setError(null);

    try {
      if (view === 'creators') {
        const response: CreatorListResponse = await api.getCreators({
          query: query || undefined,
          tag: selectedTag,
          limit: 50,
        });
        setCreators(response.items);
      } else {
        const response: AdListResponse = await api.getAds({
          query: query || undefined,
          platform: platform !== 'all' ? platform : undefined,
          tag: selectedTag,
          limit: 50,
        });
        setAds(response.items);
      }
    } catch (err: any) {
      setError(err.message || 'Failed to fetch data');
      console.error('Fetch error:', err);
    } finally {
      setLoading(false);
    }
  };

  // Get all unique tags from current data
  const allTags = view === 'creators'
    ? Array.from(new Set(creators.flatMap((c) => c.tags)))
    : Array.from(new Set(ads.flatMap((a) => a.tags)));

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Search */}
      <div className="mb-8">
        <SearchBar
          placeholder={
            view === 'creators'
              ? 'Search creators...'
              : 'Search ads by title or description...'
          }
          onSearch={setQuery}
        />
      </div>

      {/* View toggle */}
      <div className="flex gap-4 mb-6">
        <button
          onClick={() => setView('creators')}
          className={`px-6 py-3 rounded-xl font-medium transition ${
            view === 'creators'
              ? 'bg-primary text-white'
              : 'bg-card text-gray-400 hover:text-foreground'
          }`}
        >
          Creators
        </button>
        <button
          onClick={() => setView('ads')}
          className={`px-6 py-3 rounded-xl font-medium transition ${
            view === 'ads'
              ? 'bg-primary text-white'
              : 'bg-card text-gray-400 hover:text-foreground'
          }`}
        >
          Global Feed
        </button>
      </div>

      {/* Filters */}
      {view === 'ads' && (
        <div className="mb-8">
          <FiltersBar
            platform={platform}
            onPlatformChange={setPlatform}
            tags={allTags}
            selectedTag={selectedTag}
            onTagChange={setSelectedTag}
          />
        </div>
      )}

      {/* Results */}
      {loading ? (
        <div className="text-center py-16">
          <div className="inline-block w-8 h-8 border-4 border-primary border-t-transparent rounded-full animate-spin"></div>
          <p className="mt-4 text-gray-400">Loading...</p>
        </div>
      ) : error ? (
        <div className="text-center py-16">
          <p className="text-red-400">Error: {error}</p>
          <button
            onClick={fetchData}
            className="mt-4 px-6 py-2 bg-primary text-white rounded-lg hover:bg-primary/90 transition"
          >
            Retry
          </button>
        </div>
      ) : (
        <>
          {view === 'creators' ? (
            creators.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {creators.map((creator) => (
                  <CreatorCard key={creator.id} creator={creator} />
                ))}
              </div>
            ) : (
              <EmptyState
                title="No creators found"
                description="Try adjusting your search or filters"
              />
            )
          ) : ads.length > 0 ? (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {ads.map((ad) => (
                <AdCard key={ad.id} ad={ad} onTagClick={setSelectedTag} />
              ))}
            </div>
          ) : (
            <EmptyState
              title="No ads found"
              description="Try adjusting your search or filters"
            />
          )}
        </>
      )}
    </div>
  );
}
