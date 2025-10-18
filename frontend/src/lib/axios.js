import axios from 'axios';
import { toast } from 'react-hot-toast';
import { isValid } from '../auth/token';

const API_BASE = 'http://localhost:8000/api';

console.log('AXIOS Base URL:', API_BASE);

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: false,
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token && isValid(token)) {
    config.headers.Authorization = 'Bearer ' + token;
  }
  return config;
});

api.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      toast.error('Sesi�n expirada');
      setTimeout(() => window.location.assign('/'), 800);
    }
    return Promise.reject(error);
  }
);

export default api;
