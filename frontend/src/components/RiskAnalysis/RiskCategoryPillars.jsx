import React from 'react';
import { 
  DollarSign, 
  CreditCard, 
  FileCheck2, 
  ShieldAlert, 
  ShieldCheck, 
  AlertTriangle, 
  HelpCircle,
  Lock,
  UserCheck,
  Globe,
  Info
} from 'lucide-react';

export default function RiskCategoryPillars({ categories = {}, inputType = 'URL' }) {
  if (!categories || Object.keys(categories).length === 0) {
    return null;
  }

  const pillarConfig = [
    {
      key: 'financial_risk',
      title: 'Financial Risk',
      icon: DollarSign,
      defaultDescription: 'Analyzes upfront fees, registration charges, security deposits, and payment demands.',
    },
    {
      key: 'identity_risk',
      title: 'Identity / Data Risk',
      icon: Lock,
      defaultDescription: 'Monitors harvesting of Aadhaar, PAN, passport, bank details, and identity documents.',
    },
    {
      key: 'behavioral_risk',
      title: 'Behavioral Risk',
      icon: UserCheck,
      defaultDescription: 'Detects extreme urgency, unrealistic compensation, guaranteed offers, and chat-only recruiting.',
    },
    {
      key: 'technical_risk',
      title: 'Technical Infrastructure',
      icon: Globe,
      defaultDescription: 'Assesses domain age, SSL validity, DNS existence, and redirect legitimacy.',
    },
  ];

  const getLevelColor = (level, available = true) => {
    if (!available) {
      return {
        badgeBg: 'bg-surface-200 text-text-muted border-surface-border',
        barBg: 'bg-surface-border',
        textColor: 'text-text-muted',
      };
    }
    switch (level?.toUpperCase()) {
      case 'CRITICAL':
        return {
          badgeBg: 'bg-risk-critical/15 text-risk-critical border-risk-critical/30',
          barBg: 'bg-risk-critical',
          textColor: 'text-risk-critical',
        };
      case 'HIGH':
        return {
          badgeBg: 'bg-risk-high/15 text-risk-high border-risk-high/30',
          barBg: 'bg-risk-high',
          textColor: 'text-risk-high',
        };
      case 'MEDIUM':
        return {
          badgeBg: 'bg-risk-medium/15 text-risk-medium border-risk-medium/30',
          barBg: 'bg-risk-medium',
          textColor: 'text-risk-medium',
        };
      case 'LOW':
      default:
        return {
          badgeBg: 'bg-risk-low/15 text-risk-low border-risk-low/30',
          barBg: 'bg-risk-low',
          textColor: 'text-risk-low',
        };
    }
  };

  return (
    <div className="p-6 rounded-2xl bg-surface-100 border border-surface-border glass-panel space-y-5 font-sans">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-surface-border pb-3">
        <div>
          <div className="flex items-center gap-2">
            <ShieldAlert className="w-4 h-4 text-brand-light" />
            <h3 className="text-sm font-mono font-bold uppercase tracking-wider text-white">
              Risk Pillar Breakdown
            </h3>
          </div>
          <p className="text-xs text-text-muted mt-0.5">
            Independent assessment across the 4 foundational recruitment fraud vectors
          </p>
        </div>
        <div className="flex items-center gap-2 font-mono text-[11px] text-text-muted self-start sm:self-auto">
          <span>Engine:</span>
          <span className="px-2 py-0.5 rounded bg-surface-200 text-text-secondary border border-surface-border">
            Central Pipeline
          </span>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {pillarConfig.map(({ key, title, icon: Icon, defaultDescription }) => {
          const cat = categories[key] || {
            score: 0,
            level: 'LOW',
            available: true,
            signals: [],
          };
          const isAvailable = cat.available !== false;
          const levelStyle = getLevelColor(cat.level, isAvailable);
          const score = typeof cat.score === 'number' ? Math.round(cat.score) : 0;
          const signals = cat.signals || [];

          return (
            <div
              key={key}
              className={`p-4 rounded-xl border transition-all ${
                isAvailable
                  ? 'bg-surface-200/70 border-surface-border hover:border-brand-primary/40'
                  : 'bg-surface-200/30 border-surface-border/60 opacity-80'
              }`}
            >
              {/* Header */}
              <div className="flex items-center justify-between gap-2 mb-2.5">
                <div className="flex items-center gap-2 min-w-0">
                  <div className={`p-1.5 rounded-lg bg-surface-300 border border-surface-border ${levelStyle.textColor}`}>
                    <Icon className="w-4 h-4" />
                  </div>
                  <h4 className="text-xs font-bold text-white tracking-wide truncate">
                    {title}
                  </h4>
                </div>

                <div className="flex items-center gap-2 flex-shrink-0">
                  {isAvailable ? (
                    <>
                      <span className="font-mono text-xs font-bold text-white">
                        {score}
                        <span className="text-[10px] text-text-muted font-normal">/100</span>
                      </span>
                      <span className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold uppercase border ${levelStyle.badgeBg}`}>
                        {cat.level || 'LOW'}
                      </span>
                    </>
                  ) : (
                    <span className="px-2 py-0.5 rounded text-[10px] font-mono font-semibold uppercase bg-surface-300 text-text-muted border border-surface-border">
                      UNAVAILABLE
                    </span>
                  )}
                </div>
              </div>

              {/* Meter Bar */}
              <div className="w-full h-2 rounded-full bg-surface-300 overflow-hidden mb-2 relative">
                {isAvailable ? (
                  <div
                    className={`h-full rounded-full transition-all duration-700 ease-out ${levelStyle.barBg}`}
                    style={{ width: `${Math.max(5, Math.min(100, score))}%` }}
                  />
                ) : (
                  <div className="h-full w-full bg-surface-border/50 border-dashed border-b border-surface-border" />
                )}
              </div>

              {/* Signals list or explanation */}
              {isAvailable ? (
                signals.length > 0 ? (
                  <div className="space-y-1 mt-2">
                    {signals.slice(0, 3).map((sig, idx) => (
                      <div key={idx} className="flex items-start gap-1.5 text-[11px] text-text-secondary leading-snug">
                        <span className="text-risk-high font-mono flex-shrink-0">🚩</span>
                        <span className="truncate">{sig}</span>
                      </div>
                    ))}
                    {signals.length > 3 && (
                      <div className="text-[10px] font-mono text-text-muted pt-0.5">
                        +{signals.length - 3} additional warning indicator{signals.length - 3 > 1 ? 's' : ''}
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="flex items-center gap-1.5 text-[11px] text-text-muted mt-2">
                    <ShieldCheck className="w-3.5 h-3.5 text-risk-low flex-shrink-0" />
                    <span>No elevated risk indicators detected</span>
                  </div>
                )
              ) : (
                <div className="flex items-center gap-1.5 text-[11px] text-text-muted mt-2 italic">
                  <Info className="w-3.5 h-3.5 text-text-muted flex-shrink-0" />
                  <span>Technical infrastructure checks not applicable (No external URL provided)</span>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
