// src/services/api.ts
import axios from 'axios';

// Helper function to ensure consistent URL formatting
const normalizeURL = (url: string): string => {
    return url.replace(/([^:]\/)\/+/g, "$1");
};

// Create axios instance with normalized baseURL
export const api = axios.create({
    baseURL: normalizeURL(import.meta.env.VITE_API_URL || 'https://pintar-ekspor-backend.up.railway.app'),
    headers: {
        'Content-Type': 'application/json',
    },
});

// Add request interceptor for auth token
api.interceptors.request.use(
  (config) => {
      const token = localStorage.getItem('access_token');
      if (token) {
          config.headers.Authorization = `Bearer ${token}`;
      }
      // Normalize URL to prevent double slashes
      if (config.url) {
          config.url = normalizeURL(config.url);
      }
      return config;
  },
  (error) => {
      console.error('Request error:', error);
      return Promise.reject(error);
  }
);

// Add response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  async (error) => {
      if (error.response?.status === 401) {
          const refreshToken = localStorage.getItem('refresh_token');
          if (refreshToken) {
              try {
                  const response = await axios.post(
                      normalizeURL(`${api.defaults.baseURL}/auth/refresh`),
                      { refresh_token: refreshToken }
                  );
                  const { access_token } = response.data;
                  localStorage.setItem('access_token', access_token);
                  
                  // Retry the original request
                  const config = error.config;
                  config.headers.Authorization = `Bearer ${access_token}`;
                  return axios(config);
              } catch (refreshError) {
                  localStorage.removeItem('access_token');
                  localStorage.removeItem('refresh_token');
                  window.location.href = '/login';
              }
          } else {
              window.location.href = '/login';
          }
      }
      return Promise.reject(error);
  }
);