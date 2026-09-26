import apiClient from './client';

/**
 * Universal Risk Intelligence Report Normalizer.
 * Synthesizes responses from /api/risk/analyze, /api/scan, and /api/scanner/analyze-content
 * into a single unified schema expected by RiskAnalysis.jsx and its subcomponents.
 *
 * @param {Object} raw - Raw API response from backend
 * @param {Object} [context] - Calling context metadata (url, title, company, inputType)
 * @returns {Object} Fully normalized and enriched risk report
 */
export function normalizeRiskReport(raw, context = {}) {
  if (!raw) return null;

  const url = raw.final_url || raw.url || context.url || '';
  const inputType = raw.input_type || raw.inputType || context.inputType || (url ? 'URL' : 'TEXT');
  const riskScore = typeof raw.risk_score === 'number' 
    ? raw.risk_score 
    : (typeof raw.score === 'number' ? raw.score : 0);

  // Extract signals / red flags
  const redFlags = raw.red_flags || raw.signals || [];

  // Extract green flags / positive signals
  const greenFlags = raw.green_flags || (raw.positive_signals || []).map((s) => (typeof s === 'string' ? { message: s } : s));
  const positiveSignals = raw.positive_signals || (raw.green_flags || []).map((g) => (typeof g === 'string' ? g : g.message || ''));

  // Extract verdict
  const verdict = raw.verdict || raw.verification_audit?.verdict || (
    riskScore >= 60 ? 'CONFIRMED_SCAM' : riskScore >= 35 ? 'SUSPICIOUS' : 'VERIFIED_LEGITIMATE'
  );

  // Extract domain details & technical checks
  const domainAnalysis = raw.analysis?.domain || {};
  const domainDetails = domainAnalysis.details || {};
  const ssl = domainDetails.ssl || {};
  const dns = domainDetails.dns || {};
  const whois = domainDetails.whois || {};

  const technicalChecks = raw.technical_checks || {
    ssl_valid: ssl.ssl_valid ?? (url && url.startsWith('https://') ? true : null),
    domain_age_days: whois.age_days ?? null,
    dns_exists: dns.resolves ?? (url ? true : null),
    ip: dns.resolved_ips ? dns.resolved_ips[0] : null,
    redirect_count: 0,
    is_https: url ? url.startsWith('https://') : false,
    suspicious_patterns: { flagged: false },
  };

  let parsedHost = 'Not Provided';
  if (url) {
    try {
      parsedHost = new URL(url.startsWith('http') ? url : `https://${url}`).hostname;
    } catch {
      parsedHost = url;
    }
  }

  const urlIntelligence = raw.url_intelligence || {
    domain: domainAnalysis.domain || parsedHost,
    is_https: url ? url.startsWith('https://') : false,
    dns_exists: dns.resolves ?? Boolean(url),
    ssl_valid: ssl.ssl_valid ?? Boolean(url && url.startsWith('https://')),
    domain_age_days: whois.age_days ?? null,
    ip: dns.resolved_ips ? dns.resolved_ips[0] : null,
    suspicious_url_patterns: false,
    analysis_available: Boolean(url),
  };

  // Scores breakdown
  const scores = raw.scores || {
    behavioral: raw.analysis?.company?.score || 0,
    linguistic: raw.analysis?.nlp?.score || 0,
    structural: raw.analysis?.payment_credential?.score || 0,
    technical: domainAnalysis.score || 0,
  };

  // 4-Pillar risk categories breakdown
  const categories = raw.categories || {
    financial_risk: {
      score: scores.structural || 0,
      level: (scores.structural || 0) > 30 ? 'High' : 'Low',
      signals: redFlags.filter((f) => {
        const text = (f.title || f.name || f.message || '').toLowerCase();
        return text.includes('fee') || text.includes('pay') || text.includes('upi') || text.includes('money') || text.includes('deposit');
      }),
    },
    identity_risk: {
      score: scores.behavioral || 0,
      level: (scores.behavioral || 0) > 30 ? 'High' : 'Low',
      signals: redFlags.filter((f) => {
        const text = (f.title || f.name || f.message || '').toLowerCase();
        return text.includes('aadhaar') || text.includes('pan') || text.includes('bank') || text.includes('id') || text.includes('credential');
      }),
    },
    behavioral_risk: {
      score: scores.linguistic || 0,
      level: (scores.linguistic || 0) > 30 ? 'High' : 'Low',
      signals: redFlags.filter((f) => {
        const text = (f.title || f.name || f.message || '').toLowerCase();
        return text.includes('urgent') || text.includes('telegram') || text.includes('whatsapp') || text.includes('guaranteed');
      }),
    },
    technical_risk: {
      score: scores.technical || 0,
      level: (scores.technical || 0) > 30 ? 'High' : 'Low',
      signals: redFlags.filter((f) => {
        const text = (f.title || f.name || f.message || '').toLowerCase();
        return text.includes('dns') || text.includes('ssl') || text.includes('domain') || text.includes('tld');
      }),
    },
  };

  // Job metadata
  const job = raw.job || {
    title: raw.title || context.title || (context.company ? `${context.company} Position` : 'Recruitment Target'),
    company: raw.company || context.company || null,
    text_preview: raw.text_preview || (context.text ? context.text.slice(0, 1000) : ''),
  };

  return {
    ...raw,
    id: raw.id || raw.candidate_id || `SCAN-${Date.now().toString(36).toUpperCase()}`,
    risk_score: riskScore,
    score: riskScore,
    risk_level: raw.risk_level || (riskScore >= 75 ? 'CRITICAL' : riskScore >= 50 ? 'HIGH' : riskScore >= 25 ? 'MEDIUM' : 'LOW'),
    confidence: typeof raw.confidence === 'number' ? raw.confidence : 0.85,
    summary: raw.summary || raw.explanation || 'Recruitment risk intelligence evaluation complete.',
    explanation: raw.explanation || raw.summary || 'Recruitment risk intelligence evaluation complete.',
    verdict,
    legitimacy_score: typeof raw.legitimacy_score === 'number' ? raw.legitimacy_score : Math.max(0, 100 - riskScore),
    fake_job_probability: typeof raw.fake_job_probability === 'number' ? raw.fake_job_probability : Math.round(riskScore),
    input_type: inputType,
    inputType: inputType,
    url,
    final_url: raw.final_url || url,
    signals: redFlags,
    red_flags: redFlags,
    positive_signals: positiveSignals,
    green_flags: greenFlags,
    recommendations: raw.recommendations || ['Follow standard cybersecurity diligence before providing sensitive information.'],
    verification_audit: raw.verification_audit || null,
    technical_checks: technicalChecks,
    url_intelligence: urlIntelligence,
    scores,
    categories,
    job,
    content_analyzed: raw.content_analyzed !== undefined ? raw.content_analyzed : true,
    fetch_status: raw.fetch_status || 'FETCH_SUCCESS',
  };
}

