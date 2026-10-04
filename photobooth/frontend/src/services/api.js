import axios from 'axios';

const API_BASE = import.meta.env.PROD ? '' : '';

const api = axios.create({ baseURL: API_BASE, timeout: 30000 });

api.interceptors.response.use(
  (response) => response,
  (error) => {
    const message = error.response?.data?.detail || error.message || 'An error occurred';
    return Promise.reject(new Error(message));
  }
);

export const serverAPI = {
  getHealth: () => api.get('/health'),
  getInfo: () => api.get('/api/info'),
};

export const sessionAPI = {
  create: () => api.post('/api/sessions'),
  get: (sessionId) => api.get('/api/sessions/' + sessionId),
  list: () => api.get('/api/sessions'),
};

export const photoAPI = {
  uploadBase64: (sessionId, photoIndex, imageData) =>
    api.post('/api/sessions/' + sessionId + '/photos/base64/' + photoIndex, { image_data: imageData }),
  uploadFile: (sessionId, photoIndex, file) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/api/sessions/' + sessionId + '/photos/' + photoIndex, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  list: (sessionId) => api.get('/api/sessions/' + sessionId + '/photos'),
  getFile: (sessionId, photoIndex) => API_BASE + '/api/sessions/' + sessionId + '/photos/' + photoIndex + '/file',
};

export const stripAPI = {
  generate: (sessionId) => api.post('/api/sessions/' + sessionId + '/generate-strip'),
  getStrip: (sessionId) => API_BASE + '/api/sessions/' + sessionId + '/strip',
  getQR: (sessionId) => API_BASE + '/api/sessions/' + sessionId + '/qr',
  getDownloadURL: (sessionId) => API_BASE + '/download/' + sessionId,
  getPreviewURL: (sessionId) => API_BASE + '/api/sessions/' + sessionId + '/preview',
};

export const templateAPI = {
  list: () => api.get('/api/templates'),
  get: (templateId) => api.get('/api/templates/' + templateId),
  setActive: (templateId) => api.post('/api/templates/active', { template_id: templateId }),
};

export const configAPI = {
  get: () => api.get('/api/config'),
  update: (config) => api.put('/api/config', config),
};

export default api;