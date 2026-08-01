import React, { createContext, useContext, useState, useCallback, useEffect } from 'react';
import { assetService } from '../services/assetService';

const AssetContext = createContext(null);

export const AssetProvider = ({ children }) => {
  const [assets, setAssets] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);
  const [totalPages, setTotalPages] = useState(1);
  const [statistics, setStatistics] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [selectedAsset, setSelectedAsset] = useState(null);
  const [isUploadModalOpen, setIsUploadModalOpen] = useState(false);
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);

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
        include_deleted: filters.include_deleted,
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
  }, [page, pageSize, filters]);

  useEffect(() => {
    fetchAssets();
    fetchStatistics();
  }, [fetchAssets, fetchStatistics]);

  const openDrawer = (asset) => {
    setSelectedAsset(asset);
    setIsDrawerOpen(true);
  };

  const closeDrawer = () => {
    setIsDrawerOpen(false);
    setSelectedAsset(null);
  };

  const toggleFavoriteItem = async (assetId, currentFavoriteState) => {
    try {
      const updated = await assetService.toggleFavorite(assetId, !currentFavoriteState);
      setAssets((prev) => prev.map((a) => (a.id === assetId ? updated : a)));
      if (selectedAsset?.id === assetId) {
        setSelectedAsset(updated);
      }
      fetchStatistics();
    } catch (err) {
      console.error('Failed to toggle favorite:', err);
    }
  };

  const renameAssetItem = async (assetId, newName, newDescription) => {
    try {
      const updated = await assetService.renameAsset(assetId, newName, newDescription);
      setAssets((prev) => prev.map((a) => (a.id === assetId ? updated : a)));
      if (selectedAsset?.id === assetId) {
        setSelectedAsset(updated);
      }
    } catch (err) {
      console.error('Failed to rename asset:', err);
      throw err;
    }
  };

  const deleteAssetItem = async (assetId) => {
    try {
      const updated = await assetService.deleteAsset(assetId);
      setAssets((prev) => prev.map((a) => (a.id === assetId ? updated : a)));
      if (selectedAsset?.id === assetId) {
        setSelectedAsset(updated);
      }
      fetchStatistics();
    } catch (err) {
      console.error('Failed to soft delete asset:', err);
    }
  };

  const restoreAssetItem = async (assetId) => {
    try {
      const updated = await assetService.restoreAsset(assetId);
      setAssets((prev) => prev.map((a) => (a.id === assetId ? updated : a)));
      if (selectedAsset?.id === assetId) {
        setSelectedAsset(updated);
      }
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
        selectedAsset,
        isUploadModalOpen,
        isDrawerOpen,
        setPage,
        setPageSize,
        setFilters,
        setIsUploadModalOpen,
        openDrawer,
        closeDrawer,
        fetchAssets,
        fetchStatistics,
        toggleFavoriteItem,
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