/**
 * Scan a candidate posting or recruitment URL through HireShield's Risk Engine.
 * Primary endpoint: POST /api/risk/analyze (matches STEP 7)
 * Graceful fallback: POST /api/scan
 *
 * @param {string} url - Target URL to analyze
 * @returns {Promise<Object>} Formatted risk intelligence report
 */
export async function scanJobUrl(url) {
  const cleanUrl = (url || '').trim();
  let response;

  try {
    // Primary path: POST /api/risk/analyze with { url }
    response = await apiClient.post('/api/risk/analyze', {
      url: cleanUrl,
    });
  } catch (err) {
    // If /api/risk/analyze returns 404 or fails, fall back to /api/scan
    if (err.status === 404) {
      console.warn('POST /api/risk/analyze not found, trying POST /api/scan...');
      response = await apiClient.post('/api/scan', { url: cleanUrl });
    } else {
      throw err;
    }
  }

  const normalized = normalizeRiskReport(response.data, {
    url: cleanUrl,
    inputType: 'URL',
  });

  saveScanToSession(normalized);

  return {
    ...normalized,
    latencyMs: response.latencyMs,
  };
}

/**
 * Direct invocation of HireShield's Advanced Multi-Vector Risk Engine.
 * Matches backend Pydantic model RiskAnalyzeRequest:
 * { url, job_text, company_name, recruiter_email, salary, source }
 * Endpoint: POST /api/risk/analyze
 *
 * @param {Object} payload
 * @returns {Promise<Object>} Formatted risk intelligence report
 */
