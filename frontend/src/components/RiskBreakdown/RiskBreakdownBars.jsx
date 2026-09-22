import React from 'react';
import { UserCheck, MessageSquare, Network, ShieldCheck, AlertOctagon, HelpCircle, Info } from 'lucide-react';

export default function RiskBreakdownBars({ scores = {}, redFlags = [], contentAnalyzed = true }) {
  const {
    behavioral = null,
    linguistic = null,
    structural = null,
    technical = 0,
  } = scores;

  // Check if critical behavioral override was triggered in backend:
  const messages = redFlags.map((f) => (f.message || '').toLowerCase()).join(' ');
  const hasSensitive = messages.includes('sensitive identity');
  const hasPayment = messages.includes('payment') || messages.includes('fee');
  const overrideTriggered = contentAnalyzed && hasSensitive && hasPayment;

  const categories = [
    {
      id: 'behavioral',
      title: 'Behavioral Signals',
      layer: 'Layer B (Content & Heuristics)',
      score: behavioral,
      weight: '35%',
      icon: UserCheck,
      description: 'Demands for upfront payments, registration fees, Aadhaar/PAN, or bank credentials.',
      isContentLayer: true,
    },
    {
      id: 'linguistic',
      title: 'Linguistic Analysis',
      layer: 'Layer B (Content & Heuristics)',
      score: linguistic,
      weight: '25%',
      icon: MessageSquare,
      description: 'Urgency manipulation, guaranteed income claims, and deceptive language patterns.',
      isContentLayer: true,
    },
    {
      id: 'structural',
      title: 'Structural Signals',
      layer: 'Layer B (Content & Heuristics)',
      score: structural,
      weight: '20%',
      icon: Network,
      description: 'Reliance on unverified communication channels (Telegram, WhatsApp direct messaging).',
      isContentLayer: true,
    },
    {
      id: 'technical',
      title: 'Technical Infrastructure',
      layer: 'Layer A (URL & DNS Intelligence)',
      score: technical,
      weight: '20%',
      icon: ShieldCheck,
      description: 'SSL certificate status, domain age, DNS resolution, and redirect hopping.',
      isContentLayer: false,
    },
  ];

  const getScoreColor = (score) => {
    if (score === null || score === undefined) return 'bg-surface-border';
    if (score >= 70) return 'bg-risk-critical';
    if (score >= 40) return 'bg-risk-high';
    if (score >= 20) return 'bg-risk-medium';
    return 'bg-risk-low';
  };

  return (
    <div className="space-y-4 font-sans">
      <div className="flex items-center justify-between">
        <h4 className="text-xs font-mono font-semibold tracking-wider text-text-secondary uppercase">
          Signal Weights & Risk Breakdown
        </h4>
        <span className="text-[11px] font-mono text-text-muted">
          {contentAnalyzed ? 'Full Multi-Layer Engine' : 'Layer A Infrastructure Only'}
        </span>
      </div>

      {/* Override Alert */}
      {overrideTriggered && (
        <div className="flex items-start gap-2.5 p-3 rounded-lg bg-risk-critical/10 border border-risk-critical/30 text-xs text-risk-critical font-mono">
          <AlertOctagon className="w-4 h-4 mt-0.5 flex-shrink-0 animate-pulse" />
          <div>
            <div className="font-bold tracking-wide">CRITICAL OVERRIDE ACTIVATED</div>
            <div className="text-[11px] text-text-secondary mt-0.5">
              Simultaneous sensitive identity requests and advance payment fees detected. Risk score overridden to CRITICAL (minimum 85/100) regardless of clean technical domain metrics.
            </div>
          </div>
        </div>
      )}

      {/* Notice when content is unanalyzed */}
      {!contentAnalyzed && (
        <div className="p-3 rounded-lg bg-surface-200/80 border border-brand-primary/30 text-xs font-mono text-text-muted flex items-start gap-2.5">
          <Info className="w-4 h-4 text-brand-light mt-0.5 flex-shrink-0" />
          <div>
            <span className="text-brand-light font-bold">CONTENT SIGNALS NOT ANALYZED: </span>
            <span>Target server blocked automated scraping (HTTP 403 / WAF). Behavioral, Linguistic, and Structural signals require job description text.</span>
          </div>
        </div>
      )}

      <div className="space-y-3.5">
        {categories.map((cat) => {
          const Icon = cat.icon;
          const isCategoryAnalyzed = cat.score !== null && cat.score !== undefined && (!cat.isContentLayer || contentAnalyzed);

          return (
            <div key={cat.id} className="p-3.5 rounded-lg bg-surface-100 border border-surface-border">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-1 sm:gap-2 mb-2">
                <div className="flex items-center gap-2">
                  <Icon className="w-3.5 h-3.5 text-brand-light flex-shrink-0" />
                  <span className="text-xs font-semibold text-text-primary">{cat.title}</span>
                  <span className="text-[10px] font-mono text-text-muted px-1.5 py-0.5 rounded bg-surface-200 border border-surface-border">
                    {cat.weight}
                  </span>
                </div>

                <div className="flex items-center gap-2 font-mono text-xs">
                  {isCategoryAnalyzed ? (
                    <>
                      <span className="font-bold text-white">{cat.score}</span>
                      <span className="text-[10px] text-text-muted">/ 100</span>
                      <span className="text-[10px] px-1.5 py-0.2 rounded bg-risk-low/10 text-risk-low border border-risk-low/30">
                        ASSESSED
                      </span>
                    </>
                  ) : (
                    <span className="text-[11px] px-2 py-0.5 rounded bg-risk-medium/10 text-risk-medium border border-risk-medium/30 font-semibold tracking-wider">
                      NOT ANALYZED (N/A)
                    </span>
                  )}
                </div>
              </div>

              {/* Progress Bar */}
              <div className="w-full h-2 rounded-full bg-surface-200 overflow-hidden relative">
                {isCategoryAnalyzed ? (
                  <div
                    className={`h-full rounded-full transition-all duration-700 ease-out ${getScoreColor(cat.score)}`}
                    style={{ width: `${Math.min(100, Math.max(0, cat.score))}%` }}
                  />
                ) : (
                  <div className="h-full w-full bg-surface-border/40 border-dashed border-b border-surface-border animate-pulse" />
                )}
              </div>

              <div className="flex items-center justify-between mt-1.5 text-[11px] text-text-muted">
                <p className="leading-tight">{cat.description}</p>
                {!isCategoryAnalyzed && (
                  <span className="text-[10px] font-mono text-text-muted flex-shrink-0 ml-2">
                    Requires Job Text
                  </span>
                )}
              </div>
            </div>
          );
        })}
      </div>

      <div className="p-3 rounded-lg bg-surface-200/50 border border-surface-border text-[11px] font-mono text-text-muted flex items-center gap-2">
        <HelpCircle className="w-3.5 h-3.5 text-brand-light flex-shrink-0" />
        <span>
          Algorithm: <code className="text-text-secondary">35% Behavioral + 25% Linguistic + 20% Structural + 20% Technical</code>
        </span>
      </div>
    </div>
  );
}
