import axios from 'axios';

export const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000';
export const API = `${BACKEND_URL}/api`;

export const api = axios.create({
  baseURL: API,
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers = config.headers || {};
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const getErrorMessage = (err) => {
  const data = err?.response?.data;
  if (!data) return 'An error occurred';
  if (typeof data.detail === 'string') return data.detail;
  if (typeof data.error === 'string') return data.error;
  if (typeof data.message === 'string') return data.message;
  if (typeof data === 'string') return data;
  if (typeof data === 'object') {
    const firstKey = Object.keys(data)[0];
    const value = Array.isArray(data[firstKey]) ? data[firstKey][0] : data[firstKey];
    if (typeof value === 'string') return value;
  }
  return 'An error occurred';
};


