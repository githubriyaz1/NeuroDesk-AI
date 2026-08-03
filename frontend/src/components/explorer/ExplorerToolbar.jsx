import React, { useState } from 'react';
import {
  Upload,
  RefreshCw,
  LayoutGrid,
  List as ListIcon,
  SlidersHorizontal,
  Bookmark,
} from 'lucide-react';
import { Button } from '../common/Button';
import { useAssets } from '../../contexts/AssetContext';
import { GlobalSearchBar } from '../search/GlobalSearchBar';
import { AdvancedFilterPanel } from '../search/AdvancedFilterPanel';
import { SavedViewsModal } from '../search/SavedViewsModal';

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

  const [showAdvancedFilters, setShowAdvancedFilters] = useState(false);
  const [isSavedViewsOpen, setIsSavedViewsOpen] = useState(false);

  const handleRefresh = () => {
    fetchAssets();
    fetchStatistics();
  };

  const handleSearchSubmit = (newQuery) => {
    setFilters((prev) => ({ ...prev, search: newQuery }));
  };

  const handleResetFilters = () => {
    setFilters((prev) => ({ ...prev, search: '' }));
  };

  return (
    <div className="space-y-3">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-3 p-3 sm:p-4 rounded-xl bg-zinc-950/80 border border-zinc-800/80">
        {/* Global Search Bar with Ctrl + K and Suggestions */}
        <div className="flex-1 min-w-0">
          <GlobalSearchBar
            searchQuery={filters.search || ''}
            setSearchQuery={(val) => setFilters((prev) => ({ ...prev, search: val }))}
            onSearch={handleSearchSubmit}
            onToggleFilters={() => setShowAdvancedFilters((prev) => !prev)}
          />
        </div>

        {/* Sort Selection & Actions */}
        <div className="flex items-center gap-2 justify-end flex-wrap">
          <select
            value={filters.sort_by}
            onChange={(e) => setFilters((prev) => ({ ...prev, sort_by: e.target.value }))}
            className="px-3 py-1.5 bg-zinc-900 border border-zinc-800 rounded-lg text-xs text-zinc-300 focus:outline-none focus:border-indigo-500 font-mono"
          >
            <option value="created_at">Newest First</option>
            <option value="oldest">Oldest First</option>
            <option value="name_asc">Name (A-Z)</option>
            <option value="name_desc">Name (Z-A)</option>
            <option value="size_largest">Size (Largest)</option>
            <option value="size_smallest">Size (Smallest)</option>
            <option value="type">Asset Type</option>
          </select>

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

      {/* Advanced Filter Panel */}
      {showAdvancedFilters && (
        <AdvancedFilterPanel
          searchQuery={filters.search || ''}
          setSearchQuery={(val) => setFilters((prev) => ({ ...prev, search: val }))}
          onApply={handleSearchSubmit}
          onReset={handleResetFilters}
          onOpenSavedViews={() => setIsSavedViewsOpen(true)}
        />
      )}

      {/* Saved Views Modal */}
      <SavedViewsModal
        isOpen={isSavedViewsOpen}
        onClose={() => setIsSavedViewsOpen(false)}
        currentQuery={filters.search || ''}
        onSelectQuery={(q) => {
          setFilters((prev) => ({ ...prev, search: q }));
        }}
      />
    </div>
  );
};
