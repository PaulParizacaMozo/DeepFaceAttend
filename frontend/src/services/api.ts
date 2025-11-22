// src/services/api.ts
import axios from 'axios';

// import from environment variable
const backendUrl = import.meta.env.VITE_BACKEND_URL || 'http://localhost:5000';

const api = axios.create({
  baseURL: backendUrl,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor para añadir el token a todas las peticiones
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

export default api;