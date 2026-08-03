import React, { useState } from 'react';
import { AssetProvider, useAssets } from '../contexts/AssetContext';
import { AssetStatsCards } from '../components/assets/AssetStatsCards';
import { UploadModal } from '../components/assets/UploadModal';
import { AssetDetailsDrawer } from '../components/assets/AssetDetailsDrawer';
import { PreviewDrawer } from '../components/preview/PreviewDrawer';
import { ExplorerSidebar } from '../components/explorer/ExplorerSidebar';
import { ExplorerToolbar } from '../components/explorer/ExplorerToolbar';
import { ExplorerGrid } from '../components/explorer/ExplorerGrid';
import { ExplorerList } from '../components/explorer/ExplorerList';
import { BulkActionBar } from '../components/explorer/BulkActionBar';
import { DiscoveryDashboard } from '../components/search/DiscoveryDashboard';
import { Button } from '../components/common/Button';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { EmptyState } from '../components/common/EmptyState';
import {
  FolderKanban,
  Upload,
  ChevronLeft,
  ChevronRight,
  Compass,
  LayoutList,
} from 'lucide-react';

const ExplorerContent = () => {
  const {
    assets,
    total,
    page,
    totalPages,
    loading,
    viewMode,
    selectedAsset,
    previewTargetAsset,
    isUploadModalOpen,
    isDrawerOpen,
    isPreviewOpen,
    setPage,
    setIsUploadModalOpen,
    closeDrawer,
    closePreview,
    fetchAssets,
    toggleFavoriteItem,
    renameAssetItem,
    deleteAssetItem,
    restoreAssetItem,
    downloadAssetItem,
    openDrawer,
    openPreview,
  } = useAssets();

  const [activeTab, setActiveTab] = useState('explorer'); // 'explorer' | 'discovery'

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-zinc-100 flex items-center gap-2">
            <FolderKanban className="text-indigo-400" size={22} />
            Enterprise Digital Asset Explorer & Discovery Platform
          </h1>
          <p className="text-xs text-zinc-400 mt-1">
            Centralized workspace repository for datasets, model weights, prompts, documents, reports, and smart collections.
          </p>
        </div>

        <div className="flex items-center gap-2">
          {/* Navigation Tabs */}
          <div className="flex items-center p-1 rounded-xl bg-zinc-950 border border-zinc-800 text-xs font-medium">
            <button
              onClick={() => setActiveTab('explorer')}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg transition-colors ${
                activeTab === 'explorer'
                  ? 'bg-indigo-600 text-white shadow-sm'
                  : 'text-zinc-400 hover:text-zinc-200'
              }`}
            >
              <LayoutList size={14} />
              <span>Asset Explorer</span>
            </button>

            <button
              onClick={() => setActiveTab('discovery')}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg transition-colors ${
                activeTab === 'discovery'
                  ? 'bg-indigo-600 text-white shadow-sm'
                  : 'text-zinc-400 hover:text-zinc-200'
              }`}
            >
              <Compass size={14} className="text-amber-300" />
              <span>Discovery Platform</span>
            </button>
          </div>

          <Button onClick={() => setIsUploadModalOpen(true)}>
            <Upload size={16} className="mr-2" />
            Upload Asset
          </Button>
        </div>
      </div>

      {/* Stats Cards */}
      <AssetStatsCards statistics={useAssets().statistics} />

      {activeTab === 'discovery' ? (
        <DiscoveryDashboard
          onSelectAsset={(asset) => openDrawer(asset)}
          onPreviewAsset={(asset) => openPreview(asset)}
        />
      ) : (
        /* Main Workspace Explorer Layout */
        <div className="flex flex-col lg:flex-row items-start gap-6">
          {/* Sidebar Categories */}
          <ExplorerSidebar />

          {/* Explorer Content Column */}
          <div className="flex-1 w-full space-y-4">
            {/* Toolbar with Global Search & Advanced Filters */}
            <ExplorerToolbar />

            {/* View Container */}
            {loading ? (
              <LoadingSpinner label="Loading Asset Explorer Repository..." />
            ) : assets.length === 0 ? (
              <EmptyState
                title="No digital assets found in category"
                description="Upload your first dataset, document store, image, or model weight."
                icon={FolderKanban}
                actionLabel="Upload Asset"
                onAction={() => setIsUploadModalOpen(true)}
              />
            ) : viewMode === 'grid' ? (
              <ExplorerGrid />
            ) : (
              <ExplorerList />
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
          </div>
        </div>
      )}

      {/* Floating Bulk Action Bar */}
      <BulkActionBar />

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

      <PreviewDrawer
        isOpen={isPreviewOpen}
        onClose={closePreview}
        asset={selectedAsset}
        onDownload={downloadAssetItem}
      />
    </div>
  );
};

export const WorkspacePage = () => {
  return (
    <AssetProvider>
      <ExplorerContent />
    </AssetProvider>
  );
};

export default WorkspacePage;
