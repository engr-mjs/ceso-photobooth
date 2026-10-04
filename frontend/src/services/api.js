import axios from 'axios';

const API_BASE = '/api';

const api = axios.create({
  baseURL: API_BASE,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.response.use(
  (response) => response.data,
  (error) => {
    const message = error.response?.data?.detail || error.message || 'An error occurred';
    return Promise.reject(new Error(message));
  }
);

export const healthCheck = () => api.get('/health');

export const getSettings = () => api.get('/settings');

export const getTemplateConfig = () => api.get('/config/template');

export const createSession = (metadata = null) =>
  api.post('/session/create', { metadata });

export const savePhoto = (sessionId, photoNumber, imageData) =>
  api.post(`/session/${sessionId}/save-photo`, {
    photo_number: photoNumber,
    image: imageData,
  });

export const generateStrip = (sessionId, templateName = 'default') =>
  api.post(`/session/${sessionId}/generate-strip`, {
    session_id: sessionId,
    template_name: templateName,
  });

export const getSessionInfo = (sessionId) =>
  api.get(`/session/${sessionId}/info`);

export const downloadStrip = (sessionId) =>
  `${API_BASE}/download/${sessionId}`;

export const getPreviewUrl = (sessionId) =>
  `${API_BASE}/preview/${sessionId}`;

export const getQRUrl = (sessionId) =>
  `${API_BASE}/qr/${sessionId}`;

export const getPhotoUrl = (sessionId, photoNumber) =>
  `${API_BASE}/photo/${sessionId}/${photoNumber}`;

export const getTemplates = () => api.get('/templates');

export const deleteSession = (sessionId) =>
  api.delete(`/session/${sessionId}`);

export default api;
