import axios from 'axios';

// Active FastAPI backend port is 8001
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8001';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 15000,
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
    let formattedError = {
      status: error.response ? error.response.status : 0,
      message: 'An unexpected communication error occurred.',
      detail: null,
      isNetworkError: false,
      isValidationError: false,
      timestamp: new Date().toISOString(),
    };

    if (!error.response) {
      formattedError.isNetworkError = true;
      formattedError.message = 'Unable to connect to HireShield backend API.';
      formattedError.detail = `Could not reach ${API_BASE_URL}. Ensure the FastAPI server is running with 'python -m uvicorn app.main:app --port 8001'.`;
    } else if (error.response.status === 422) {
      formattedError.isValidationError = true;
      const details = error.response.data?.detail;
      if (Array.isArray(details)) {
        formattedError.message = details.map((d) => d.msg).join(', ');
        formattedError.detail = details;
      } else {
        formattedError.message = 'Invalid request parameters provided.';
        formattedError.detail = details;
      }
    } else if (error.response.status === 400) {
      formattedError.message = error.response.data?.detail || 'Request rejected by HireShield Risk Engine.';
      formattedError.detail = error.response.data?.detail;
    } else if (error.response.status >= 500) {
      formattedError.message = 'HireShield backend internal server error.';
      formattedError.detail = error.response.data?.detail || 'The risk processing engine encountered an unexpected error.';
    } else {
      formattedError.message = error.response.data?.detail || error.message;
    }

    return Promise.reject(formattedError);
  }
);

export default apiClient;
