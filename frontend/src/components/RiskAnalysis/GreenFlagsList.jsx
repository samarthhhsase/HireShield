import React from 'react';
import { ShieldCheck, CheckCircle2, Award, FileCheck, Shield, Sparkles } from 'lucide-react';

export default function GreenFlagsList({ greenFlags = [], legitimacyScore = null }) {
  if (!greenFlags || greenFlags.length === 0) {
    return (
      <div className="p-5 rounded-xl bg-surface-100 border border-surface-border text-center space-y-2">
        <div className="w-8 h-8 rounded-full bg-surface-200 text-text-muted flex items-center justify-center mx-auto">
          <Shield className="w-4 h-4" />
        </div>
        <div className="text-xs font-mono font-semibold text-text-muted uppercase tracking-wider">
          No Corporate Legitimacy Signatures Detected
        </div>
        <p className="text-[11px] text-text-muted max-w-xs mx-auto">
          Posting lacks standard corporate compliance hallmarks such as formal EEO declarations, structured benefits packages, or anti-fraud recruitment policies.
        </p>
      </div>
    );
  }

  const getFlagIcon = (type) => {
    switch (type) {
      case 'anti_fraud_policy':
        return ShieldCheck;
      case 'eeo_compliance':
        return Award;
      case 'corporate_benefits':
        return Sparkles;
      case 'enterprise_ats':
        return FileCheck;
      case 'structured_qualifications':
      case 'hiring_process':
      default:
        return CheckCircle2;
    }
  };

  return (
    <div className="space-y-3 font-sans">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <ShieldCheck className="w-4 h-4 text-risk-low" />
          <h4 className="text-xs font-mono font-semibold tracking-wider text-text-secondary uppercase">
            Legitimacy Markers ({greenFlags.length})
          </h4>
        </div>
        {legitimacyScore !== null && (
          <span className="text-[11px] font-mono text-risk-low font-bold px-2 py-0.5 rounded bg-risk-low/10 border border-risk-low/30">
            {legitimacyScore}% Legitimacy Index
          </span>
        )}
      </div>

      <div className="space-y-2.5">
        {greenFlags.map((flag, index) => {
          const Icon = getFlagIcon(flag.type);
          return (
            <div
              key={index}
              className="p-3 rounded-lg border border-risk-low/30 bg-risk-low/5 transition-all"
            >
              <div className="flex items-start gap-3">
                <Icon className="w-4 h-4 mt-0.5 flex-shrink-0 text-risk-low" />
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1 flex-wrap">
                    <span className="text-[10px] font-mono font-bold uppercase tracking-wider px-2 py-0.5 rounded border bg-risk-low/15 text-risk-low border-risk-low/40">
                      VERIFIED MARKER
                    </span>
                    {flag.trust_bonus && (
                      <span className="text-[10px] font-mono text-risk-low font-bold">
                        +{flag.trust_bonus} Trust
                      </span>
                    )}
                  </div>
                  <div className="text-xs font-semibold text-white">
                    {flag.title || flag.message}
                  </div>
                  <p className="text-[11px] text-text-secondary leading-relaxed mt-0.5">
                    {flag.message}
                  </p>
                  {flag.evidence && (
                    <div className="mt-1 font-mono text-[10px] text-text-muted italic truncate">
                      {flag.evidence}
                    </div>
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
