import api from './api';

export const chatService = {
  // Conversation API Calls
  async listConversations(params = {}) {
    const response = await api.get('/chat/conversations', { params });
    return response.data;
  },

  async createConversation(data = {}) {
    const response = await api.post('/chat/conversations', data);
    return response.data;
  },

  async getConversation(id) {
    const response = await api.get(`/chat/conversations/${id}`);
    return response.data;
  },

  async updateConversation(id, data) {
    const response = await api.patch(`/chat/conversations/${id}`, data);
    return response.data;
  },

  async deleteConversation(id) {
    const response = await api.delete(`/chat/conversations/${id}`);
    return response.data;
  },

  async archiveConversation(id) {
    const response = await api.post(`/chat/conversations/${id}/archive`);
    return response.data;
  },

  async favoriteConversation(id) {
    const response = await api.post(`/chat/conversations/${id}/favorite`);
    return response.data;
  },

  async pinConversation(id) {
    const response = await api.post(`/chat/conversations/${id}/pin`);
    return response.data;
  },

  async duplicateConversation(id) {
    const response = await api.post(`/chat/conversations/${id}/duplicate`);
    return response.data;
  },

  async restoreConversation(id) {
    const response = await api.post(`/chat/conversations/${id}/restore`);
    return response.data;
  },

  async clearConversation(id) {
    const response = await api.post(`/chat/conversations/${id}/clear`);
    return response.data;
  },

  async exportConversation(id, format = 'markdown') {
    const response = await api.get(`/chat/conversations/${id}/export`, {
      params: { format },
    });
    return response.data;
  },

  async importConversation(jsonContent) {
    const response = await api.post('/chat/conversations/import', {
      json_content: jsonContent,
    });
    return response.data;
  },

  // Message API Calls
  async getMessages(conversationId) {
    const response = await api.get(`/chat/messages/${conversationId}`);
    return response.data;
  },

  async sendMessage(msgData) {
    const response = await api.post('/chat/messages', msgData);
    return response.data;
  },

  async updateMessage(id, content) {
    const response = await api.patch(`/chat/messages/${id}`, { content });
    return response.data;
  },

  async deleteMessage(id) {
    const response = await api.delete(`/chat/messages/${id}`);
    return response.data;
  },

  async regenerateMessage(id) {
    const response = await api.post(`/chat/messages/${id}/regenerate`);
    return response.data;
  },

  // Real-time SSE Streaming & Control API
  async cancelStream(messageId, streamId) {
    const response = await api.post(`/chat/messages/${messageId}/cancel`, null, {
      params: { stream_id: streamId },
    });
    return response.data;
  },

  async getDiagnostics() {
    const response = await api.get('/chat/diagnostics');
    return response.data;
  },

  async streamResponse({ conversation_id, prompt, stream_id, onChunk, onError, onComplete }) {
    const token = localStorage.getItem('token');
    const response = await fetch(`/api/v1/chat/stream?stream_id=${stream_id || ''}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ conversation_id, prompt }),
    });

    if (!response.ok) {
      if (onError) onError(new Error(`Streaming failed: HTTP ${response.status}`));
      return;
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder('utf-8');
    let buffer = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n\n');
      buffer = lines.pop(); // keep last incomplete line

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const data = JSON.parse(line.replace('data: ', ''));
            if (onChunk) onChunk(data);
            if (data.is_final && onComplete) onComplete(data);
          } catch (err) {
            console.error('Failed to parse SSE chunk:', err);
          }
        }
      }
    }
  },
};

export default chatService;
