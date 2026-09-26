import React from 'react';
import { 
  FileText, 
  ShieldAlert, 
  ShieldCheck, 
  AlertTriangle, 
  CheckCircle2, 
  HelpCircle,
  AlertOctagon,
  ArrowRight,
  ExternalLink
} from 'lucide-react';

export default function ExecutiveSummaryAdvisory({ 
  summary = '', 
  recommendations = [], 
  riskLevel = 'LOW',
  riskScore = 0,
  inputType = 'URL'
}) {
  const getSeverityStyle = (level) => {
    switch (level?.toUpperCase()) {
      case 'CRITICAL':
        return {
          border: 'border-risk-critical/40',
          badge: 'bg-risk-critical/15 text-risk-critical border-risk-critical/30',
          iconColor: 'text-risk-critical',
          accent: 'from-risk-critical/10 to-transparent',
          label: 'CRITICAL THREAT DETECTED',
        };
      case 'HIGH':
        return {
          border: 'border-risk-high/40',
          badge: 'bg-risk-high/15 text-risk-high border-risk-high/30',
          iconColor: 'text-risk-high',
          accent: 'from-risk-high/10 to-transparent',
          label: 'HIGH-RISK SIGNALS DETECTED',
        };
      case 'MEDIUM':
        return {
          border: 'border-risk-medium/40',
          badge: 'bg-risk-medium/15 text-risk-medium border-risk-medium/30',
          iconColor: 'text-risk-medium',
          accent: 'from-risk-medium/10 to-transparent',
          label: 'CAUTION ADVISED // ANOMALIES IDENTIFIED',
        };
      case 'LOW':
      default:
        return {
          border: 'border-risk-low/30',
          badge: 'bg-risk-low/15 text-risk-low border-risk-low/30',
          iconColor: 'text-risk-low',
          accent: 'from-risk-low/10 to-transparent',
          label: 'LOW SUSPICION // MINIMAL RISK SIGNALS',
        };
    }
  };

  const style = getSeverityStyle(riskLevel);

  const fallbackRecommendations = [
    'Always verify job openings via the company\'s official website careers section.',
    'Never submit advance registration fees, security deposits, or training charges.',
    'Keep your Aadhaar, PAN, and banking details confidential until receiving an authenticated contract.',
    'Confirm recruiter identity through corporate email or official verified channels.',
  ];

  const displayRecs = recommendations && recommendations.length > 0 ? recommendations : fallbackRecommendations;

  return (
    <div className={`p-6 rounded-2xl bg-surface-100 border ${style.border} glass-panel space-y-6 font-sans relative overflow-hidden`}>
      {/* Decorative gradient header accent */}
      <div className={`absolute top-0 left-0 right-0 h-1.5 bg-gradient-to-r ${style.accent}`} />

      {/* Top Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div className="flex items-center gap-2.5">
          <div className={`p-2 rounded-xl bg-surface-200 border border-surface-border ${style.iconColor}`}>
            {riskLevel === 'CRITICAL' || riskLevel === 'HIGH' ? (
              <ShieldAlert className="w-5 h-5" />
            ) : riskLevel === 'MEDIUM' ? (
              <AlertTriangle className="w-5 h-5" />
            ) : (
              <ShieldCheck className="w-5 h-5" />
            )}
          </div>
          <div>
            <div className="flex items-center gap-2 font-mono text-xs">
              <span className={`px-2 py-0.5 rounded font-bold uppercase border ${style.badge}`}>
                {style.label}
              </span>
              <span className="text-text-muted">|</span>
              <span className="text-text-muted uppercase">EVALUATION SUMMARY</span>
            </div>
            <h3 className="text-lg font-bold text-white mt-0.5">
              Explainable Risk Intelligence Dossier
            </h3>
          </div>
        </div>

        <div className="flex items-center gap-2 font-mono text-xs self-start sm:self-auto">
          <span className="text-text-muted">Target Type:</span>
          <span className="px-2.5 py-1 rounded bg-surface-200 border border-surface-border text-white font-semibold">
            {inputType === 'PDF' ? '📄 PDF Document' : 
             inputType === 'GOOGLE_FORM' ? '📝 Google Form' : 
             inputType === 'TEXT' ? '✍️ Job Description Text' : 
             '🌐 Website URL'}
          </span>
        </div>
      </div>

      {/* Natural Language Summary Card */}
      <div className="p-4 rounded-xl bg-surface-200/80 border border-surface-border space-y-2">
        <div className="flex items-center justify-between text-xs font-mono">
          <span className="text-brand-light font-bold flex items-center gap-1.5">
            <FileText className="w-3.5 h-3.5" />
            EXECUTIVE FINDINGS
          </span>
          <span className="text-text-muted">Evidence-Grounded Synthesis</span>
        </div>
        <p className="text-sm text-text-primary leading-relaxed">
          {summary || (
            riskLevel === 'CRITICAL' || riskLevel === 'HIGH'
              ? 'Multiple high-risk indicators were detected during cross-examination. Potentially suspicious patterns require extreme caution before proceeding.'
              : 'Our risk engine completed multi-layer examination with low suspicion indicators. Maintain standard diligence.'
          )}
        </p>
      </div>

      {/* What Should You Do? Actionable Safety Guidance */}
      <div className="space-y-3 pt-1">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <ShieldCheck className="w-4 h-4 text-risk-low" />
            <h4 className="text-xs font-mono font-bold tracking-wider text-white uppercase">
              What Should You Do? (Recommended Safety Actions)
            </h4>
          </div>
          <span className="text-[11px] font-mono text-text-muted">
            Candidate Guidance
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-2.5">
          {displayRecs.map((rec, i) => (
            <div 
              key={i} 
              className="p-3 rounded-lg bg-surface-200/60 border border-surface-border hover:border-brand-primary/30 transition-colors flex items-start gap-2.5 text-xs text-text-secondary leading-snug"
            >
              <CheckCircle2 className="w-4 h-4 text-brand-light mt-0.5 flex-shrink-0" />
              <span>{rec}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
