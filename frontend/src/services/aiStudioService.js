import api from './api';

export const aiStudioService = {
  getModels: async () => {
    const response = await api.get('/ai-studio/models');
    return response.data;
  },

  createModel: async (modelData) => {
    const response = await api.post('/ai-studio/models', modelData);
    return response.data;
  },
};
