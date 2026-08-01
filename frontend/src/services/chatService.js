import api from './api';

export const chatService = {
  sendPrompt: async (prompt, sessionId = null) => {
    const response = await api.post('/chat/prompt', { prompt, session_id: sessionId });
    return response.data;
  },

  getSession: async (sessionId = null) => {
    const params = sessionId ? { session_id: sessionId } : {};
    const response = await api.get('/chat/session', { params });
    return response.data;
  },
};
