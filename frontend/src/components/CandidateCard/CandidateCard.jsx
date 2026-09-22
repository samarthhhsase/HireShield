import React from 'react';
import { Link } from 'react-router-dom';
import { ShieldCheck, AlertTriangle, ShieldAlert, AlertOctagon, HelpCircle, ArrowRight, Globe, Lock, Unlock } from 'lucide-react';

export default function CandidateCard({ candidate }) {
  const getBadge = (level) => {
    switch ((level || '').toUpperCase()) {
      case 'INCOMPLETE':
        return {
          style: 'bg-risk-medium/15 text-risk-medium border-risk-medium/30',
          icon: HelpCircle,
        };
      case 'CRITICAL':
        return {
          style: 'bg-risk-critical/15 text-risk-critical border-risk-critical/30',
          icon: AlertOctagon,
        };
      case 'HIGH':
        return {
          style: 'bg-risk-high/15 text-risk-high border-risk-high/30',
          icon: ShieldAlert,
        };
      case 'MEDIUM':
        return {
          style: 'bg-risk-medium/15 text-risk-medium border-risk-medium/30',
          icon: AlertTriangle,
        };
      case 'LOW':
      default:
        return {
          style: 'bg-risk-low/15 text-risk-low border-risk-low/30',
          icon: ShieldCheck,
        };
    }
  };

  const badge = getBadge(candidate.risk_level);
  const Icon = badge.icon;
  const flagCount = candidate.red_flags ? candidate.red_flags.length : 0;

  return (
    <div className="p-4 rounded-lg bg-surface-100 border border-surface-border glass-panel-hover flex flex-col justify-between">
      <div>
        <div className="flex items-start justify-between gap-2 mb-3">
          <div className="min-w-0">
            <div className="flex items-center gap-1.5 flex-wrap">
              <h3 className="font-semibold text-text-primary text-sm truncate">
                {candidate.candidateName || candidate.job?.title || 'Target Profile'}
              </h3>
              {candidate.isDemoData && (
                <span className="text-[9px] font-mono px-1 py-0.2 rounded bg-surface-200 text-text-muted border border-surface-border">
                  DEMO
                </span>
              )}
            </div>
            <div className="text-[11px] font-mono text-text-muted truncate mt-0.5" title={candidate.url}>
              {candidate.url}
            </div>
          </div>

          <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-mono font-bold tracking-wider border flex-shrink-0 ${badge.style}`}>
            <Icon className="w-3 h-3" />
            <span>{candidate.risk_level || 'INCOMPLETE'}</span>
          </span>
        </div>

        <p className="text-xs text-text-secondary line-clamp-2 mb-4 leading-relaxed">
          {candidate.job?.text_preview || 'No text snippet preview available for this target.'}
        </p>

        {/* Scores Mini Grid */}
        <div className="grid grid-cols-4 gap-1.5 p-2 rounded bg-surface-200/60 border border-surface-border font-mono text-center text-[10px] mb-4">
          <div>
            <div className="text-text-muted">BEHAV</div>
            <div className="font-bold text-white mt-0.5">
              {candidate.scores?.behavioral !== null && candidate.scores?.behavioral !== undefined ? candidate.scores.behavioral : 'N/A'}
            </div>
          </div>
          <div>
            <div className="text-text-muted">LING</div>
            <div className="font-bold text-white mt-0.5">
              {candidate.scores?.linguistic !== null && candidate.scores?.linguistic !== undefined ? candidate.scores.linguistic : 'N/A'}
            </div>
          </div>
          <div>
            <div className="text-text-muted">STRUCT</div>
            <div className="font-bold text-white mt-0.5">
              {candidate.scores?.structural !== null && candidate.scores?.structural !== undefined ? candidate.scores.structural : 'N/A'}
            </div>
          </div>
          <div>
            <div className="text-text-muted">TECH</div>
            <div className="font-bold text-white mt-0.5">
              {candidate.scores?.technical !== null && candidate.scores?.technical !== undefined ? candidate.scores.technical : 'N/A'}
            </div>
          </div>
        </div>
      </div>

      <div className="pt-3 border-t border-surface-border/60 flex items-center justify-between">
        <div className="text-[11px] font-mono text-text-muted">
          Score: {candidate.risk_score !== null && candidate.risk_score !== undefined ? (
            <><span className="font-bold text-white">{candidate.risk_score}</span>/100</>
          ) : (
            <span className="font-bold text-risk-medium">N/A</span>
          )}
        </div>

        <Link
          to={`/risk-analysis/${candidate.id}`}
          state={{ candidateData: candidate }}
          className="inline-flex items-center gap-1 text-xs font-mono text-brand-light hover:text-white transition-colors"
        >
          <span>Dossier</span>
          <ArrowRight className="w-3.5 h-3.5" />
        </Link>
      </div>
    </div>
  );
}
