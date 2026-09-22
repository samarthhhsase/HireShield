import React from 'react';
import { AlertOctagon, AlertTriangle, AlertCircle, CheckCircle2, Shield } from 'lucide-react';

export default function RedFlagsList({ redFlags = [] }) {
  if (!redFlags || redFlags.length === 0) {
    return (
      <div className="p-6 rounded-lg bg-surface-100 border border-surface-border text-center">
        <div className="w-10 h-10 rounded-full bg-risk-low/10 text-risk-low flex items-center justify-center mx-auto mb-3">
          <CheckCircle2 className="w-5 h-5" />
        </div>
        <div className="text-xs font-mono font-semibold text-text-primary uppercase tracking-wider">
          No Threat Red Flags Detected
        </div>
        <p className="text-[12px] text-text-muted mt-1 max-w-sm mx-auto">
          The linguistic, behavioral, and structural scanners did not identify any payment demands, sensitive credential solicitation, or unverified contact channels.
        </p>
      </div>
    );
  }

  const getSeverityStyle = (severity) => {
    switch ((severity || '').toLowerCase()) {
      case 'critical':
        return {
          badge: 'bg-risk-critical/15 text-risk-critical border-risk-critical/40',
          card: 'border-risk-critical/30 bg-risk-critical/5',
          icon: AlertOctagon,
          iconColor: 'text-risk-critical',
        };
      case 'high':
        return {
          badge: 'bg-risk-high/15 text-risk-high border-risk-high/40',
          card: 'border-risk-high/30 bg-risk-high/5',
          icon: AlertTriangle,
          iconColor: 'text-risk-high',
        };
      case 'medium':
      default:
        return {
          badge: 'bg-risk-medium/15 text-risk-medium border-risk-medium/40',
          card: 'border-risk-medium/30 bg-risk-medium/5',
          icon: AlertCircle,
          iconColor: 'text-risk-medium',
        };
    }
  };

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h4 className="text-xs font-mono font-semibold tracking-wider text-text-secondary uppercase">
          Detected Threat Signals ({redFlags.length})
        </h4>
        <span className="text-[11px] font-mono text-text-muted">
          AI/NLP Evidence Engine
        </span>
      </div>

      <div className="space-y-2.5">
        {redFlags.map((flag, index) => {
          const style = getSeverityStyle(flag.severity);
          const Icon = style.icon;

          return (
            <div
              key={index}
              className={`p-3.5 rounded-lg border transition-all ${style.card}`}
            >
              <div className="flex items-start gap-3">
                <Icon className={`w-4 h-4 mt-0.5 flex-shrink-0 ${style.iconColor}`} />
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1 flex-wrap">
                    <span className={`text-[10px] font-mono font-bold uppercase tracking-wider px-2 py-0.5 rounded border ${style.badge}`}>
                      {flag.severity}
                    </span>
                    <span className="text-[10px] font-mono text-text-muted uppercase px-1.5 py-0.5 rounded bg-surface-200 border border-surface-border">
                      {flag.type}
                    </span>
                  </div>
                  <p className="text-xs text-text-primary leading-relaxed font-medium">
                    {flag.message}
                  </p>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
