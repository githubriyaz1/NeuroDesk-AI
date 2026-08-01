import React, { useState } from 'react';
import { AssetProvider, useAssets } from '../contexts/AssetContext';
import { AssetStatsCards } from '../components/assets/AssetStatsCards';
import { UploadModal } from '../components/assets/UploadModal';
import { AssetDetailsDrawer } from '../components/assets/AssetDetailsDrawer';
import { Card } from '../components/common/Card';
import { Button } from '../components/common/Button';
import { Badge } from '../components/common/Badge';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { EmptyState } from '../components/common/EmptyState';
import {
  Upload,
  Search,
  Star,
  Download,
  Trash2,
  RotateCcw,
  Eye,
  FileText,
  Database,
  Image as ImageIcon,
  Music,
  Film,
  Sparkles,
  Box,
  Code,
  FolderKanban,
  ChevronLeft,
  ChevronRight,
  Filter,
} from 'lucide-react';
import { formatBytes, formatDate } from '../utils/formatters';

const getAssetIcon = (type) => {
  switch (type) {
    case 'IMAGE':
      return ImageIcon;
    case 'AUDIO':
      return Music;
    case 'VIDEO':
      return Film;
    case 'SPREADSHEET':
      return Database;
    case 'DATASET':
      return Box;
    case 'PROMPT':
      return Sparkles;
    case 'MODEL':
      return Code;
    case 'REPORT':
      return FileText;
    default:
      return FileText;
  }
};

