import { apiClient } from './client';
import { getSessionScans } from './analysis';

/**
 * BACKEND CANDIDATE / JOB PERSISTENCE API:
 * Fully implemented in FastAPI backend:
 * - GET /api/candidates
 * - GET /api/candidates/{id}
 * - POST /api/candidates
 * - DELETE /api/candidates/{id}
 */
export const CANDIDATES_API_MISSING = false;
export const CANDIDATES_ENDPOINT = '/api/candidates';

// Fallback demo baseline records in case server connection is offline
const DEMO_CANDIDATE_TARGETS = [
  {
    id: 'HS-2026-00421',
    isDemoData: true,
    candidateName: 'Alex Mercer (Lead Fullstack Architect)',
    url: 'https://example-careers.io/positions/lead-architect',
    final_url: 'https://example-careers.io/positions/lead-architect',
    job: {
      title: 'Senior Distributed Systems Architect',
      text_preview: 'Seeking experienced architect with 8+ years in cloud infrastructure, Go, and Kubernetes. No upfront deposit required.',
    },
    scores: {
      behavioral: 12,
      linguistic: 8,
      structural: 10,
      technical: 15,
    },
    risk_score: 11,
    risk_level: 'LOW',
    red_flags: [],
    technical_checks: {
      ssl_valid: true,
      domain_age_days: 1420,
      dns_exists: true,
      ip: '198.51.100.42',
      redirect_count: 0,
    },
    scannedAt: '2026-09-20T10:14:00Z',
  },
  {
    id: 'HS-2026-00892',
    isDemoData: true,
    candidateName: 'Elena Rostova (Cryptographic Engineer)',
    url: 'https://telegram-quick-hire.vip/apply-urgent',
    final_url: 'https://redirect-node.net/portal/fee-collector',
    job: {
      title: 'Immediate Remote Data Entry Specialist - Urgent Hiring',
      text_preview: 'Urgent vacancies! High salary guaranteed! Must pay ₹2500 refundable processing fee and provide Aadhaar Card and bank account details for verification.',
    },
    scores: {
      behavioral: 90,
      linguistic: 65,
      structural: 60,
      technical: 75,
    },
    risk_score: 85,
    risk_level: 'CRITICAL',
    red_flags: [
      {
        type: 'behavioral',
        severity: 'critical',
        message: 'Sensitive identity or financial information is requested.',
      },
      {
        type: 'behavioral',
        severity: 'critical',
        message: 'A payment, fee, deposit, or paid verification is requested.',
      },
      {
        type: 'linguistic',
        severity: 'high',
        message: 'Urgency or pressure-based recruitment language detected.',
      },
      {
        type: 'structural',
        severity: 'medium',
        message: 'Recruitment appears to rely on informal messaging channels.',
      },
    ],
    technical_checks: {
      ssl_valid: false,
      domain_age_days: 12,
      dns_exists: true,
      ip: '203.0.113.19',
      redirect_count: 3,
    },
    scannedAt: '2026-09-20T11:45:00Z',
  },
  {
    id: 'HS-2026-01044',
    isDemoData: true,
    candidateName: 'Marcus Vance (Data Science Lead)',
    url: 'https://fast-talent-pipeline.co/roles/ds',
    final_url: 'https://fast-talent-pipeline.co/roles/ds',
    job: {
      title: 'Machine Learning Research Engineer',
      text_preview: 'Position available immediately. No experience required for high salary. Send resume via WhatsApp recruiter.',
    },
    scores: {
      behavioral: 0,
      linguistic: 55,
      structural: 40,
      technical: 25,
    },
    risk_score: 42,
    risk_level: 'MEDIUM',
    red_flags: [
      {
        type: 'linguistic',
        severity: 'high',
        message: 'Unusually strong job or income guarantees detected.',
      },
      {
        type: 'structural',
        severity: 'medium',
        message: 'Recruitment appears to rely on informal messaging channels.',
      },
    ],
    technical_checks: {
      ssl_valid: true,
      domain_age_days: 94,
      dns_exists: true,
      ip: '198.51.100.88',
      redirect_count: 1,
    },
    scannedAt: '2026-09-20T12:30:00Z',
  },
];

/**
 * Fetches candidates from backend SQLite database via GET /api/candidates.
 * Falls back to active session scans + demo targets if backend is temporarily unreachable.
 */
export async function getCandidatesList(params = {}) {
  try {
    const response = await apiClient.get('/api/candidates', { params });
    if (Array.isArray(response.data) && response.data.length > 0) {
      return response.data;
    }
  } catch (err) {
    console.warn('Backend /api/candidates fetch warning, using local session state:', err);
  }

  // Graceful fallback for offline mode
  const sessionScans = getSessionScans().map((scan, idx) => ({
    ...scan,
    id: scan.id || `SCAN-SESSION-${idx + 1}`,
    candidateName: scan.job?.title || 'Scanned Target Profile',
    isDemoData: false,
  }));

  return [...sessionScans, ...DEMO_CANDIDATE_TARGETS];
}

/**
 * Get single candidate by ID from backend SQLite database via GET /api/candidates/{id}
 */
export async function getCandidateById(id) {
  try {
    const response = await apiClient.get(`/api/candidates/${encodeURIComponent(id)}`);
    if (response.data && response.data.id) {
      return response.data;
    }
  } catch (err) {
    console.warn(`Backend /api/candidates/${id} fetch warning:`, err);
  }

  // Fallback to local search
  const all = await getCandidatesList();
  const match = all.find((c) => c.id === id);
  if (!match) {
    throw new Error(`Candidate or job dossier with ID '${id}' not found.`);
  }
  return match;
}

/**
 * Manually create a new candidate dossier via POST /api/candidates
 */
export async function createCandidate(payload) {
  const response = await apiClient.post('/api/candidates', payload);
  return response.data;
}

/**
 * Delete a candidate dossier by ID via DELETE /api/candidates/{id}
 */
export async function deleteCandidate(id) {
  const response = await apiClient.delete(`/api/candidates/${encodeURIComponent(id)}`);
  return response.data;
}
