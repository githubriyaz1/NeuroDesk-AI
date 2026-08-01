import api from './api';

export const workflowService = {
  getWorkflows: async () => {
    const response = await api.get('/workflows');
    return response.data;
  },

  createWorkflow: async (data) => {
    const response = await api.post('/workflows', data);
    return response.data;
  },
};
