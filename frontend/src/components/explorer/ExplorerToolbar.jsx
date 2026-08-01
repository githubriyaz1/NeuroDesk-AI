import React from 'react';
import {
  Upload,
  RefreshCw,
  Search,
  LayoutGrid,
  List as ListIcon,
  SlidersHorizontal,
} from 'lucide-react';
import { Button } from '../common/Button';
import { useAssets } from '../../contexts/AssetContext';

export const ExplorerToolbar = () => {
  const {
    filters,
    setFilters,
    viewMode,
    setViewMode,
    setIsUploadModalOpen,
    fetchAssets,
    fetchStatistics,
  } = useAssets();

  const handleRefresh = () => {
    fetchAssets();
    fetchStatistics();
  };

  return (
    <div className="flex flex-col md:flex-row md:items-center justify-between gap-3 p-3 sm:p-4 rounded-xl bg-zinc-950/80 border border-zinc-800/80">
      {/* Search & Filter Controls */}
      <div className="flex flex-1 items-center gap-2">
        <div className="relative flex-1 max-w-xs sm:max-w-md">
          <Search className="absolute left-3 top-2.5 text-zinc-500" size={14} />
          <input
            type="text"
            placeholder="Filter metadata & titles..."
            value={filters.search || ''}
            onChange={(e) => setFilters((prev) => ({ ...prev, search: e.target.value }))}
            className="w-full pl-9 pr-3 py-1.5 bg-zinc-900 border border-zinc-800 rounded-lg text-xs text-zinc-100 placeholder-zinc-500 focus:outline-none focus:border-indigo-500"
          />
        </div>

        {/* Sort Selection */}
        <select
          value={filters.sort_by}
          onChange={(e) => setFilters((prev) => ({ ...prev, sort_by: e.target.value }))}
          className="px-3 py-1.5 bg-zinc-900 border border-zinc-800 rounded-lg text-xs text-zinc-300 focus:outline-none focus:border-indigo-500"
        >
          <option value="created_at">Newest First</option>
          <option value="oldest">Oldest First</option>
          <option value="name_asc">Name (A-Z)</option>
          <option value="name_desc">Name (Z-A)</option>
          <option value="size_largest">Size (Largest)</option>
          <option value="size_smallest">Size (Smallest)</option>
          <option value="type">Asset Type</option>
        </select>
      </div>

      {/* Action Buttons & View Toggles */}
      <div className="flex items-center gap-2 justify-end">
        <Button size="sm" onClick={() => setIsUploadModalOpen(true)}>
          <Upload size={14} className="mr-1.5" /> Upload Asset
        </Button>

        <button
          onClick={handleRefresh}
          className="p-2 rounded-lg bg-zinc-900 hover:bg-zinc-800 text-zinc-400 hover:text-zinc-200 border border-zinc-800 transition-colors"
          title="Refresh Explorer"
        >
          <RefreshCw size={14} />
        </button>

        {/* View Mode Toggle */}
        <div className="flex items-center p-1 rounded-lg bg-zinc-900 border border-zinc-800">
          <button
            onClick={() => setViewMode('grid')}
            className={`p-1.5 rounded transition-colors ${
              viewMode === 'grid'
                ? 'bg-zinc-800 text-indigo-400 font-semibold shadow-sm'
                : 'text-zinc-500 hover:text-zinc-300'
            }`}
            title="Grid View"
          >
            <LayoutGrid size={14} />
          </button>
          <button
            onClick={() => setViewMode('list')}
            className={`p-1.5 rounded transition-colors ${
              viewMode === 'list'
                ? 'bg-zinc-800 text-indigo-400 font-semibold shadow-sm'
                : 'text-zinc-500 hover:text-zinc-300'
            }`}
            title="List View"
          >
            <ListIcon size={14} />
          </button>
        </div>
      </div>
    </div>
  );
};
