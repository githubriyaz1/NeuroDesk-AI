import React, { createContext, useContext, useState, useCallback, useEffect } from 'react';
import { assetService } from '../services/assetService';

const AssetContext = createContext(null);

export const AssetProvider = ({ children }) => {
  const [assets, setAssets] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(24);
  const [totalPages, setTotalPages] = useState(1);
  const [statistics, setStatistics] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  
  const [viewMode, setViewMode] = useState('grid'); // 'grid' | 'list'
  const [activeCategory, setActiveCategory] = useState('all');
  const [selectedAssetIds, setSelectedAssetIds] = useState([]);
  const [selectedAsset, setSelectedAsset] = useState(null);

  const [isUploadModalOpen, setIsUploadModalOpen] = useState(false);
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);
  const [isPreviewOpen, setIsPreviewOpen] = useState(false);

  const [filters, setFilters] = useState({
    asset_type: '',
    status: '',
    is_favorite: undefined,
    include_deleted: false,
    sort_by: 'created_at',
    sort_dir: 'desc',
    search: '',
  });

  const fetchStatistics = useCallback(async () => {
    try {
      const stats = await assetService.getStatistics();
      setStatistics(stats);
    } catch (err) {
      console.error('Failed to load asset statistics:', err);
    }
  }, []);

  const fetchAssets = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const params = {
        page,
        page_size: pageSize,
        sort_by: filters.sort_by,
        sort_dir: filters.sort_dir,
        include_deleted: filters.include_deleted || activeCategory === 'trash',
      };

      if (filters.asset_type) params.asset_type = filters.asset_type;
      if (filters.status) params.status = filters.status;
      if (filters.is_favorite !== undefined) params.is_favorite = filters.is_favorite;

      const data = await assetService.getAssets(params);
      let items = data.items || [];

      if (filters.search) {
        const q = filters.search.toLowerCase();
        items = items.filter(
          (a) => a.name.toLowerCase().includes(q) || a.original_filename.toLowerCase().includes(q)
        );
      }

      setAssets(items);
      setTotal(data.total || 0);
      setTotalPages(data.total_pages || 1);
    } catch (err) {
      console.error('Failed to fetch assets:', err);
      setError(err.message || 'Failed to load assets');
    } finally {
      setLoading(false);
    }
  }, [page, pageSize, filters, activeCategory]);

  useEffect(() => {
    fetchAssets();
    fetchStatistics();
  }, [fetchAssets, fetchStatistics]);

  const selectCategory = (cat) => {
    setActiveCategory(cat);
    setSelectedAssetIds([]);
    setPage(1);

    switch (cat) {
      case 'all':
        setFilters((prev) => ({ ...prev, asset_type: '', status: '', is_favorite: undefined, include_deleted: false }));
        break;
      case 'recent':
        setFilters((prev) => ({ ...prev, asset_type: '', status: '', is_favorite: undefined, include_deleted: false, sort_by: 'created_at', sort_dir: 'desc' }));
        break;
      case 'favorites':
        setFilters((prev) => ({ ...prev, asset_type: '', status: '', is_favorite: true, include_deleted: false }));
        break;
      case 'documents':
        setFilters((prev) => ({ ...prev, asset_type: 'DOCUMENT', status: '', is_favorite: undefined, include_deleted: false }));
        break;
      case 'images':
        setFilters((prev) => ({ ...prev, asset_type: 'IMAGE', status: '', is_favorite: undefined, include_deleted: false }));
        break;
      case 'datasets':
        setFilters((prev) => ({ ...prev, asset_type: 'DATASET', status: '', is_favorite: undefined, include_deleted: false }));
        break;
      case 'archived':
        setFilters((prev) => ({ ...prev, asset_type: '', status: 'ARCHIVED', is_favorite: undefined, include_deleted: false }));
        break;
      case 'trash':
        setFilters((prev) => ({ ...prev, asset_type: '', status: 'DELETED', is_favorite: undefined, include_deleted: true }));
        break;
      default:
        break;
    }
  };

  const toggleSelectAsset = (assetId) => {
    setSelectedAssetIds((prev) =>
      prev.includes(assetId) ? prev.filter((id) => id !== assetId) : [...prev, assetId]
    );
  };

  const selectAllAssets = () => {
    if (selectedAssetIds.length === assets.length) {
      setSelectedAssetIds([]);
    } else {
      setSelectedAssetIds(assets.map((a) => a.id));
    }
  };

  const clearSelection = () => {
    setSelectedAssetIds([]);
  };

  const openDrawer = (asset) => {
    setSelectedAsset(asset);
    setIsDrawerOpen(true);
  };

  const closeDrawer = () => {
    setIsDrawerOpen(false);
    setSelectedAsset(null);
  };

  const openPreview = (asset) => {
    setSelectedAsset(asset);
    setIsPreviewOpen(true);
  };

  const closePreview = () => {
    setIsPreviewOpen(false);
    setSelectedAsset(null);
  };

  const executeBulkAction = async (action) => {
    if (selectedAssetIds.length === 0) return;
    try {
      await assetService.executeBulkAction(selectedAssetIds, action);
      setSelectedAssetIds([]);
      await fetchAssets();
      await fetchStatistics();
    } catch (err) {
      console.error('Failed to execute bulk action:', err);
    }
  };

  const toggleFavoriteItem = async (assetId, currentFavoriteState) => {
    try {
      const updated = await assetService.toggleFavorite(assetId, !currentFavoriteState);
      setAssets((prev) => prev.map((a) => (a.id === assetId ? updated : a)));
      if (selectedAsset?.id === assetId) setSelectedAsset(updated);
      fetchStatistics();
    } catch (err) {
      console.error('Failed to toggle favorite:', err);
    }
  };

  const archiveAssetItem = async (assetId, currentStatus) => {
    try {
      const isArchived = currentStatus === 'ARCHIVED';
      const updated = await assetService.toggleArchive(assetId, !isArchived);
      setAssets((prev) => prev.map((a) => (a.id === assetId ? updated : a)));
      if (selectedAsset?.id === assetId) setSelectedAsset(updated);
      fetchStatistics();
    } catch (err) {
      console.error('Failed to toggle archive:', err);
    }
  };

  const renameAssetItem = async (assetId, newName, newDescription) => {
    try {
      const updated = await assetService.renameAsset(assetId, newName, newDescription);
      setAssets((prev) => prev.map((a) => (a.id === assetId ? updated : a)));
      if (selectedAsset?.id === assetId) setSelectedAsset(updated);
    } catch (err) {
      console.error('Failed to rename asset:', err);
      throw err;
    }
  };

  const deleteAssetItem = async (assetId) => {
    try {
      const updated = await assetService.deleteAsset(assetId);
      setAssets((prev) => prev.map((a) => (a.id === assetId ? updated : a)));
      if (selectedAsset?.id === assetId) setSelectedAsset(updated);
      fetchStatistics();
    } catch (err) {
      console.error('Failed to soft delete asset:', err);
    }
  };

  const restoreAssetItem = async (assetId) => {
    try {
      const updated = await assetService.restoreAsset(assetId);
      setAssets((prev) => prev.map((a) => (a.id === assetId ? updated : a)));
      if (selectedAsset?.id === assetId) setSelectedAsset(updated);
      fetchStatistics();
    } catch (err) {
      console.error('Failed to restore asset:', err);
    }
  };

  const downloadAssetItem = async (assetId, filename) => {
    try {
      await assetService.downloadAsset(assetId, filename);
    } catch (err) {
      console.error('Failed to download asset:', err);
      throw err;
    }
  };

  return (
    <AssetContext.Provider
      value={{
        assets,
        total,
        page,
        pageSize,
        totalPages,
        statistics,
        loading,
        error,
        filters,
        viewMode,
        activeCategory,
        selectedAssetIds,
        selectedAsset,
        isUploadModalOpen,
        isDrawerOpen,
        isPreviewOpen,
        setViewMode,
        setPage,
        setPageSize,
        setFilters,
        setIsUploadModalOpen,
        selectCategory,
        toggleSelectAsset,
        selectAllAssets,
        clearSelection,
        executeBulkAction,
        openDrawer,
        closeDrawer,
        openPreview,
        closePreview,
        fetchAssets,
        fetchStatistics,
        toggleFavoriteItem,
        archiveAssetItem,
        renameAssetItem,
        deleteAssetItem,
        restoreAssetItem,
        downloadAssetItem,
      }}
    >
      {children}
    </AssetContext.Provider>
  );
};

export const useAssets = () => {
  const context = useContext(AssetContext);
  if (!context) {
    throw new Error('useAssets must be used within an AssetProvider');
  }
  return context;
};
