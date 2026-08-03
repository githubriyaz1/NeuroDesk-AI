import api from './api';

export const generatorService = {
  generateBlueprint: async (payload) => {
    const response = await api.post('/ai-studio/generate', payload);
    return response.data;
  },

  getBlueprints: async (params = {}) => {
    const response = await api.get('/ai-studio/blueprints', { params });
    return response.data;
  },

  getBlueprintDetails: async (blueprintId) => {
    const response = await api.get(`/ai-studio/blueprints/${blueprintId}`);
    return response.data;
  },

  updateBlueprint: async (blueprintId, payload) => {
    const response = await api.put(`/ai-studio/blueprints/${blueprintId}`, payload);
    return response.data;
  },

  cloneBlueprint: async (blueprintId) => {
    const response = await api.post(`/ai-studio/blueprints/${blueprintId}/clone`);
    return response.data;
  },

  exportBlueprint: async (payload) => {
    const response = await api.post('/ai-studio/export', payload);
    return response.data;
  },

  getMetrics: async () => {
    const response = await api.get('/ai-studio/blueprints/metrics');
    return response.data;
  },

  getStarterTemplates: async () => {
    const response = await api.get('/ai-studio/blueprints/templates/starter');
    return response.data;
  },
};
