import api from './api';

export const searchService = {
  /**
   * Search digital assets with query syntax parsing & score ranking
   */
  async search(params = {}) {
    const response = await api.get('/search', { params });
    return response.data;
  },

  /**
   * Fetch auto-complete search suggestions
   */
  async getSuggestions(q, limit = 8) {
    const response = await api.get('/search/suggestions', { params: { q, limit } });
    return response.data;
  },
};
