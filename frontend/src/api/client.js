import axios from 'axios';

// Resolve API Base URL from Vite environment variable (normalized without trailing slash)
const rawBaseUrl = 
  import.meta.env.VITE_API_URL || 
  import.meta.env.VITE_API_BASE_URL || 
  'https://hireshield-production.up.railway.app';

export const API_BASE_URL = rawBaseUrl.replace(/\/+$/, '');

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
});

// Request interceptor for logging, telemetry, and JWT bearer authentication
apiClient.interceptors.request.use(
  (config) => {
    config.metadata = { startTime: new Date() };
    const token = localStorage.getItem('hireshield_auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor with cybersecurity-grade error formatting
apiClient.interceptors.response.use(
  (response) => {
    const duration = new Date() - response.config.metadata.startTime;
    response.latencyMs = duration;
    return response;
  },
  (error) => {
    const status = error.response ? error.response.status : 0;
    let formattedError = {
      status,
      message: 'An unexpected communication error occurred.',
      detail: null,
      isNetworkError: false,
      isTimeout: false,
      isAuthError: false,
      isValidationError: false,
      timestamp: new Date().toISOString(),
      url: error.config?.url || '',
    };

    if (error.code === 'ECONNABORTED' || error.message?.toLowerCase().includes('timeout')) {
      formattedError.isTimeout = true;
      formattedError.message = 'Backend request timed out.';
      formattedError.detail = `The request to ${API_BASE_URL} exceeded ${error.config?.timeout || 30000}ms. The risk engine or target page may be under heavy load.`;
    } else if (!error.response) {
      formattedError.isNetworkError = true;
      formattedError.message = 'Unable to reach backend';
      const isLocal = API_BASE_URL.includes('localhost') || API_BASE_URL.includes('127.0.0.1');
      formattedError.detail = isLocal
        ? `Could not reach ${API_BASE_URL}. Ensure the local FastAPI server is running with 'python -m uvicorn app.main:app --port 8001'.`
        : `Could not reach deployed HireShield backend at ${API_BASE_URL}. Verify network connectivity or check Railway deployment status.`;
    } else if (status === 401) {
      formattedError.isAuthError = true;
      formattedError.message = 'Authentication required';
      formattedError.detail = error.response.data?.detail || 'Please sign in with your enterprise analyst credentials.';
    } else if (status === 403) {
      formattedError.isAuthError = true;
      formattedError.message = 'Access denied';
      formattedError.detail = error.response.data?.detail || 'You do not have authorization to access this resource or candidate dossier.';
    } else if (status === 404) {
      formattedError.message = 'API endpoint not found';
      formattedError.detail = error.response.data?.detail || `Endpoint ${error.config?.url || ''} was not found on ${API_BASE_URL}.`;
    } else if (status === 422) {
      formattedError.isValidationError = true;
      const details = error.response.data?.detail;
      if (Array.isArray(details)) {
        formattedError.message = 'Invalid request data';
        formattedError.detail = details.map((d) => d.msg || `${d.loc?.join('.')}: invalid`).join(', ');
      } else {
        formattedError.message = 'Invalid request data';
        formattedError.detail = details || 'Invalid request parameters provided.';
      }
    } else if (status === 400) {
      formattedError.message = error.response.data?.detail || 'Request rejected by HireShield Risk Engine.';
      formattedError.detail = error.response.data?.detail;
    } else if (status >= 500) {
      formattedError.message = 'Server error';
      formattedError.detail = error.response.data?.detail || 'The risk processing engine encountered an unexpected error.';
    } else {
      formattedError.message = error.response.data?.detail || error.message;
    }

    return Promise.reject(formattedError);
  }
);

export default apiClient;

