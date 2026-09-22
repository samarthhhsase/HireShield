import React from 'react';
import { Lock, Unlock, Calendar, Globe, Server, CornerDownRight, CheckCircle2, XCircle } from 'lucide-react';

export default function TechnicalChecks({ checks = {} }) {
  const {
    ssl_valid = false,
    domain_age_days = null,
    dns_exists = false,
    ip = null,
    redirect_count = 0,
  } = checks;

  const getAgeLabel = (days) => {
    if (days === null || days === undefined) return 'Unknown (Whois restricted)';
    if (days < 30) return `${days} days (Newly registered - High Risk)`;
    if (days < 180) return `${days} days (Under 6 months - Moderate Risk)`;
    const years = Math.floor(days / 365);
    return `${days} days (~${years} years - Established)`;
  };

  const isNewDomain = domain_age_days !== null && domain_age_days < 30;

  return (
    <div className="space-y-3 font-sans">
      <div className="flex items-center justify-between">
        <h4 className="text-xs font-mono font-semibold tracking-wider text-text-secondary uppercase">
          Technical & Infrastructure Checks
        </h4>
        <span className="text-[11px] font-mono text-text-muted">
          Network Layer
        </span>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 font-mono text-xs">
        {/* SSL Status */}
        <div className="p-3 rounded-lg bg-surface-100 border border-surface-border flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            {ssl_valid ? (
              <Lock className="w-4 h-4 text-risk-low" />
            ) : (
              <Unlock className="w-4 h-4 text-risk-critical" />
            )}
            <div>
              <div className="text-[11px] text-text-muted">SSL Certificate</div>
              <div className="font-semibold text-text-primary mt-0.5">
                {ssl_valid ? 'Valid & Encrypted' : 'Invalid / Insecure'}
              </div>
            </div>
          </div>
          {ssl_valid ? (
            <span className="px-2 py-0.5 rounded text-[10px] bg-risk-low/15 text-risk-low border border-risk-low/30 font-bold">
              PASS
            </span>
          ) : (
            <span className="px-2 py-0.5 rounded text-[10px] bg-risk-critical/15 text-risk-critical border border-risk-critical/30 font-bold">
              FAIL
            </span>
          )}
        </div>

        {/* DNS Existence */}
        <div className="p-3 rounded-lg bg-surface-100 border border-surface-border flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <Globe className={`w-4 h-4 ${dns_exists ? 'text-risk-low' : 'text-risk-critical'}`} />
            <div>
              <div className="text-[11px] text-text-muted">DNS Resolution</div>
              <div className="font-semibold text-text-primary mt-0.5">
                {dns_exists ? 'Resolved Host' : 'Host Unresolved'}
              </div>
            </div>
          </div>
          {dns_exists ? (
            <span className="px-2 py-0.5 rounded text-[10px] bg-risk-low/15 text-risk-low border border-risk-low/30 font-bold">
              ACTIVE
            </span>
          ) : (
            <span className="px-2 py-0.5 rounded text-[10px] bg-risk-critical/15 text-risk-critical border border-risk-critical/30 font-bold">
              NO_DNS
            </span>
          )}
        </div>

        {/* Domain Age */}
        <div className="p-3 rounded-lg bg-surface-100 border border-surface-border flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <Calendar className={`w-4 h-4 ${isNewDomain ? 'text-risk-critical' : 'text-brand-light'}`} />
            <div>
              <div className="text-[11px] text-text-muted">Domain Age</div>
              <div className="font-semibold text-text-primary mt-0.5 truncate max-w-[180px]">
                {getAgeLabel(domain_age_days)}
              </div>
            </div>
          </div>
          {isNewDomain && (
            <span className="px-2 py-0.5 rounded text-[10px] bg-risk-critical/15 text-risk-critical border border-risk-critical/30 font-bold">
              NEW
            </span>
          )}
        </div>

        {/* Resolved IP */}
        <div className="p-3 rounded-lg bg-surface-100 border border-surface-border flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <Server className="w-4 h-4 text-brand-light" />
            <div>
              <div className="text-[11px] text-text-muted">Resolved IP</div>
              <div className="font-semibold text-text-primary mt-0.5 font-mono">
                {ip || 'None detected'}
              </div>
            </div>
          </div>
          <span className="text-[10px] font-mono text-text-muted">IPv4</span>
        </div>

        {/* Redirect Hops */}
        <div className="p-3 rounded-lg bg-surface-100 border border-surface-border flex items-center justify-between sm:col-span-2">
          <div className="flex items-center gap-2.5">
            <CornerDownRight className={`w-4 h-4 ${redirect_count >= 2 ? 'text-risk-high' : 'text-brand-light'}`} />
            <div>
              <div className="text-[11px] text-text-muted">HTTP Redirect Hops</div>
              <div className="font-semibold text-text-primary mt-0.5">
                {redirect_count} redirect{redirect_count === 1 ? '' : 's'} recorded during extraction
              </div>
            </div>
          </div>
          <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
            redirect_count >= 3
              ? 'bg-risk-critical/15 text-risk-critical border border-risk-critical/30'
              : redirect_count === 2
              ? 'bg-risk-medium/15 text-risk-medium border border-risk-medium/30'
              : 'bg-surface-200 text-text-muted border border-surface-border'
          }`}>
            {redirect_count >= 3 ? 'SUSPICIOUS_REDIRECTS' : 'NORMAL'}
          </span>
        </div>
      </div>
    </div>
  );
}
