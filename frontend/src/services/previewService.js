import api from './api';

export const previewService = {
  /**
   * Fetch structured preview payload for asset
   */
  async getPreview(assetId) {
    const response = await api.get(`/assets/${assetId}/preview`);
    return response.data;
  },

  /**
   * Fetch preview metadata for asset
   */
  async getMetadata(assetId) {
    const response = await api.get(`/assets/${assetId}/metadata`);
    return response.data;
  },

  /**
   * Get thumbnail URL with auth token header or direct stream endpoint
   */
  getThumbnailUrl(assetId) {
    return `${api.defaults.baseURL}/assets/${assetId}/thumbnail`;
  },
};
