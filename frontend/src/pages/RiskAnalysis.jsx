import React, { useState, useEffect } from 'react';
import { useLocation, useParams, Link } from 'react-router-dom';
import { 
  Shield, 
  Search, 
  Play, 
  RefreshCw, 
  AlertTriangle, 
  AlertOctagon, 
  CheckCircle2, 
  ExternalLink, 
  ArrowLeft,
  FileText,
  Download,
  Copy,
  Check,
  Globe,
  Terminal as TerminalIcon,
  HelpCircle,
  ShieldAlert,
  Send,
  Sparkles,
  Info,
  Lock
} from 'lucide-react';
import { 
  scanJobUrl, 
  analyzePageContent, 
  scanJobPdf, 
  scanJobForm, 
  scanJobText 
} from '../api/analysis';
import { getCandidateById } from '../api/candidates';
import { API_BASE_URL } from '../api/client';
import { generatePdfReport } from '../utils/generatePdfReport';
import RadialScoreGauge from '../components/RiskScore/RadialScoreGauge';
import RiskBreakdownBars from '../components/RiskBreakdown/RiskBreakdownBars';
import RedFlagsList from '../components/RiskAnalysis/RedFlagsList';
import GreenFlagsList from '../components/RiskAnalysis/GreenFlagsList';
import TechnicalChecks from '../components/RiskAnalysis/TechnicalChecks';
import AITerminal from '../components/RiskAnalysis/AITerminal';
import BrowserFallbackModal from '../components/RiskAnalysis/BrowserFallbackModal';
import VerificationAudit from '../components/RiskAnalysis/VerificationAudit';
import MultiInputScanner from '../components/RiskAnalysis/MultiInputScanner';
import RiskCategoryPillars from '../components/RiskAnalysis/RiskCategoryPillars';
import ExecutiveSummaryAdvisory from '../components/RiskAnalysis/ExecutiveSummaryAdvisory';

