import api from './api';

export const authService = {
  register: async (userData) => {
    const response = await api.post('/auth/register', userData);
    return response.data;
  },

  login: async (email, password) => {
    const response = await api.post('/auth/login', { email, password });
    if (response.data?.access_token) {
      localStorage.setItem('neurodesk_token', response.data.access_token);
      localStorage.setItem('neurodesk_refresh_token', response.data.refresh_token);
    }
    return response.data;
  },

  logout: async () => {
    const refreshToken = localStorage.getItem('neurodesk_refresh_token');
    try {
      if (refreshToken) {
        await api.post('/auth/logout', { refresh_token: refreshToken });
      }
    } catch (err) {
      console.warn('Logout endpoint call failed:', err);
    } finally {
      localStorage.removeItem('neurodesk_token');
      localStorage.removeItem('neurodesk_refresh_token');
    }
  },

  getMe: async () => {
    const response = await api.get('/users/me');
    return response.data;
  },

  updateProfile: async (data) => {
    const response = await api.put('/users/profile', data);
    return response.data;
  },

  changePassword: async (passwords) => {
    const response = await api.post('/users/change-password', passwords);
    return response.data;
  },

  deleteAccount: async () => {
    const response = await api.delete('/users/delete-account');
    localStorage.removeItem('neurodesk_token');
    localStorage.removeItem('neurodesk_refresh_token');
    return response.data;
  },
};
