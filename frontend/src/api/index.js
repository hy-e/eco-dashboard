import axios from 'axios';

const api = axios.create({ baseURL: '/api' });

export function fetchStats() {
  return api.get('/stats');
}

export function fetchStepSeqs() {
  return api.get('/step-seqs');
}

export function fetchEcos(params = {}) {
  return api.get('/ecos', { params });
}

export function fetchEcoSummary(ecoNo) {
  return api.get(`/ecos/${encodeURIComponent(ecoNo)}/summary`);
}
