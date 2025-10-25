/**
 * Search bar component
 */
'use client';

import { useState } from 'react';

interface SearchBarProps {
  placeholder?: string;
  onSearch: (query: string) => void;
  defaultValue?: string;
}

export default function SearchBar({
  placeholder = 'Search creators or ads...',
  onSearch,
  defaultValue = '',
}: SearchBarProps) {
  const [query, setQuery] = useState(defaultValue);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSearch(query);
  };

  return (
    <form onSubmit={handleSubmit} className="w-full">
      <div className="relative">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder={placeholder}
          className="w-full px-4 py-3 bg-card border border-border rounded-2xl text-foreground placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-primary"
        />
        <button
          type="submit"
          className="absolute right-3 top-1/2 -translate-y-1/2 px-4 py-1.5 bg-primary text-white rounded-lg hover:bg-primary/90 transition"
        >
          Search
        </button>
      </div>
    </form>
  );
}