export async function analyzeJobRisk({
  url,
  job_text,
  company_name,
  recruiter_email,
  salary,
  source = 'direct',
}) {
  const payload = {
    url: url || undefined,
    job_text: job_text || undefined,
    company_name: company_name || undefined,
    recruiter_email: recruiter_email || undefined,
    salary: salary || undefined,
    source,
  };

  const response = await apiClient.post('/api/risk/analyze', payload);
  const normalized = normalizeRiskReport(response.data, {
    url,
    company: company_name,
    text: job_text,
    inputType: url ? 'URL' : 'TEXT',
  });

  saveScanToSession(normalized);

  return {
    ...normalized,
    latencyMs: response.latencyMs,
  };
}

/**
 * Analyze browser-supplied job page content via verified fallback endpoint:
 * POST /api/scanner/analyze-content (also available as /api/scan/content)
 * 
 * @param {Object} payload - { url, title, company, content }
 * @returns {Promise<Object>} Formatted risk intelligence report
 */
export async function analyzePageContent({ url = '', title = '', company = '', content }) {
  const response = await apiClient.post('/api/scanner/analyze-content', {
    url: url || '',
    title: title || '',
    company: company || '',
    content: content || '',
  });

  const normalized = normalizeRiskReport(response.data, {
    url,
    title,
    company,
    text: content,
    inputType: url ? 'URL' : 'TEXT',
  });

  saveScanToSession(normalized);

  return {
    ...normalized,
    latencyMs: response.latencyMs,
  };
}

/**
 * Analyze raw pasted job description or recruitment message text.
 * Routes directly to existing live backend endpoints:
 * Primary: POST /api/scanner/analyze-content (verified 200 on Railway)
 * Secondary: POST /api/risk/analyze with { job_text, company_name }
 *
 * @param {Object} payload - { text, title, company }
 * @returns {Promise<Object>} Formatted risk intelligence report
 */
export async function scanJobText({ text, title = '', company = '' }) {
  const cleanText = (text || '').trim();
  let response;

  try {
    // Primary path: /api/scanner/analyze-content is deployed and verified on Railway
    response = await apiClient.post('/api/scanner/analyze-content', {
      url: '',
      title: title || '',
      company: company || '',
      content: cleanText,
    }, {
      timeout: 25000,
    });
  } catch (err) {
    if (err.status === 404) {
      // Fallback path: POST /api/risk/analyze with { job_text, company_name }
      response = await apiClient.post('/api/risk/analyze', {
        job_text: cleanText,
        company_name: company || undefined,
        source: 'text_input',
      }, {
        timeout: 25000,
      });
    } else {
      throw err;
    }
  }

  const normalized = normalizeRiskReport(response.data, {
    text: cleanText,
    title,
    company,
    inputType: 'TEXT',
  });

  saveScanToSession(normalized);

  return {
    ...normalized,
    latencyMs: response.latencyMs,
  };
}

/**
 * Analyze a Google Form or recruitment form URL.
 * Routes to existing live backend endpoint: POST /api/scan or POST /api/risk/analyze
 *
 * @param {string} url - Target Google Form URL
 * @returns {Promise<Object>} Formatted risk intelligence report
 */
