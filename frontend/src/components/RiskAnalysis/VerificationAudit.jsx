import React from 'react';
import { 
  ShieldCheck, 
  AlertOctagon, 
  AlertTriangle, 
  CheckCircle2, 
  XCircle, 
  Globe, 
  Building2, 
  Mail, 
  CreditCard, 
  KeyRound, 
  BarChart3, 
  Info,
  Check
} from 'lucide-react';

export default function VerificationAudit({ audit }) {
  if (!audit) return null;

  const verdict = audit.verdict || 'UNVERIFIED';
  const isReal = verdict === 'VERIFIED_REAL' || verdict.includes('REAL');
  const isFake = verdict === 'FLAGGED_FAKE' || verdict.includes('FAKE') || verdict.includes('SCAM');

  const getPillarIcon = (pillarName = '') => {
    const p = pillarName.toLowerCase();
    if (p.includes('domain')) return Globe;
    if (p.includes('employer') || p.includes('brand')) return Building2;
    if (p.includes('recruiter') || p.includes('channel') || p.includes('communication')) return Mail;
    if (p.includes('payment') || p.includes('fee')) return CreditCard;
    if (p.includes('identity') || p.includes('credential')) return KeyRound;
    if (p.includes('salary') || p.includes('compensation') || p.includes('role')) return BarChart3;
    return ShieldCheck;
  };

  const getStatusBadge = (status = 'CAUTION') => {
    const s = status.toUpperCase();
    if (s === 'PASSED') {
      return (
        <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[10px] font-mono font-bold bg-risk-low/10 text-risk-low border border-risk-low/30">
          <Check className="w-3 h-3 stroke-[3]" />
          PASSED
        </span>
      );
    }
    if (s === 'FAILED') {
      return (
        <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[10px] font-mono font-bold bg-risk-critical/10 text-risk-critical border border-risk-critical/30">
          <XCircle className="w-3 h-3" />
          FAILED
        </span>
      );
    }
    return (
      <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[10px] font-mono font-bold bg-risk-medium/10 text-risk-medium border border-risk-medium/30">
        <AlertTriangle className="w-3 h-3" />
        CAUTION
      </span>
    );
  };

  const checks = audit.checks_performed || [];

  return (
    <div className="p-6 rounded-2xl bg-surface-100 border border-surface-border glass-panel space-y-6">
      {/* Header Banner */}
      <div className={`p-5 rounded-xl border flex flex-col md:flex-row md:items-center justify-between gap-4 ${
        isReal 
          ? 'bg-risk-low/5 border-risk-low/30' 
          : isFake 
            ? 'bg-risk-critical/5 border-risk-critical/30' 
            : 'bg-risk-medium/5 border-risk-medium/30'
      }`}>
        <div className="flex items-start gap-3.5">
          <div className={`p-2.5 rounded-xl border flex-shrink-0 ${
            isReal 
              ? 'bg-risk-low/10 text-risk-low border-risk-low/30' 
              : isFake 
                ? 'bg-risk-critical/10 text-risk-critical border-risk-critical/30' 
                : 'bg-risk-medium/10 text-risk-medium border-risk-medium/30'
          }`}>
            {isReal ? (
              <ShieldCheck className="w-6 h-6" />
            ) : isFake ? (
              <AlertOctagon className="w-6 h-6" />
            ) : (
              <AlertTriangle className="w-6 h-6" />
            )}
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-mono text-[11px] font-bold uppercase tracking-wider text-text-muted">
                VERIFICATION AUDIT REPORT
              </span>
              <span className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold border ${
                isReal 
                  ? 'bg-risk-low/10 text-risk-low border-risk-low/30' 
                  : isFake 
                    ? 'bg-risk-critical/10 text-risk-critical border-risk-critical/30' 
                    : 'bg-risk-medium/10 text-risk-medium border-risk-medium/30'
              }`}>
                {verdict.replace(/_/g, ' ')}
              </span>
            </div>
            <h3 className="text-base sm:text-lg font-bold text-white mt-1">
              {audit.headline || `Why This Job Is ${verdict}`}
            </h3>
            <p className="text-xs text-text-secondary mt-1.5 leading-relaxed font-sans max-w-2xl">
              {audit.verdict_explanation}
            </p>
          </div>
        </div>
      </div>

      {/* 6 Security Pillars Grid */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="text-sm font-bold text-white uppercase tracking-wider font-mono">
              WHAT WE CHECKED &amp; HOW IT WAS VERIFIED
            </span>
          </div>
          <span className="text-[11px] font-mono text-text-muted">
            {checks.length} SECURITY VECTORS
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {checks.map((chk, idx) => {
            const IconComponent = getPillarIcon(chk.pillar);
            const statusUpper = (chk.status || 'CAUTION').toUpperCase();
            const isPassed = statusUpper === 'PASSED';
            const isFailed = statusUpper === 'FAILED';

            return (
              <div 
                key={idx}
                className={`p-4 rounded-xl border transition-all flex flex-col justify-between space-y-3 ${
                  isPassed 
                    ? 'bg-surface-200/50 border-surface-border hover:border-risk-low/40' 
                    : isFailed 
                      ? 'bg-risk-critical/5 border-risk-critical/30 hover:border-risk-critical/50' 
                      : 'bg-risk-medium/5 border-risk-medium/30 hover:border-risk-medium/50'
                }`}
              >
                {/* Pillar Header */}
                <div className="flex items-center justify-between gap-2 border-b border-surface-border/60 pb-2.5">
                  <div className="flex items-center gap-2 min-w-0">
                    <div className={`p-1.5 rounded-lg border flex-shrink-0 ${
                      isPassed ? 'bg-risk-low/10 text-risk-low border-risk-low/20' :
                      isFailed ? 'bg-risk-critical/10 text-risk-critical border-risk-critical/20' :
                      'bg-risk-medium/10 text-risk-medium border-risk-medium/20'
                    }`}>
                      <IconComponent className="w-4 h-4" />
                    </div>
                    <span className="font-semibold text-xs text-white truncate">
                      {chk.pillar}
                    </span>
                  </div>
                  {getStatusBadge(chk.status)}
                </div>

                {/* What We Checked & How Verified */}
                <div className="space-y-2 text-xs">
                  <div>
                    <span className="font-mono text-[10px] text-text-muted uppercase tracking-wider block mb-0.5">
                      What We Checked:
                    </span>
                    <p className="text-text-secondary text-[11px] leading-relaxed">
                      {chk.what_we_checked}
                    </p>
                  </div>

                  <div>
                    <span className="font-mono text-[10px] text-text-muted uppercase tracking-wider block mb-0.5">
                      How It Was Verified:
                    </span>
                    <p className="text-text-secondary text-[11px] leading-relaxed">
                      {chk.how_verified}
                    </p>
                  </div>
                </div>

                {/* Evidence Finding */}
                <div className={`p-2.5 rounded-lg border text-xs font-sans mt-1 ${
                  isPassed 
                    ? 'bg-surface-300/40 text-text-primary border-surface-border' 
                    : isFailed 
                      ? 'bg-risk-critical/10 text-risk-critical border-risk-critical/30 font-medium' 
                      : 'bg-risk-medium/10 text-risk-medium border-risk-medium/30 font-medium'
                }`}>
                  <span className="font-mono text-[10px] font-bold uppercase tracking-wider block mb-1 opacity-80">
                    Audit Finding:
                  </span>
                  <span className="leading-relaxed block">
                    {chk.finding}
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Methodology Footer */}
      {audit.verification_methodology && (
        <div className="flex items-center gap-2 p-3 rounded-lg bg-surface-200/50 border border-surface-border text-[11px] text-text-muted font-mono">
          <Info className="w-4 h-4 text-brand-light flex-shrink-0" />
          <span>
            <strong className="text-text-secondary">Methodology:</strong> {audit.verification_methodology}
          </span>
        </div>
      )}
    </div>
  );
}
