import api from './api';

export const assetService = {
  /**
   * Upload single or multi files to DAMS with progress tracking callback
   */
  async uploadAsset(file, description = '', onProgress = null) {
    const formData = new FormData();
    formData.append('file', file);
    if (description) {
      formData.append('description', description);
    }

    const response = await api.post('/assets/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent) => {
        if (onProgress && progressEvent.total) {
          const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          onProgress(percentCompleted);
        }
      },
    });

    return response.data;
  },

  /**
   * Fetch paginated assets list with optional filtering
   */
  async getAssets(params = {}) {
    const response = await api.get('/assets', { params });
    return response.data;
  },

  /**
   * Fetch user asset statistics
   */
  async getStatistics() {
    const response = await api.get('/assets/statistics');
    return response.data;
  },

  /**
   * Fetch single asset details
   */
  async getAssetDetails(assetId) {
    const response = await api.get(`/assets/${assetId}`);
    return response.data;
  },

  /**
   * Download physical asset file via Blob stream
   */
  async downloadAsset(assetId, filename = 'download') {
    const response = await api.get(`/assets/${assetId}/download`, {
      responseType: 'blob',
    });

    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', filename);
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
  },

  /**
   * Rename asset or update description
   */
  async renameAsset(assetId, name, description = null) {
    const response = await api.patch(`/assets/${assetId}`, { name, description });
    return response.data;
  },

  /**
   * Toggle favorite state
   */
  async toggleFavorite(assetId, isFavorite) {
    const response = await api.post(`/assets/${assetId}/favorite`, {
      is_favorite: isFavorite,
    });
    return response.data;
  },

  /**
   * Toggle archive state
   */
  async toggleArchive(assetId, isArchived = true) {
    const response = await api.post(`/assets/${assetId}/archive`, {
      is_archived: isArchived,
    });
    return response.data;
  },

  /**
   * Execute bulk action across asset IDs
   */
  async executeBulkAction(assetIds, action) {
    const response = await api.post('/assets/bulk-action', {
      asset_ids: assetIds,
      action,
    });
    return response.data;
  },

  /**
   * Soft delete asset
   */
  async deleteAsset(assetId) {
    const response = await api.delete(`/assets/${assetId}`);
    return response.data;
  },

  /**
   * Restore soft-deleted asset
   */
  async restoreAsset(assetId) {
    const response = await api.post(`/assets/${assetId}/restore`);
    return response.data;
  },
};