export async function scanJobForm(url) {
  const cleanUrl = (url || '').trim();
  let response;

  try {
    // The deployed /api/scan endpoint natively evaluates form URLs through Risk Engine
    response = await apiClient.post('/api/scan', { url: cleanUrl }, {
      timeout: 25000,
    });
  } catch (err) {
    if (err.status === 404) {
      response = await apiClient.post('/api/risk/analyze', {
        url: cleanUrl,
        source: 'google_forms',
      }, {
        timeout: 25000,
      });
    } else {
      throw err;
    }
  }

  const normalized = normalizeRiskReport(response.data, {
    url: cleanUrl,
    inputType: 'GOOGLE_FORM',
  });

  saveScanToSession(normalized);

  return {
    ...normalized,
    latencyMs: response.latencyMs,
  };
}

/**
 * Helper: Extract digital text from a PDF file in browser if backend endpoint is unavailable.
 */
async function extractDigitalTextFromPdf(file) {
  try {
    const arrayBuffer = await file.arrayBuffer();
    const bytes = new Uint8Array(arrayBuffer);
    const maxBytes = Math.min(bytes.byteLength, 4 * 1024 * 1024);
    let binary = '';
    for (let i = 0; i < maxBytes; i++) {
      binary += String.fromCharCode(bytes[i]);
    }

    const textPieces = [];
    const tjRegex = /\(([^)\\]*(?:\\.[^)\\]*)*)\)\s*(?:Tj|'|")/g;
    let match;
    while ((match = tjRegex.exec(binary)) !== null) {
      const cleanPiece = match[1]
        .replace(/\\([0-7]{1,3})/g, (_, oct) => String.fromCharCode(parseInt(oct, 8)))
        .replace(/\\([()\\])/g, '$1')
        .replace(/\\r/g, ' ')
        .replace(/\\n/g, ' ')
        .replace(/\\t/g, ' ');
      if (cleanPiece.trim().length > 0) {
        textPieces.push(cleanPiece);
      }
    }

    const combined = textPieces.join(' ').replace(/\s+/g, ' ').trim();
    return combined;
  } catch {
    return '';
  }
}

/**
 * Analyze a job/offer PDF document.
 * Tries POST /api/scanner/analyze-pdf first.
 * If backend returns 404 (endpoint not deployed on Railway yet), extracts digital text
 * and routes cleanly through /api/scanner/analyze-content without throwing a 404.
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

  try {
    const response = await apiClient.post('/api/scanner/analyze-pdf', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      timeout: 30000,
    });

    const normalized = normalizeRiskReport(response.data, {
      title: title || file.name,
      company,
      inputType: 'PDF',
    });

    saveScanToSession(normalized);

    return {
      ...normalized,
      latencyMs: response.latencyMs,
    };
  } catch (err) {
    // If backend returns 404, fall back to browser-side text extraction + content analysis
    if (err.status === 404) {
      console.warn('Endpoint /api/scanner/analyze-pdf returned 404. Initiating digital text extraction fallback...');
      const extractedText = await extractDigitalTextFromPdf(file);

      if (extractedText && extractedText.length >= 25) {
        return await analyzePageContent({
          url: '',
          title: title || file.name.replace(/\.[^/.]+$/, ''),
          company,
          content: extractedText,
        });
      }

      // If document is scanned / image-based (no readable digital text streams)
      return {
        success: false,
        status: 'NO_EXTRACTABLE_TEXT',
        score: null,
        risk_score: null,
        risk_level: 'INCOMPLETE',
        verdict: 'INCOMPLETE',
        input_type: 'PDF',
        inputType: 'PDF',
        message: 'No digital text could be extracted from this scanned or image-based document.',
        summary: 'No digital text could be extracted from this scanned or image-based document.',
        explanation: 'Scanned image PDF detected. Please copy the text into the Paste Job Text tab.',
        fallback_available: true,
        is_scanned_image: true,
        filename: file.name,
        signals: [],
        red_flags: [],
        categories: {},
        recommendations: [
          'Use the Paste Job Text scanner tab to copy and paste the readable text.',
          'If this is a physical paper document, type the key terms, salary claims, and requested fees into HireShield.',
          'Do not pay any upfront fees or transfer money requested in unverified documents.',
        ],
      };
    }
    throw err;
  }
}

/**
 * Check backend liveness.
 * Calls actual backend endpoints: GET /health or GET /api/health
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
