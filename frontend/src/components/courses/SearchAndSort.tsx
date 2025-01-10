// src/components/courses/SearchAndSort.tsx
import { useState, useCallback } from 'react';
import debounce from 'lodash/debounce';

type SortOption = 'title' | 'progress';
type SortDirection = 'asc' | 'desc';

interface SearchAndSortProps {
  onSearch: (query: string) => void;
  onSort: (option: SortOption, direction: SortDirection) => void;
}

export default function SearchAndSort({ onSearch, onSort }: SearchAndSortProps) {
  const [searchTerm, setSearchTerm] = useState('');
  const [sortOption, setSortOption] = useState<SortOption>('title');
  const [sortDirection, setSortDirection] = useState<SortDirection>('asc');

  const debouncedSearch = useCallback(
    debounce((query: string) => {
      onSearch(query);
    }, 300),
    [onSearch]
  );

  const handleSearch = (event: React.ChangeEvent<HTMLInputElement>) => {
    const query = event.target.value;
    setSearchTerm(query);
    debouncedSearch(query);
  };

  const handleSort = (option: SortOption) => {
    // If clicking the same option, toggle direction
    if (option === sortOption) {
      const newDirection = sortDirection === 'asc' ? 'desc' : 'asc';
      setSortDirection(newDirection);
      onSort(option, newDirection);
    } else {
      // New option, default to ascending
      setSortOption(option);
      setSortDirection('asc');
      onSort(option, 'asc');
    }
  };

  return (
    <div className="space-y-4">
      {/* Search input */}
      <div className="relative">
        <input
          type="text"
          value={searchTerm}
          onChange={handleSearch}
          placeholder="Search courses..."
          className="w-full px-4 py-2 rounded-lg border border-gray-300 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        />
        <span className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400">
          🔍
        </span>
      </div>

      {/* Sort buttons */}
      <div className="flex gap-2">
        <span className="text-sm text-gray-600 self-center">Sort by:</span>
        <button
          onClick={() => handleSort('title')}
          className={`px-3 py-1 rounded-md text-sm ${
            sortOption === 'title'
              ? 'bg-blue-100 text-blue-700'
              : 'bg-gray-100 text-gray-700'
          }`}
        >
          Title {sortOption === 'title' && (sortDirection === 'asc' ? '↑' : '↓')}
        </button>
        <button
          onClick={() => handleSort('progress')}
          className={`px-3 py-1 rounded-md text-sm ${
            sortOption === 'progress'
              ? 'bg-blue-100 text-blue-700'
              : 'bg-gray-100 text-gray-700'
          }`}
        >
          Progress {sortOption === 'progress' && (sortDirection === 'asc' ? '↑' : '↓')}
        </button>
      </div>
    </div>
  );
}