const WorkspaceContent = () => {
  const {
    assets,
    total,
    page,
    totalPages,
    statistics,
    loading,
    filters,
    selectedAsset,
    isUploadModalOpen,
    isDrawerOpen,
    setPage,
    setFilters,
    setIsUploadModalOpen,
    openDrawer,
    closeDrawer,
    fetchAssets,
    toggleFavoriteItem,
    renameAssetItem,
    deleteAssetItem,
    restoreAssetItem,
    downloadAssetItem,
  } = useAssets();

  const [activeTab, setActiveTab] = useState('ALL');

  const handleTabChange = (type) => {
    setActiveTab(type);
    if (type === 'ALL') {
      setFilters((prev) => ({ ...prev, asset_type: '', is_favorite: undefined, include_deleted: false }));
    } else if (type === 'FAVORITES') {
      setFilters((prev) => ({ ...prev, asset_type: '', is_favorite: true, include_deleted: false }));
    } else if (type === 'TRASH') {
      setFilters((prev) => ({ ...prev, asset_type: '', is_favorite: undefined, include_deleted: true }));
    } else {
      setFilters((prev) => ({ ...prev, asset_type: type, is_favorite: undefined, include_deleted: false }));
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-zinc-100 flex items-center gap-2">
            <FolderKanban className="text-indigo-400" size={22} />
            Digital Asset Management System (DAMS)
          </h1>
          <p className="text-xs text-zinc-400 mt-1">
            Enterprise core repository for datasets, model weights, prompts, documents, and reports.
          </p>
        </div>
        <Button onClick={() => setIsUploadModalOpen(true)}>
          <Upload size={16} className="mr-2" />
          Upload Digital Asset
        </Button>
      </div>

      {/* Statistics Header Cards */}
      <AssetStatsCards statistics={statistics} />

      {/* Controls & Filter Bar */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-4 rounded-xl bg-zinc-950/80 border border-zinc-800/80">
        {/* Type Filter Tabs */}
        <div className="flex items-center gap-1 overflow-x-auto pb-1 md:pb-0 scrollbar-none">
          {[
            { id: 'ALL', label: 'All Assets' },
            { id: 'DATASET', label: 'Datasets' },
            { id: 'DOCUMENT', label: 'Documents' },
            { id: 'SPREADSHEET', label: 'Spreadsheets' },
            { id: 'IMAGE', label: 'Images' },
            { id: 'MODEL', label: 'AI Models' },
            { id: 'FAVORITES', label: 'Favorites' },
            { id: 'TRASH', label: 'Trash' },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => handleTabChange(tab.id)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors flex-shrink-0 ${
                activeTab === tab.id
                  ? 'bg-indigo-600/20 text-indigo-400 border border-indigo-500/30 font-semibold'
                  : 'text-zinc-400 hover:text-zinc-200 hover:bg-zinc-900'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Search & Sort */}
        <div className="flex items-center gap-2">
          <div className="relative flex-1 md:w-64">
            <Search className="absolute left-3 top-2.5 text-zinc-500" size={14} />
            <input
              type="text"
              placeholder="Search assets..."
              value={filters.search || ''}
              onChange={(e) => setFilters((prev) => ({ ...prev, search: e.target.value }))}
              className="w-full pl-9 pr-3 py-1.5 bg-zinc-900 border border-zinc-800 rounded-lg text-xs text-zinc-100 placeholder-zinc-500 focus:outline-none focus:border-indigo-500"
            />
          </div>
          <select
            value={filters.sort_by}
            onChange={(e) => setFilters((prev) => ({ ...prev, sort_by: e.target.value }))}
            className="px-3 py-1.5 bg-zinc-900 border border-zinc-800 rounded-lg text-xs text-zinc-300 focus:outline-none focus:border-indigo-500"
          >
            <option value="created_at">Sort by Date</option>
            <option value="name">Sort by Name</option>
            <option value="file_size">Sort by Size</option>
          </select>
        </div>
      </div>

      {/* Main Assets Grid / Loading / Empty State */}
      {loading ? (
        <LoadingSpinner label="Loading DAMS Repository Assets..." />
      ) : assets.length === 0 ? (
        <EmptyState
          title="No digital assets found"
          description="Upload your first dataset, document store, image, or model weight to DAMS."
          icon={FolderKanban}
          actionLabel="Upload Asset"
          onAction={() => setIsUploadModalOpen(true)}
        />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {assets.map((asset) => {
            const IconComponent = getAssetIcon(asset.asset_type);
            return (
              <Card key={asset.id} className="hover:border-zinc-700/80 transition-all flex flex-col justify-between">
                <div>
                  {/* Top Bar */}
                  <div className="flex items-start justify-between">
                    <div className="flex items-center gap-3">
                      <div className="p-2.5 rounded-lg bg-zinc-900 text-indigo-400 border border-zinc-800">
                        <IconComponent size={20} />
                      </div>
                      <div className="min-w-0">
                        <h3 className="text-sm font-semibold text-zinc-100 truncate">{asset.name}</h3>
                        <span className="text-[10px] font-mono text-zinc-500 uppercase">{asset.asset_type}</span>
                      </div>
                    </div>
                    <div className="flex items-center gap-1">
                      <button
                        onClick={() => toggleFavoriteItem(asset.id, asset.is_favorite)}
                        className="text-zinc-500 hover:text-amber-400 transition-colors p-1"
                      >
                        <Star size={16} className={asset.is_favorite ? 'text-amber-400 fill-amber-400' : ''} />
                      </button>
                      <Badge variant={asset.is_deleted ? 'danger' : 'success'}>{asset.status}</Badge>
                    </div>
                  </div>

                  <p className="text-xs text-zinc-400 mt-3 line-clamp-2 leading-relaxed">
                    {asset.description || 'No description provided.'}
                  </p>
                </div>

                {/* Footer Metadata & Action Buttons */}
                <div className="mt-4 pt-3 border-t border-zinc-800/80 flex items-center justify-between text-[11px] font-mono text-zinc-500">
                  <span>{formatBytes(asset.file_size)}</span>

                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => openDrawer(asset)}
                      className="px-2 py-1 rounded bg-zinc-900 hover:bg-zinc-800 text-zinc-300 hover:text-white transition-colors flex items-center gap-1 text-xs"
                    >
                      <Eye size={12} /> Inspect
                    </button>

                    {!asset.is_deleted ? (
                      <>
                        <button
                          onClick={() => downloadAssetItem(asset.id, asset.original_filename)}
                          className="px-2 py-1 rounded bg-indigo-600/10 hover:bg-indigo-600/20 text-indigo-400 border border-indigo-500/20 transition-colors flex items-center gap-1 text-xs"
                        >
                          <Download size={12} /> Download
                        </button>
                        <button
                          onClick={() => deleteAssetItem(asset.id)}
                          className="p-1 rounded text-zinc-500 hover:text-rose-400 transition-colors"
                          title="Soft Delete"
                        >
                          <Trash2 size={14} />
                        </button>
                      </>
                    ) : (
                      <button
                        onClick={() => restoreAssetItem(asset.id)}
                        className="px-2 py-1 rounded bg-emerald-600/10 hover:bg-emerald-600/20 text-emerald-400 border border-emerald-500/20 transition-colors flex items-center gap-1 text-xs"
                      >
                        <RotateCcw size={12} /> Restore
                      </button>
                    )}
                  </div>
                </div>
              </Card>
            );
          })}
        </div>
      )}

      {/* Pagination Footer */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between p-4 rounded-xl bg-zinc-950/80 border border-zinc-800/80 text-xs text-zinc-400">
          <span>
            Showing Page {page} of {totalPages} ({total} total assets)
          </span>
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              disabled={page <= 1}
              onClick={() => setPage((p) => Math.max(1, p - 1))}
            >
              <ChevronLeft size={14} className="mr-1" /> Previous
            </Button>
            <Button
              variant="outline"
              size="sm"
              disabled={page >= totalPages}
              onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
            >
              Next <ChevronRight size={14} className="ml-1" />
            </Button>
          </div>
        </div>
      )}

      {/* Modals and Drawers */}
      <UploadModal
        isOpen={isUploadModalOpen}
        onClose={() => setIsUploadModalOpen(false)}
        onSuccess={() => fetchAssets()}
      />

      <AssetDetailsDrawer
        isOpen={isDrawerOpen}
        onClose={closeDrawer}
        asset={selectedAsset}
        onDownload={downloadAssetItem}
        onRename={renameAssetItem}
        onToggleFavorite={toggleFavoriteItem}
        onDelete={deleteAssetItem}
        onRestore={restoreAssetItem}
      />
    </div>
  );
};

export const WorkspacePage = () => {
  return (
    <AssetProvider>
      <WorkspaceContent />
    </AssetProvider>
  );
};

export default WorkspacePage;
