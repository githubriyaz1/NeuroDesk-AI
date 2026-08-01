import api from './api';

export const generatorService = {
  generateBlueprint: async (payload) => {
    const response = await api.post('/project-generator/generate', payload);
    return response.data;
  },

  getBlueprints: async () => {
    const response = await api.get('/project-generator/blueprints');
    return response.data;
  },
};