export default function RiskAnalysis() {
  const { id } = useParams();
  const location = useLocation();

  // Multi-input selector state: 'URL' | 'PDF' | 'FORM' | 'TEXT'
  const [activeTab, setActiveTab] = useState('URL');
  const [specialNotice, setSpecialNotice] = useState(null);

  // URL state
  const [targetUrl, setTargetUrl] = useState('');
  const [scanning, setScanning] = useState(false);
  const [error, setError] = useState(null);
  const [report, setReport] = useState(null);
  const [copied, setCopied] = useState(false);

  // Fallback modal state for blocked pages (e.g. HTTP 403)
  const [showFallbackModal, setShowFallbackModal] = useState(false);
  const [fallbackInitialTitle, setFallbackInitialTitle] = useState('');
  const [fallbackInitialCompany, setFallbackInitialCompany] = useState('');

  // Preset test targets
  const presets = [
    {
      label: 'Apple Careers (Protected Target)',
      url: 'https://jobs.apple.com/en-us/details/200684375-1052/integration-engineering-software-engineer?team=SFTWR',
      desc: 'Corporate WAF (HTTP 403 Access Limited / No Fraud Penalty)',
    },
    {
      label: 'Clean Example Target',
      url: 'https://example.com/',
      desc: 'Legitimate baseline (0 Score / LOW)',
    },
    {
      label: 'Python Software Foundation',
      url: 'https://www.python.org/',
      desc: 'Established SSL & DNS infrastructure',
    },
  ];

  // If navigated with initialUrl, ID parameter, or query ID
  useEffect(() => {
    const searchParams = new URLSearchParams(location.search);
    const searchUrl = searchParams.get('url');
    const queryId = searchParams.get('id');
    const targetId = id || queryId;

    if (targetId) {
      if (searchUrl) setTargetUrl(searchUrl);
      loadCandidate(targetId);
    } else if (location.state?.candidateData) {
      setReport(location.state.candidateData);
      setTargetUrl(location.state.candidateData.url || '');
    } else if (searchUrl) {
      setTargetUrl(searchUrl);
      executeScan(searchUrl);
    } else if (location.state?.initialUrl) {
      setTargetUrl(location.state.initialUrl);
      executeScan(location.state.initialUrl);
    } else {
      // Default initial target: Apple Careers to demonstrate 403 access limitation handling
      setTargetUrl('https://jobs.apple.com/en-us/details/200684375-1052/integration-engineering-software-engineer?team=SFTWR');
    }
  }, [id, location.state, location.search]);

  const loadCandidate = async (candId) => {
    setScanning(true);
    setError(null);
    setSpecialNotice(null);
    try {
      const data = await getCandidateById(candId);
      setReport({
        ...data,
        content_analyzed: true,
        fetch_status: data.fetch_status || 'FETCH_SUCCESS',
      });
      setTargetUrl(data.url || '');
    } catch (err) {
      setError({
        message: err.message || 'Unable to locate candidate dossier.',
      });
    } finally {
      setScanning(false);
    }
  };

  const executeScan = async (urlToScan) => {
    const url = (urlToScan || targetUrl).trim();
    if (!url) return;

    setScanning(true);
    setError(null);
    setSpecialNotice(null);
    setShowFallbackModal(false);

    try {
      const result = await scanJobUrl(url);
      setReport(result);
      // If blocked, pre-fill fallback URL and sample company if detectable
      if (result.fetch_status === 'FETCH_BLOCKED' || !result.content_analyzed) {
        if (url.includes('apple.com')) {
          setFallbackInitialCompany('Apple Inc.');
          setFallbackInitialTitle('Integration Engineering Software Engineer');
        } else {
          setFallbackInitialCompany('');
          setFallbackInitialTitle('');
        }
      }
    } catch (err) {
      console.error('Scan failed', err);
      setError({
        message: err.message || 'Threat scan failed.',
        detail: err.detail || 'The backend could not complete extraction.',
        status: err.status,
        isNetworkError: err.isNetworkError,
      });
      setReport(null);
    } finally {
      setScanning(false);
    }
  };

  const handleScanUrl = (urlToScan) => {
    executeScan(urlToScan);
  };

  const handleScanPdf = async (file, meta = {}) => {
    if (!file) return;
    setScanning(true);
    setError(null);
    setSpecialNotice(null);
    try {
      const result = await scanJobPdf(file, meta);
      if (result.success === false && result.status === 'NO_EXTRACTABLE_TEXT') {
        setSpecialNotice({
          type: 'SCANNED_PDF',
          title: 'Image-Based / Scanned PDF Detected',
          message: result.message || 'No digital text could be extracted from this scanned or image-based document.',
          recommendation: 'Optical Character Recognition (OCR) fallback is available. You can also paste the document text directly for immediate evaluation.',
        });
        setReport(null);
      } else {
        setReport(result);
      }
    } catch (err) {
      console.error('PDF scan failed', err);
      setError({
        message: err.message || 'PDF threat evaluation failed.',
        detail: err.detail || 'Could not parse the uploaded document.',
        status: err.status,
      });
      setReport(null);
    } finally {
      setScanning(false);
    }
  };

  const handleScanForm = async (url) => {
    if (!url) return;
    setScanning(true);
    setError(null);
    setSpecialNotice(null);
    try {
      const result = await scanJobForm(url);
      if (result.success === false) {
        setSpecialNotice({
          type: 'FORM_RESTRICTED',
          title: 'Google Form Access Restricted',
          message: result.message || 'Unable to access the form automatically. The form may require sign-in or be restricted.',
          recommendation: 'Paste the form questions or recruitment text directly into HireShield for instant risk analysis.',
        });
        setReport(null);
      } else {
        setReport(result);
      }
    } catch (err) {
      console.error('Form scan failed', err);
      setError({
        message: err.message || 'Google Form threat scan failed.',
        detail: err.detail || 'Unable to retrieve form contents.',
        status: err.status,
      });
      setReport(null);
    } finally {
      setScanning(false);
    }
  };

  const handleScanText = async ({ text, title, company }) => {
    if (!text || text.trim().length < 15) return;
    setScanning(true);
    setError(null);
    setSpecialNotice(null);
    try {
      const result = await scanJobText({ text, title, company });
      setReport(result);
    } catch (err) {
      console.error('Text scan failed', err);
      setError({
        message: err.message || 'Job text evaluation failed.',
        detail: err.detail || 'Could not process text input.',
        status: err.status,
      });
      setReport(null);
    } finally {
      setScanning(false);
    }
  };

  const handleFallbackSubmit = async ({ url, title, company, content }) => {
    const result = await analyzePageContent({
      url: url || report?.final_url || report?.url || targetUrl,
      title,
      company,
      content,
    });
    setReport(result);
    return result;
  };

  const handleCopyReport = () => {
    if (!report) return;
    navigator.clipboard.writeText(JSON.stringify(report, null, 2));
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const isAccessLimited = report && (
    report.fetch_status === 'FETCH_BLOCKED' ||
    report.fetch_status === 'FETCH_RATE_LIMITED' ||
    report.fetch_status === 'FETCH_SERVER_ERROR' ||
    report.fetch_status === 'FETCH_TIMEOUT' ||
    (!report.content_analyzed && report.fetch_status !== 'FETCH_INVALID_URL')
  );

  return (
    <div className="space-y-8 font-sans pb-16">
      {/* 1. Multi-Input Scanner Control Panel */}
      <MultiInputScanner
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        scanning={scanning}
        targetUrl={targetUrl}
        setTargetUrl={setTargetUrl}
        onScanUrl={handleScanUrl}
        onScanPdf={handleScanPdf}
        onScanForm={handleScanForm}
        onScanText={handleScanText}
        presets={presets}
      />

      {/* Special Notice Banner (e.g. Scanned / Image-Based PDF or Restricted Google Form) */}
      {specialNotice && (
        <div className="p-6 rounded-2xl bg-surface-100 border border-brand-primary/40 glass-panel space-y-4 font-sans animate-fadeIn">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-xl bg-risk-medium/15 text-risk-medium border border-risk-medium/30">
              <AlertTriangle className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center gap-2 font-mono text-xs text-risk-medium font-bold uppercase">
                <span>{specialNotice.title}</span>
                <span className="px-2 py-0.5 rounded-full text-[10px] bg-risk-low/10 text-risk-low border border-risk-low/30">
                  ACTION REQUIRED
                </span>
              </div>
              <p className="text-sm font-semibold text-white mt-0.5">
                {specialNotice.message}
              </p>
            </div>
          </div>
          <div className="p-4 rounded-xl bg-surface-200/80 border border-surface-border text-xs text-text-secondary flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div className="flex items-center gap-2">
              <Info className="w-4 h-4 text-brand-light flex-shrink-0" />
              <span>{specialNotice.recommendation}</span>
            </div>
            <button
              type="button"
              onClick={() => {
                setActiveTab('TEXT');
                setSpecialNotice(null);
              }}
              className="px-4 py-2 rounded-lg bg-brand-primary hover:bg-brand-light text-white font-mono text-xs font-bold tracking-wider flex items-center gap-2 shadow-cyber transition-all flex-shrink-0 cursor-pointer"
            >
              <FileText className="w-3.5 h-3.5" />
              <span>Switch to Paste Job Text</span>
            </button>
          </div>
        </div>
      )}

      {/* Error Alert Box (Categorized failure feedback) */}
      {error && (
        <div className="p-5 rounded-xl bg-risk-critical/10 border border-risk-critical/30 text-xs font-mono text-risk-critical space-y-2">
          <div className="flex items-center gap-2 font-bold tracking-wide text-sm">
            <AlertOctagon className="w-4 h-4" />
            <span>
              {error.status === 401 || error.status === 403
                ? `AUTHENTICATION FAULT // HTTP ${error.status}`
                : error.status === 404
                ? 'ENDPOINT NOT FOUND // HTTP 404'
                : error.status >= 500
                ? `BACKEND SERVER FAULT // HTTP ${error.status}`
                : error.isTimeout
                ? 'NETWORK TIMEOUT // ENGINE DELAY'
                : `COMMUNICATION FAULT // ${error.status || 'OFFLINE'}`}
            </span>
          </div>
          <p className="text-text-primary text-xs leading-relaxed">
            {error.message}
          </p>
          {error.detail && (
            <div className="p-3 rounded bg-surface-300/80 border border-surface-border text-text-secondary text-[11px] leading-relaxed">
              {typeof error.detail === 'string' ? error.detail : JSON.stringify(error.detail)}
            </div>
          )}
        </div>
      )}

      {/* Loading Scanning State */}
      {scanning && (
        <div className="p-12 rounded-2xl bg-surface-100 border border-surface-border text-center space-y-5">
          <div className="w-16 h-16 rounded-2xl bg-brand-primary/10 border border-brand-primary/40 flex items-center justify-center text-brand-primary mx-auto shadow-cyber animate-pulse">
            <Shield className="w-8 h-8 animate-bounce" />
          </div>
          <div>
            <div className="text-sm font-bold font-mono text-white tracking-wider">
              RUNNING HIRESHIELD THREAT EXTRACTION...
            </div>
            <p className="text-xs text-text-muted mt-1 font-mono">
              Layer A URL Intelligence &bull; SSL Validation &bull; DNS Query &bull; Heuristic Layer B Parsing
            </p>
          </div>
        </div>
      )}

      {/* 2. THE STAR REPORT INTERFACE: RENDERS ACTUAL BACKEND RESPONSE */}
      {!scanning && report && (
        <div className="space-y-6">

          {/* PAGE ACCESS LIMITED CYBER PANEL (Triggered on HTTP 403 / WAF / Automated Block) */}
          {isAccessLimited && (
            <div className="p-6 rounded-2xl bg-surface-100 border border-brand-primary/40 glass-panel space-y-5">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-surface-border pb-4">
                <div className="flex items-center gap-3">
                  <div className="p-2.5 rounded-xl bg-risk-medium/10 text-risk-medium border border-risk-medium/30">
                    <ShieldAlert className="w-6 h-6" />
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="font-mono text-xs font-bold text-risk-medium uppercase tracking-wider">
                        PAGE ACCESS LIMITED // {report.http_status ? `HTTP ${report.http_status}` : report.fetch_status}
                      </span>
                      <span className="px-2 py-0.5 rounded-full text-[10px] font-mono bg-risk-low/10 text-risk-low border border-risk-low/30">
                        NOT FRAUD EVIDENCE
                      </span>
                    </div>
                    <h3 className="text-lg font-bold text-white mt-0.5">
                      Automated Access Restricted by Target Website
                    </h3>
                  </div>
                </div>

                <button
                  type="button"
                  onClick={() => setShowFallbackModal(true)}
                  className="px-4 py-2.5 rounded-lg bg-brand-primary hover:bg-brand-light text-white font-mono text-xs font-semibold tracking-wider flex items-center gap-2 shadow-cyber transition-all cursor-pointer flex-shrink-0"
                >
                  <FileText className="w-4 h-4" />
                  <span>ANALYZE CURRENT PAGE CONTENT</span>
                </button>
              </div>

              <div className="text-xs text-text-secondary leading-relaxed space-y-2">
                <p>
                  The target website server returned <strong>{report.http_status ? `HTTP ${report.http_status}` : report.fetch_status}</strong>, denying automated server-side scraping via its security policy (e.g. Cloudflare, Akamai, or corporate WAF protections).
                </p>
                <div className="p-3 rounded-lg bg-surface-200/80 border border-surface-border text-[11px] text-text-muted font-mono flex items-center gap-2">
                  <Info className="w-4 h-4 text-brand-light flex-shrink-0" />
                  <span>
                    <strong>HireShield Policy:</strong> Access restriction is NOT treated as evidence of fraud. Zero penalty has been added to the candidate risk score.
                  </span>
                </div>
              </div>

              {/* Layer A vs Layer B Status Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs font-mono">
                {/* Layer A: URL Intelligence */}
                <div className="p-4 rounded-xl bg-surface-200/80 border border-surface-border space-y-2.5">
                  <div className="text-[11px] text-risk-low font-bold uppercase tracking-wider flex items-center gap-1.5">
                    <CheckCircle2 className="w-4 h-4" />
                    <span>Layer A: URL & Infrastructure (Completed)</span>
                  </div>
                  <ul className="space-y-1.5 text-text-muted text-[11px]">
                    <li className="flex items-center justify-between">
                      <span>Target Hostname:</span>
                      <span className="text-white font-semibold">{report.url_intelligence?.domain || 'Identified'}</span>
                    </li>
                    <li className="flex items-center justify-between">
                      <span>Protocol Security:</span>
                      <span className="text-white font-semibold">{report.url_intelligence?.is_https ? 'HTTPS Verified' : 'Insecure HTTP'}</span>
                    </li>
                    <li className="flex items-center justify-between">
                      <span>DNS Resolution:</span>
                      <span className="text-white font-semibold">{report.url_intelligence?.dns_exists ? 'Resolved' : 'No DNS Record'}</span>
                    </li>
                    <li className="flex items-center justify-between">
                      <span>SSL Certificate:</span>
                      <span className="text-white font-semibold">{report.technical_checks?.ssl_valid ? 'Valid & Trusted' : 'Invalid / Missing'}</span>
                    </li>
                    <li className="flex items-center justify-between">
                      <span>Domain Registration Age:</span>
                      <span className="text-white font-semibold">{report.technical_checks?.domain_age_days ? `${report.technical_checks.domain_age_days} days` : 'Not available'}</span>
                    </li>
                  </ul>
                </div>

                {/* Layer B: Content NLP */}
                <div className="p-4 rounded-xl bg-surface-200/80 border border-surface-border space-y-2.5">
                  <div className="text-[11px] text-text-muted font-bold uppercase tracking-wider flex items-center gap-1.5">
                    <AlertTriangle className="w-4 h-4 text-risk-medium" />
                    <span>Layer B: Page Content & NLP (Unavailable)</span>
                  </div>
                  <ul className="space-y-1.5 text-text-muted text-[11px]">
                    <li className="flex items-center justify-between">
                      <span>Recruitment Body Text:</span>
                      <span className="text-text-muted">Blocked by remote WAF</span>
                    </li>
                    <li className="flex items-center justify-between">
                      <span>Compensation & Fee Detection:</span>
                      <span className="text-text-muted">Awaiting browser content</span>
                    </li>
                    <li className="flex items-center justify-between">
                      <span>Linguistic Urgency Analysis:</span>
                      <span className="text-text-muted">Awaiting browser content</span>
                    </li>
                    <li className="flex items-center justify-between">
                      <span>Sensitive Identity Screening:</span>
                      <span className="text-text-muted">Awaiting browser content</span>
                    </li>
                    <li className="flex items-center justify-between">
                      <span>Browser Content Fallback:</span>
                      <span className="text-brand-light font-semibold">Ready for submission</span>
                    </li>
                  </ul>
                </div>
              </div>
            </div>
          )}

          {/* BROWSER FALLBACK SUCCESS BANNER */}
          {report.content_intelligence?.source === 'browser_fallback' && (
            <div className="p-5 rounded-2xl bg-surface-100 border border-brand-primary/40 glass-panel flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <div className="flex items-center gap-3">
                <div className="p-2.5 rounded-xl bg-risk-low/10 text-risk-low border border-risk-low/30">
                  <CheckCircle2 className="w-6 h-6" />
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-xs font-bold text-brand-light uppercase tracking-wider">
                      BROWSER CONTENT FALLBACK APPLIED
                    </span>
                    <span className="px-2 py-0.5 rounded-full text-[10px] font-mono bg-risk-low/10 text-risk-low border border-risk-low/30 font-bold">
                      ASSESSMENT COMPLETE
                    </span>
                  </div>
                  <h3 className="text-base font-bold text-white mt-0.5">
                    Multi-Layer Risk Engine Evaluation Synthesized
                  </h3>
                  <p className="text-xs text-text-muted mt-0.5 font-sans">
                    Retained original Layer A infrastructure (SSL, DNS, Domain Age) and combined with Layer B browser text heuristics.
                  </p>
                </div>
              </div>

              <button
                type="button"
                onClick={() => setShowFallbackModal(true)}
                className="px-4 py-2 rounded-lg bg-surface-200 hover:bg-surface-300 border border-surface-border text-text-secondary hover:text-white font-mono text-xs flex items-center gap-2 transition-colors cursor-pointer flex-shrink-0 self-start sm:self-auto"
              >
                <RefreshCw className="w-3.5 h-3.5" />
                <span>Update Job Text</span>
              </button>
            </div>
          )}

          {/* Target Metadata Banner */}
          <div className="p-5 rounded-xl bg-surface-100 border border-surface-border flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div className="min-w-0">
              <div className="flex items-center gap-2 font-mono text-[11px] text-brand-light mb-1 flex-wrap">
                <span>TARGET IDENTIFIER: {report.id || 'LIVE-SCAN-SESSION'}</span>
                <span className="px-1.5 py-0.2 rounded bg-surface-200 text-text-muted border border-surface-border">
                  {report.fetch_status || 'LIVE'}
                </span>
                <span className="px-2 py-0.5 rounded font-mono font-bold text-[10px] bg-brand-primary/20 text-brand-light border border-brand-primary/40 uppercase">
                  {report.input_type === 'PDF' ? '📄 PDF Document' :
                   report.input_type === 'GOOGLE_FORM' ? '📝 Google Form' :
                   report.input_type === 'TEXT' ? '✍️ Pasted Text' :
                   '🌐 Website URL'}
                </span>
                {report.content_analyzed ? (
                  <span className="px-1.5 py-0.2 rounded bg-risk-low/10 text-risk-low border border-risk-low/30">
                    LAYER B ANALYZED
                  </span>
                ) : (
                  <span className="px-1.5 py-0.2 rounded bg-risk-medium/10 text-risk-medium border border-risk-medium/30">
                    LAYER A ONLY
                  </span>
                )}
              </div>
              <h3 className="text-lg font-bold text-white truncate font-sans">
                {report.job?.title || 'Target Job Extraction'}
              </h3>
              <div className="flex items-center gap-2 font-mono text-xs text-text-muted mt-0.5 truncate">
                {report.input_type === 'PDF' ? (
                  <div className="flex items-center gap-1.5 truncate">
                    <FileText className="w-3.5 h-3.5 text-brand-light flex-shrink-0" />
                    <span className="truncate">{report.job?.title || 'Uploaded Document'} {report.job?.company ? `(${report.job.company})` : ''}</span>
                  </div>
                ) : report.input_type === 'TEXT' ? (
                  <div className="flex items-center gap-1.5 truncate">
                    <FileText className="w-3.5 h-3.5 text-brand-light flex-shrink-0" />
                    <span className="truncate">Ingested Text Snippet {report.job?.company ? `&bull; ${report.job.company}` : ''}</span>
                  </div>
                ) : (
                  <>
                    <Globe className="w-3.5 h-3.5 flex-shrink-0" />
                    <a 
                      href={report.final_url || report.url} 
                      target="_blank" 
                      rel="noreferrer"
                      className="truncate hover:text-brand-light transition-colors flex items-center gap-1"
                    >
                      <span className="truncate">{report.final_url || report.url}</span>
                      <ExternalLink className="w-3 h-3 flex-shrink-0" />
                    </a>
                  </>
                )}
              </div>
            </div>

            <div className="flex items-center gap-2 sm:gap-3 font-mono text-xs flex-wrap md:flex-nowrap flex-shrink-0">
              {report.verdict && (
                <div className="p-2.5 rounded-lg bg-surface-200 border border-surface-border text-center min-w-[100px]">
                  <div className="text-[10px] text-text-muted">CLASSIFICATION</div>
                  <div className={`font-bold mt-0.5 ${
                    report.verdict === 'CONFIRMED_SCAM' ? 'text-risk-critical' :
                    report.verdict === 'HIGH_RISK_FAKE' ? 'text-risk-high' :
                    report.verdict === 'SUSPICIOUS' ? 'text-risk-medium' :
                    'text-risk-low'
                  }`}>
                    {report.verdict.replace('_', ' ')}
                  </div>
                </div>
              )}

              {report.fake_job_probability !== null && report.fake_job_probability !== undefined && (
                <div className="p-2.5 rounded-lg bg-surface-200 border border-surface-border text-center">
                  <div className="text-[10px] text-text-muted">SCAM PROBABILITY</div>
                  <div className={`font-bold mt-0.5 ${
                    report.fake_job_probability >= 70 ? 'text-risk-critical' :
                    report.fake_job_probability >= 40 ? 'text-risk-high' :
                    report.fake_job_probability >= 20 ? 'text-risk-medium' :
                    'text-risk-low'
                  }`}>
                    {report.fake_job_probability}%
                  </div>
                </div>
              )}

              <div className="p-2.5 rounded-lg bg-surface-200 border border-surface-border text-center">
                <div className="text-[10px] text-text-muted">RISK LEVEL</div>
                <div className={`font-bold mt-0.5 ${
                  report.risk_level === 'CRITICAL' ? 'text-risk-critical' :
                  report.risk_level === 'HIGH' ? 'text-risk-high' :
                  report.risk_level === 'MEDIUM' ? 'text-risk-medium' :
                  report.risk_level === 'INCOMPLETE' ? 'text-risk-medium' : 'text-risk-low'
                }`}>
                  {report.risk_level || (report.content_analyzed ? 'LOW' : 'INCOMPLETE')}
                </div>
              </div>

              <div className="p-2.5 rounded-lg bg-surface-200 border border-surface-border text-center">
                <div className="text-[10px] text-text-muted">RISK SCORE</div>
                <div className="font-bold text-white mt-0.5">
                  {report.risk_score !== null && report.risk_score !== undefined ? `${report.risk_score} / 100` : 'N/A'}
                </div>
              </div>

              <button
                type="button"
                onClick={() => generatePdfReport(report)}
                className="p-2.5 rounded-lg bg-brand-primary/10 hover:bg-brand-primary/20 border border-brand-primary/30 text-brand-light hover:text-white transition-all flex flex-col items-center justify-center text-center cursor-pointer min-w-[85px] shadow-sm"
                title="Download Executive Security Audit PDF Report"
              >
                <Download className="w-4 h-4 mb-0.5 text-brand-light" />
                <span className="text-[10px] font-bold tracking-wider">GET PDF</span>
              </button>
            </div>
          </div>

          {/* Executive Summary & Practical Safety Advisory */}
          <ExecutiveSummaryAdvisory
            summary={report.summary}
            recommendations={report.recommendations}
            riskLevel={report.risk_level}
            riskScore={report.risk_score}
            inputType={report.input_type || 'URL'}
          />

          {/* 4-Pillar Risk Categories Breakdown (Financial, Identity, Behavioral, Technical) */}
          {report.categories && (
            <RiskCategoryPillars
              categories={report.categories}
              inputType={report.input_type || 'URL'}
            />
          )}

          {/* Central Risk Dossier Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            {/* Left: Overall Risk Score Radial Indicator */}
            <div className="lg:col-span-4 p-6 rounded-xl bg-surface-100 border border-surface-border glass-panel flex flex-col items-center justify-center text-center space-y-4">
              <div className="w-full flex items-center justify-between font-mono text-xs text-text-muted mb-2">
                <span>RADIAL METRIC</span>
                <span className="text-brand-light">v1.0 WEIGHTED</span>
              </div>

              <RadialScoreGauge
                score={report.risk_score}
                level={report.risk_level || (report.content_analyzed ? 'LOW' : 'INCOMPLETE')}
                contentAnalyzed={report.content_analyzed}
                size={210}
                strokeWidth={15}
              />

              <div className="p-3 rounded-lg bg-surface-200/60 border border-surface-border w-full font-mono text-xs text-text-muted space-y-1">
                <div className="flex justify-between">
                  <span>Audit Status:</span>
                  <span className="text-white font-bold">{report.content_analyzed ? 'Full Multi-Layer Assessment' : 'Layer A Infrastructure Only'}</span>
                </div>
                <div className="flex justify-between">
                  <span>Classification:</span>
                  <span className={`font-bold ${report.content_analyzed ? 'text-white' : 'text-risk-medium'}`}>
                    {report.content_analyzed ? `${report.risk_level} RISK` : 'INCOMPLETE (Awaiting Content)'}
                  </span>
                </div>
              </div>
            </div>

            {/* Right: Weighted Risk Breakdown */}
            <div className="lg:col-span-8 p-6 rounded-xl bg-surface-100 border border-surface-border glass-panel">
              <RiskBreakdownBars
                scores={report.scores || {}}
                redFlags={report.red_flags || []}
                contentAnalyzed={report.content_analyzed}
              />
            </div>
          </div>

          {/* Extracted Text Preview Card */}
          <div className="p-5 rounded-xl bg-surface-100 border border-surface-border space-y-2">
            <div className="flex items-center justify-between">
              <span className="font-mono text-xs font-semibold text-text-secondary uppercase tracking-wider">
                Extracted Job Spec Content
              </span>
              <span className="font-mono text-[11px] text-text-muted">
                {report.content_intelligence?.source === 'browser_fallback' ? 'Browser Fallback Source' : 'HTTPX Scraper Output'}
              </span>
            </div>
            <div className="p-4 rounded-lg bg-surface-200/80 border border-surface-border text-xs text-text-secondary leading-relaxed font-sans max-h-36 overflow-y-auto">
              {report.job?.text_preview || 'No text snippet preview extracted from target.'}
            </div>
          </div>

          {/* AI Terminal & Heuristic Analysis */}
          <div className="space-y-3">
            <AITerminal
              job={report.job}
              scores={report.scores}
              redFlags={report.red_flags}
              contentAnalyzed={report.content_analyzed}
              fetchStatus={report.fetch_status}
              httpStatus={report.http_status}
              contentSource={report.content_intelligence?.source || (report.fetch_status === 'BROWSER_CONTENT_RECEIVED' ? 'browser_fallback' : 'server_fetch')}
              pipelineStages={report.pipeline_stages || []}
              isLoading={false}
            />
          </div>

          {/* Verification Audit: Why Real / Fake, What Checked & How Verified */}
          {report.verification_audit && (
            <VerificationAudit audit={report.verification_audit} />
          )}

          {/* Bottom Grid: Red Flags, Green Flags & Technical Checks */}
          <div className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
              <div className="lg:col-span-6 p-6 rounded-xl bg-surface-100 border border-surface-border glass-panel">
                <RedFlagsList redFlags={report.red_flags || []} />
              </div>

              <div className="lg:col-span-6 p-6 rounded-xl bg-surface-100 border border-surface-border glass-panel">
                <GreenFlagsList 
                  greenFlags={report.green_flags || []} 
                  legitimacyScore={report.legitimacy_score}
                />
              </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
              <div className="lg:col-span-6 p-6 rounded-xl bg-surface-100 border border-surface-border glass-panel">
                <TechnicalChecks 
                  checks={report.technical_checks || {}} 
                  inputType={report.input_type || 'URL'} 
                />
              </div>

              <div className="lg:col-span-6 p-6 rounded-xl bg-surface-100 border border-surface-border glass-panel space-y-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Shield className="w-4 h-4 text-brand-light" />
                    <h4 className="text-xs font-mono font-semibold tracking-wider text-text-secondary uppercase">
                      Candidate Diligence & Safety Advisory
                    </h4>
                  </div>
                  <span className="text-[11px] font-mono text-text-muted">
                    Safety
                  </span>
                </div>

                <div className="space-y-2">
                  {(report.recommendations && report.recommendations.length > 0 ? report.recommendations : [
                    "Verify recruiter credentials on official corporate domain.",
                    "Never transfer funds or provide sensitive bank details before formal offer."
                  ]).map((rec, i) => (
                    <div key={i} className="p-3 rounded-lg bg-surface-200/70 border border-surface-border text-xs text-text-primary flex items-start gap-2.5">
                      <CheckCircle2 className="w-4 h-4 text-brand-light mt-0.5 flex-shrink-0" />
                      <span className="leading-relaxed">{rec}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Browser Content Fallback Modal Component */}
      <BrowserFallbackModal
        isOpen={showFallbackModal}
        onClose={() => setShowFallbackModal(false)}
        targetUrl={report?.final_url || report?.url || targetUrl}
        initialTitle={fallbackInitialTitle || report?.job?.title || ''}
        initialCompany={fallbackInitialCompany || report?.job?.company || ''}
        onSubmit={handleFallbackSubmit}
      />
    </div>
  );
}
