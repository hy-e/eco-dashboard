import axios from 'axios';

const api = axios.create({ baseURL: '/api' });

export const fetchStats       = ()           => api.get('/stats');
export const fetchStepSeqs    = ()           => api.get('/step-seqs');
export const fetchEcos        = (params={}) => api.get('/ecos', { params });
export const fetchEcoSummary  = (ecoNo)     => api.get(`/ecos/${encodeURIComponent(ecoNo)}/summary`);
export const fetchEcoAnalysis = (ecoNo)     => api.get(`/ecos/${encodeURIComponent(ecoNo)}/analysis`);
export const fetchItemData    = (ecoNo, param) =>
  api.get(`/ecos/${encodeURIComponent(ecoNo)}/items/${encodeURIComponent(param)}/data`);
