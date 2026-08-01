import api from './api';

export const metadataService = {
  /**
   * Fetch extracted metadata for requested asset grouped by categories
   */
  async getMetadata(assetId) {
    const response = await api.get(`/assets/${assetId}/metadata`);
    return response.data;
  },

  /**
   * Trigger refresh/re-indexing of metadata for requested asset
   */
  async refreshMetadata(assetId) {
    const response = await api.post(`/assets/${assetId}/metadata/refresh`);
    return response.data;
  },
};
