import React from 'react';
import { Link } from 'react-router-dom';
import { ShieldCheck, AlertTriangle, ShieldAlert, AlertOctagon, HelpCircle, ExternalLink, ArrowRight, CheckCircle2 } from 'lucide-react';

export default function CandidateTable({ candidates = [], isLoading = false }) {
  if (isLoading) {
    return (
      <div className="p-8 text-center font-mono text-xs text-text-muted bg-surface-100 rounded-lg border border-surface-border animate-pulse">
        SCANNING CANDIDATE INTELLIGENCE REPOSITORY...
      </div>
    );
  }

  if (!candidates || candidates.length === 0) {
    return (
      <div className="p-8 text-center bg-surface-100 rounded-lg border border-surface-border">
        <ShieldCheck className="w-8 h-8 text-brand-light mx-auto mb-2 opacity-50" />
        <div className="text-sm font-semibold text-text-primary">No Candidate Analyses Found</div>
        <p className="text-xs text-text-muted mt-1 max-w-sm mx-auto">
          No candidates or recruitment targets have been scanned yet. Run a live scan in Risk Analysis to generate intelligence dossiers.
        </p>
      </div>
    );
  }

  const getRiskBadge = (level, score) => {
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

  return (
    <div className="overflow-x-auto rounded-lg border border-surface-border bg-surface-100/80">
      <table className="w-full text-left border-collapse text-xs font-sans">
        <thead>
          <tr className="border-b border-surface-border bg-surface-200/60 font-mono text-[11px] text-text-muted uppercase tracking-wider">
            <th className="py-3 px-4">Candidate / Target</th>
            <th className="py-3 px-4">Subject Title</th>
            <th className="py-3 px-4 text-center">Risk Score</th>
            <th className="py-3 px-4 text-center">Threat Level</th>
            <th className="py-3 px-4">Flags</th>
            <th className="py-3 px-4">Analysis Date</th>
            <th className="py-3 px-4 text-right">Action</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-surface-border/60">
          {candidates.map((cand) => {
            const badge = getRiskBadge(cand.risk_level, cand.risk_score);
            const Icon = badge.icon;
            const flagCount = cand.red_flags ? cand.red_flags.length : 0;
            const formattedDate = cand.scannedAt ? new Date(cand.scannedAt).toLocaleDateString() : 'Active Session';

            return (
              <tr key={cand.id} className="hover:bg-surface-200/50 transition-colors group">
                {/* Candidate / ID */}
                <td className="py-3.5 px-4">
                  <div className="font-semibold text-text-primary flex items-center gap-1.5">
                    <span>{cand.candidateName || cand.job?.title || 'Target Profile'}</span>
                    {cand.isDemoData && (
                      <span className="text-[9px] font-mono px-1 py-0.2 rounded bg-surface-200 text-text-muted border border-surface-border">
                        DEMO
                      </span>
                    )}
                  </div>
                  <div className="font-mono text-[10px] text-text-muted mt-0.5 truncate max-w-[200px]" title={cand.url}>
                    {cand.url}
                  </div>
                </td>

                {/* Job Title */}
                <td className="py-3.5 px-4 text-text-secondary max-w-[220px] truncate" title={cand.job?.title}>
                  {cand.job?.title || 'Extracted Recruitment Spec'}
                </td>

                {/* Risk Score */}
                <td className="py-3.5 px-4 text-center font-mono">
                  {cand.risk_score !== null && cand.risk_score !== undefined ? (
                    <>
                      <span className="text-sm font-bold text-white">
                        {cand.risk_score}
                      </span>
                      <span className="text-[10px] text-text-muted">/100</span>
                    </>
                  ) : (
                    <span className="text-xs font-bold text-risk-medium">
                      N/A
                    </span>
                  )}
                </td>

                {/* Threat Level */}
                <td className="py-3.5 px-4 text-center">
                  <span className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10px] font-mono font-bold tracking-wider border ${badge.style}`}>
                    <Icon className="w-3 h-3" />
                    <span>{cand.risk_level || 'INCOMPLETE'}</span>
                  </span>
                </td>

                {/* Flags Count */}
                <td className="py-3.5 px-4 font-mono text-[11px]">
                  {flagCount > 0 ? (
                    <span className="text-risk-high font-semibold flex items-center gap-1">
                      <AlertTriangle className="w-3 h-3" /> {flagCount} Flag{flagCount === 1 ? '' : 's'}
                    </span>
                  ) : (
                    <span className="text-risk-low flex items-center gap-1">
                      <CheckCircle2 className="w-3 h-3" /> Clean
                    </span>
                  )}
                </td>

                {/* Date */}
                <td className="py-3.5 px-4 font-mono text-text-muted text-[11px]">
                  {formattedDate}
                </td>

                {/* Action */}
                <td className="py-3.5 px-4 text-right">
                  <Link
                    to={`/risk-analysis/${cand.id}`}
                    state={{ candidateData: cand }}
                    className="inline-flex items-center gap-1 px-2.5 py-1 rounded bg-surface-200 hover:bg-brand-primary/20 text-brand-light font-mono text-[11px] border border-surface-border hover:border-brand-primary/40 transition-all group-hover:border-brand-light/30"
                  >
                    <span>Inspect</span>
                    <ArrowRight className="w-3 h-3" />
                  </Link>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
