import api from './api';

export const knowledgeService = {
  async queryKnowledge(data = {}) {
    const response = await api.post('/knowledge/query', data);
    return response.data;
  },

  async triggerIndexing(assetId = null) {
    const response = await api.post('/knowledge/index', null, {
      params: { asset_id: assetId || undefined },
    });
    return response.data;
  },

  async getDiagnostics() {
    const response = await api.get('/knowledge/diagnostics');
    return response.data;
  },
};

export default knowledgeService;
