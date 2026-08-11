import api from './api';

export const workflowService = {
  listWorkflows: async (params = {}) => {
    const response = await api.get('/workflows', { params });
    return response.data;
  },

  getWorkflow: async (workflowId) => {
    const response = await api.get(`/workflows/${workflowId}`);
    return response.data;
  },

  createWorkflow: async (payload) => {
    const response = await api.post('/workflows', payload);
    return response.data;
  },

  updateWorkflow: async (workflowId, payload) => {
    const response = await api.put(`/workflows/${workflowId}`, payload);
    return response.data;
  },

  runWorkflow: async (workflowId, payload = { inputs: {} }) => {
    const response = await api.post(`/workflows/${workflowId}/run`, payload);
    return response.data;
  },

  cancelExecution: async (executionId) => {
    const response = await api.post(`/workflows/executions/${executionId}/cancel`);
    return response.data;
  },

  getExecutionDetails: async (executionId) => {
    const response = await api.get(`/workflows/executions/${executionId}`);
    return response.data;
  },

  listExecutions: async (params = {}) => {
    const response = await api.get('/workflows/executions', { params });
    return response.data;
  },

  getStarterTemplates: async () => {
    const response = await api.get('/workflows/templates');
    return response.data;
  },

  getMetrics: async () => {
    const response = await api.get('/workflows/metrics');
    return response.data;
  },

  duplicateWorkflow: async (workflowId) => {
    const response = await api.post(`/workflows/${workflowId}/duplicate`);
    return response.data;
  },

  deleteWorkflow: async (workflowId) => {
    const response = await api.delete(`/workflows/${workflowId}`);
    return response.data;
  },

  exportWorkflow: async (workflowId) => {
    const response = await api.get(`/workflows/${workflowId}/export`);
    return response.data;
  },

  importWorkflow: async (payload) => {
    const response = await api.post('/workflows/import', payload);
    return response.data;
  },
};
