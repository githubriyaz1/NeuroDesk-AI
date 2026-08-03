import api from './api';

export const discoveryService = {
  async getRecent(limit = 10) {
    const response = await api.get('/discovery/recent', { params: { limit } });
    return response.data;
  },

  async getFavorites(limit = 10) {
    const response = await api.get('/discovery/favorites', { params: { limit } });
    return response.data;
  },

  async getLargest(limit = 10) {
    const response = await api.get('/discovery/largest', { params: { limit } });
    return response.data;
  },

  async getNewest(limit = 10) {
    const response = await api.get('/discovery/newest', { params: { limit } });
    return response.data;
  },
};
