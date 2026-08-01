import axios from 'axios';
import { API_BASE_URL } from '../utils/constants';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
});

// Flag to prevent infinite token refresh loops
let isRefreshing = false;
let failedQueue = [];

const processQueue = (error, token = null) => {
  failedQueue.forEach((prom) => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve(token);
    }
  });
  failedQueue = [];
};

// Request Interceptor: Attach bearer access token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('neurodesk_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response Interceptor: Auto Token Refresh on 401
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry && !originalRequest.url.includes('/auth/login') && !originalRequest.url.includes('/auth/refresh')) {
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        })
          .then((token) => {
            originalRequest.headers.Authorization = `Bearer ${token}`;
            return api(originalRequest);
          })
          .catch((err) => Promise.reject(err));
      }

      originalRequest._retry = true;
      isRefreshing = true;

      const refreshToken = localStorage.getItem('neurodesk_refresh_token');

      if (!refreshToken) {
        isRefreshing = false;
        localStorage.removeItem('neurodesk_token');
        localStorage.removeItem('neurodesk_refresh_token');
        window.location.href = '/login';
        return Promise.reject(error);
      }

      try {
        const response = await axios.post(`${API_BASE_URL}/auth/refresh`, {
          refresh_token: refreshToken,
        });

        const { access_token, refresh_token: new_refresh_token } = response.data;
        localStorage.setItem('neurodesk_token', access_token);
        if (new_refresh_token) {
          localStorage.setItem('neurodesk_refresh_token', new_refresh_token);
        }

        api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
        originalRequest.headers['Authorization'] = `Bearer ${access_token}`;

        processQueue(null, access_token);
        isRefreshing = false;
        return api(originalRequest);
      } catch (refreshError) {
        processQueue(refreshError, null);
        isRefreshing = false;
        localStorage.removeItem('neurodesk_token');
        localStorage.removeItem('neurodesk_refresh_token');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    const message = error.response?.data?.detail || error.response?.data?.message || error.message || 'An unexpected API error occurred';
    return Promise.reject({
      status: error.response?.status,
      message,
      details: error.response?.data?.details,
    });
  }
);

export default api;
