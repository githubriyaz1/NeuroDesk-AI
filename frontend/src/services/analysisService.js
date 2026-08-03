import api from './api';

export const analysisService = {
  async analyzeDocument(assetId) {
    const response = await api.post(`/analysis/document?asset_id=${assetId}`);
    return response.data;
  },

  async analyzeDataset(assetId) {
    const response = await api.post(`/analysis/dataset?asset_id=${assetId}`);
    return response.data;
  },

  async compareAssets(assetIdA, assetIdB) {
    const response = await api.post('/analysis/compare', {
      asset_id_a: assetIdA,
      asset_id_b: assetIdB,
    });
    return response.data;
  },

  async generateInsights(title, summary) {
    const response = await api.post(`/analysis/insights?title=${encodeURIComponent(title)}&summary=${encodeURIComponent(summary)}`);
    return response.data;
  },

  async exportReport(payload) {
    const response = await api.post('/analysis/export', payload);
    return response.data;
  },
};

export default analysisService;
