import React, { useState, useEffect } from 'react';
import { useParams, useLocation, Link, useNavigate } from 'react-router-dom';
import { 
  ArrowLeft, 
  Globe, 
  ExternalLink, 
  ShieldCheck, 
  AlertTriangle, 
  AlertOctagon, 
  ShieldAlert, 
  FileText,
  Download,
  Calendar,
  Layers,
  Copy,
  Check
} from 'lucide-react';
import { getCandidateById } from '../api/candidates';
import { generatePdfReport } from '../utils/generatePdfReport';
import RadialScoreGauge from '../components/RiskScore/RadialScoreGauge';
import RiskBreakdownBars from '../components/RiskBreakdown/RiskBreakdownBars';
import RedFlagsList from '../components/RiskAnalysis/RedFlagsList';
import TechnicalChecks from '../components/RiskAnalysis/TechnicalChecks';

export default function CandidateDetails() {
  const { id } = useParams();
  const location = useLocation();
  const navigate = useNavigate();

  const [candidate, setCandidate] = useState(null);
  const [loading, setLoading] = useState(true);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    if (location.state?.candidateData) {
      setCandidate(location.state.candidateData);
      setLoading(false);
    } else if (id) {
      loadData(id);
    }
  }, [id, location.state]);

  const loadData = async (candId) => {
    setLoading(true);
    try {
      const data = await getCandidateById(candId);
      setCandidate(data);
    } catch (err) {
      console.error('Failed to load candidate', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCopyJson = () => {
    if (!candidate) return;
    navigator.clipboard.writeText(JSON.stringify(candidate, null, 2));
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  if (loading) {
    return (
      <div className="p-12 text-center font-mono text-xs text-text-muted animate-pulse">
        RETRIEVING CANDIDATE INTELLIGENCE DOSSIER // {id}...
      </div>
    );
  }

  if (!candidate) {
    return (
      <div className="p-8 text-center bg-surface-100 rounded-lg border border-surface-border space-y-4">
        <AlertTriangle className="w-8 h-8 text-amber-400 mx-auto" />
        <h3 className="text-sm font-bold text-white">Candidate Record Not Found</h3>
        <p className="text-xs text-text-muted">
          Could not find an intelligence dossier corresponding to ID '{id}'.
        </p>
        <Link
          to="/candidates"
          className="inline-flex items-center gap-1.5 px-4 py-2 rounded bg-surface-200 text-brand-light font-mono text-xs"
        >
          <ArrowLeft className="w-3.5 h-3.5" />
          <span>Back to Candidate Registry</span>
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-6 font-sans pb-12">
      {/* Top Breadcrumb & Actions */}
      <div className="flex items-center justify-between">
        <Link
          to="/candidates"
          className="inline-flex items-center gap-1.5 text-xs font-mono text-text-muted hover:text-white transition-colors"
        >
          <ArrowLeft className="w-3.5 h-3.5" />
          <span>Candidate Registry</span>
        </Link>

        <div className="flex items-center gap-2 flex-wrap">
          <button
            type="button"
            onClick={() => generatePdfReport(candidate)}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded bg-brand-primary hover:bg-brand-light text-white text-xs font-mono font-bold shadow-cyber transition-all cursor-pointer"
            title="Download Executive Security Audit PDF Report"
          >
            <Download className="w-3.5 h-3.5" />
            <span>Download PDF</span>
          </button>

          <button
            onClick={handleCopyJson}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded bg-surface-200 hover:bg-surface-300 border border-surface-border text-xs font-mono text-text-secondary transition-colors cursor-pointer"
          >
            {copied ? <Check className="w-3.5 h-3.5 text-risk-low" /> : <Copy className="w-3.5 h-3.5" />}
            <span>{copied ? 'JSON Copied' : 'Export Dossier'}</span>
          </button>

          <Link
            to="/risk-analysis"
            state={{ initialUrl: candidate.url }}
            className="px-3.5 py-1.5 rounded bg-surface-200 hover:bg-surface-300 border border-surface-border text-text-primary text-xs font-mono font-semibold transition-colors"
          >
            Re-run Live Scan
          </Link>
        </div>
      </div>

      {/* Header Profile Dossier Card */}
      <div className="p-6 rounded-xl bg-surface-100 border border-surface-border glass-panel">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 font-mono text-xs text-brand-light mb-1">
              <span>CANDIDATE DOSSIER // {candidate.id}</span>
              {candidate.isDemoData && (
                <span className="px-1.5 py-0.2 rounded bg-surface-200 text-text-muted border border-surface-border">
                  DEMO DATA
                </span>
              )}
            </div>
            <h2 className="text-xl font-bold text-white tracking-tight">
              {candidate.candidateName || candidate.job?.title || 'Target Subject'}
            </h2>
            <div className="flex items-center gap-2 font-mono text-xs text-text-muted mt-1">
              <Globe className="w-3.5 h-3.5 flex-shrink-0" />
              <a
                href={candidate.final_url || candidate.url}
                target="_blank"
                rel="noreferrer"
                className="hover:text-brand-light transition-colors flex items-center gap-1"
              >
                <span>{candidate.final_url || candidate.url}</span>
                <ExternalLink className="w-3 h-3" />
              </a>
            </div>
          </div>

          <div className="flex items-center gap-3 font-mono text-xs">
            <div className="p-3 rounded-lg bg-surface-200 border border-surface-border text-center">
              <div className="text-[10px] text-text-muted">RISK ASSESSMENT</div>
              <div className={`font-bold mt-0.5 text-sm ${
                candidate.risk_level === 'CRITICAL' ? 'text-risk-critical' :
                candidate.risk_level === 'HIGH' ? 'text-risk-high' :
                candidate.risk_level === 'MEDIUM' ? 'text-risk-medium' :
                candidate.risk_level === 'INCOMPLETE' ? 'text-risk-medium' : 'text-risk-low'
              }`}>
                {candidate.risk_level || (candidate.content_analyzed === false ? 'INCOMPLETE' : 'LOW')}
              </div>
            </div>
            <div className="p-3 rounded-lg bg-surface-200 border border-surface-border text-center">
              <div className="text-[10px] text-text-muted">RISK SCORE</div>
              <div className="font-bold mt-0.5 text-sm text-white">
                {candidate.risk_score !== null && candidate.risk_score !== undefined ? `${candidate.risk_score} / 100` : 'N/A'}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Main Grid: Radial Gauge & Risk Breakdown */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        <div className="lg:col-span-4 p-6 rounded-xl bg-surface-100 border border-surface-border glass-panel flex flex-col items-center justify-center text-center">
          <RadialScoreGauge
            score={candidate.risk_score}
            level={candidate.risk_level || (candidate.content_analyzed === false ? 'INCOMPLETE' : 'LOW')}
            contentAnalyzed={candidate.content_analyzed !== false}
            size={200}
          />
          <div className="mt-4 font-mono text-xs text-text-muted">
            Status: <span className="text-white font-bold">{candidate.content_analyzed === false ? 'Layer A Infrastructure Only' : 'Multi-Layer Assessment Complete'}</span>
          </div>
        </div>

        <div className="lg:col-span-8 p-6 rounded-xl bg-surface-100 border border-surface-border glass-panel">
          <RiskBreakdownBars
            scores={candidate.scores || {}}
            redFlags={candidate.red_flags || []}
            contentAnalyzed={candidate.content_analyzed !== false}
          />
        </div>
      </div>

      {/* Extracted Text & Resume Information */}
      <div className="p-5 rounded-xl bg-surface-100 border border-surface-border space-y-2">
        <div className="font-mono text-xs font-semibold text-text-secondary uppercase tracking-wider">
          Extracted Text & Subject Details
        </div>
        <div className="p-4 rounded-lg bg-surface-200/80 border border-surface-border text-xs text-text-secondary leading-relaxed max-h-48 overflow-y-auto">
          {candidate.job?.text_preview || 'No content snippet available.'}
        </div>
      </div>

      {/* Red Flags & Technical Infrastructure */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        <div className="lg:col-span-6 p-6 rounded-xl bg-surface-100 border border-surface-border glass-panel">
          <RedFlagsList redFlags={candidate.red_flags || []} />
        </div>

        <div className="lg:col-span-6 p-6 rounded-xl bg-surface-100 border border-surface-border glass-panel">
          <TechnicalChecks checks={candidate.technical_checks || {}} />
        </div>
      </div>
    </div>
  );
}
