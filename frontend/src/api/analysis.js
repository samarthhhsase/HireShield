import apiClient from './client';

/**
 * Scan a candidate posting or recruitment URL through HireShield's live Risk Engine.
 * Calls the actual discovered backend endpoint: POST /api/scan
 *
 * @param {string} url - Target URL to analyze
 * @returns {Promise<Object>} Formatted risk intelligence report
 */
export async function scanJobUrl(url) {
  const response = await apiClient.post('/api/scan', { url });
  
  // Persist scan result to current browser session for Candidate and Dashboard views
  saveScanToSession(response.data);

  return {
    ...response.data,
    latencyMs: response.latencyMs,
  };
}

/**
 * Analyze browser-supplied job page content via fallback endpoint:
 * POST /api/scanner/analyze-content
 * 
 * @param {Object} payload - { url, title, company, content }
 * @returns {Promise<Object>} Formatted risk intelligence report
 */
export async function analyzePageContent({ url, title, company, content }) {
  const response = await apiClient.post('/api/scanner/analyze-content', {
    url,
    title,
    company,
    content,
  });

  saveScanToSession(response.data);

  return {
    ...response.data,
    latencyMs: response.latencyMs,
  };
}

/**
 * Analyze a job/offer PDF document.
 * Calls backend endpoint: POST /api/scanner/analyze-pdf
 *
 * @param {File} file - PDF file to upload and scan
 * @param {Object} [meta] - Optional metadata { company, title }
 * @returns {Promise<Object>} Formatted risk intelligence report
 */
export async function scanJobPdf(file, { company = '', title = '' } = {}) {
  const formData = new FormData();
  formData.append('file', file);
  if (company) formData.append('company', company);
  if (title) formData.append('title', title);

  const response = await apiClient.post('/api/scanner/analyze-pdf', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
    timeout: 30000,
  });

  if (response.data && response.data.success !== false) {
    saveScanToSession(response.data);
  }

  return {
    ...response.data,
    latencyMs: response.latencyMs,
  };
}

/**
 * Analyze a Google Form or recruitment form URL.
 * Calls backend endpoint: POST /api/scanner/analyze-form
 *
 * @param {string} url - Target Google Form URL
 * @returns {Promise<Object>} Formatted risk intelligence report
 */
export async function scanJobForm(url) {
  const response = await apiClient.post('/api/scanner/analyze-form', { url }, {
    timeout: 20000,
  });

  if (response.data && response.data.success !== false) {
    saveScanToSession(response.data);
  }

  return {
    ...response.data,
    latencyMs: response.latencyMs,
  };
}

/**
 * Analyze raw pasted job description or recruitment message text.
 * Calls backend endpoint: POST /api/scanner/analyze-text
 *
 * @param {Object} payload - { text, title, company }
 * @returns {Promise<Object>} Formatted risk intelligence report
 */
export async function scanJobText({ text, title = '', company = '' }) {
  const response = await apiClient.post('/api/scanner/analyze-text', {
    text,
    title,
    company,
  }, {
    timeout: 15000,
  });

  if (response.data && response.data.success !== false) {
    saveScanToSession(response.data);
  }

  return {
    ...response.data,
    latencyMs: response.latencyMs,
  };
}

/**
 * Check backend liveness.
 * Calls actual backend endpoint: GET /health
 */
export async function checkBackendHealth() {
  try {
    const response = await apiClient.get('/health');
    return {
      ...response.data,
      latencyMs: response.latencyMs,
    };
  } catch (err) {
    const response = await apiClient.get('/api/health');
    return {
      ...response.data,
      latencyMs: response.latencyMs,
    };
  }
}

/**
 * Get backend system metadata.
 * Calls actual backend endpoint: GET /
 */
export async function getBackendInfo() {
  const response = await apiClient.get('/');
  return response.data;
}

// In-memory / Session storage helper for scans conducted during the active session
const SESSION_SCANS_KEY = 'hireshield_session_scans';

export function getSessionScans() {
  try {
    const raw = sessionStorage.getItem(SESSION_SCANS_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch {
    return [];
  }
}

export function saveScanToSession(scanData) {
  try {
    const existing = getSessionScans();
    const item = {
      id: scanData.id || `SCAN-${Date.now().toString(36).toUpperCase()}`,
      scannedAt: new Date().toISOString(),
      ...scanData,
    };
    const updated = [
      item,
      ...existing.filter((s) => (s.id && item.id ? s.id !== item.id : s.url !== scanData.url)),
    ].slice(0, 50);
    sessionStorage.setItem(SESSION_SCANS_KEY, JSON.stringify(updated));
    return item;
  } catch (err) {
    console.warn('Could not save scan to session storage', err);
    return scanData;
  }
}
