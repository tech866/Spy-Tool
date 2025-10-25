/**
 * API client for backend communication
 */

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export async function fetchAPI<T>(
  endpoint: string,
  options?: RequestInit
): Promise<T> {
  const url = `${API_URL}${endpoint}`;

  const response = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  });

  if (!response.ok) {
    throw new Error(`API error: ${response.status} ${response.statusText}`);
  }

  return response.json();
}

export const api = {
  // Health check
  healthCheck: () => fetchAPI('/healthz'),

  // Creators
  getCreators: (params?: {
    query?: string;
    tag?: string;
    limit?: number;
    offset?: number;
  }) => {
    const searchParams = new URLSearchParams();
    if (params?.query) searchParams.set('query', params.query);
    if (params?.tag) searchParams.set('tag', params.tag);
    if (params?.limit) searchParams.set('limit', params.limit.toString());
    if (params?.offset) searchParams.set('offset', params.offset.toString());

    const query = searchParams.toString();
    return fetchAPI(`/creators${query ? `?${query}` : ''}`);
  },

  getCreator: (id: string) => fetchAPI(`/creators/${id}`),

  getCreatorAds: (
    id: string,
    params?: {
      platform?: string;
      active?: boolean;
      since?: string;
      until?: string;
      limit?: number;
      offset?: number;
    }
  ) => {
    const searchParams = new URLSearchParams();
    if (params?.platform) searchParams.set('platform', params.platform);
    if (params?.active !== undefined) searchParams.set('active', params.active.toString());
    if (params?.since) searchParams.set('since', params.since);
    if (params?.until) searchParams.set('until', params.until);
    if (params?.limit) searchParams.set('limit', params.limit.toString());
    if (params?.offset) searchParams.set('offset', params.offset.toString());

    const query = searchParams.toString();
    return fetchAPI(`/creators/${id}/ads${query ? `?${query}` : ''}`);
  },

  // Ads
  getAds: (params?: {
    query?: string;
    platform?: string;
    tag?: string;
    since?: string;
    until?: string;
    limit?: number;
    offset?: number;
  }) => {
    const searchParams = new URLSearchParams();
    if (params?.query) searchParams.set('query', params.query);
    if (params?.platform) searchParams.set('platform', params.platform);
    if (params?.tag) searchParams.set('tag', params.tag);
    if (params?.since) searchParams.set('since', params.since);
    if (params?.until) searchParams.set('until', params.until);
    if (params?.limit) searchParams.set('limit', params.limit.toString());
    if (params?.offset) searchParams.set('offset', params.offset.toString());

    const query = searchParams.toString();
    return fetchAPI(`/ads${query ? `?${query}` : ''}`);
  },

  // Tags
  updateAdTags: (adId: string, add: string[], remove: string[]) =>
    fetchAPI(`/ads/${adId}/tags`, {
      method: 'POST',
      body: JSON.stringify({ add, remove }),
    }),

  // Jobs
  getJobs: (limit?: number) => {
    const query = limit ? `?limit=${limit}` : '';
    return fetchAPI(`/jobs${query}`);
  },

  getJob: (id: string) => fetchAPI(`/jobs/${id}`),

  // Admin
  triggerIngestion: () =>
    fetchAPI('/ingest/run', {
      method: 'POST',
    }),

  importData: (data: { creators: any[]; ads: any[] }) =>
    fetchAPI('/ingest/import', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
};
