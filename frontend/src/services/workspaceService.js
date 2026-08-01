import api from './api';

export const workspaceService = {
  getWorkspaceItems: async () => {
    const response = await api.get('/workspace');
    return response.data;
  },

  createWorkspaceItem: async (data) => {
    const response = await api.post('/workspace', data);
    return response.data;
  },
};
