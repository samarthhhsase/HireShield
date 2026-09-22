import React, { useState } from 'react';
import { AlertCircle, ChevronDown, ChevronUp, Database, Code, ShieldAlert } from 'lucide-react';

export default function MissingEndpointBadge({ 
  endpoint = 'GET /api/candidates', 
  title = 'MISSING BACKEND ENDPOINT',
  description = 'The existing Python backend currently operates in stateless URL scan mode and does not yet implement this endpoint.',
  suggestedAction = 'Extend app/main.py and add SQLite persistence via SQLAlchemy.'
}) {
  const [expanded, setExpanded] = useState(false);

  return (
    <div className="rounded-lg border border-amber-500/30 bg-amber-500/5 p-3.5 text-xs">
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-start gap-2.5">
          <ShieldAlert className="w-4 h-4 text-amber-400 mt-0.5 flex-shrink-0" />
          <div>
            <div className="flex items-center gap-2 flex-wrap">
              <span className="font-mono font-semibold text-amber-300 tracking-wider text-[11px] bg-amber-500/10 px-2 py-0.5 rounded border border-amber-500/20">
                {title}
              </span>
              <span className="font-mono text-text-secondary bg-surface-100 px-2 py-0.5 rounded text-[11px] border border-surface-border">
                {endpoint}
              </span>
            </div>
            <p className="text-text-muted mt-1.5 leading-relaxed text-[12px]">
              {description}
            </p>
          </div>
        </div>

        <button
          onClick={() => setExpanded(!expanded)}
          className="text-amber-400/80 hover:text-amber-300 font-mono text-[11px] flex items-center gap-1 transition-colors flex-shrink-0"
        >
          {expanded ? 'Hide Details' : 'Backend Spec'}
          {expanded ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
        </button>
      </div>

      {expanded && (
        <div className="mt-3 pt-3 border-t border-amber-500/20 font-mono text-[11px] space-y-2 text-text-secondary bg-surface-300/60 p-3 rounded">
          <div className="flex items-center gap-1.5 text-brand-light font-semibold">
            <Database className="w-3.5 h-3.5" />
            <span>Architecture Guidance & Database Plan</span>
          </div>
          <p className="text-text-muted">
            The frontend avoids fabricating fake APIs or mock database connections. To make this fully persistent in the backend:
          </p>
          <ul className="list-disc list-inside space-y-1 text-text-secondary pl-1">
            <li>Install <code className="text-brand-light bg-surface-100 px-1 py-0.5 rounded">sqlalchemy</code> in <code className="text-brand-light">requirements.txt</code></li>
            <li>Define candidate & scan models in <code className="text-brand-light">app/models/candidate.py</code></li>
            <li>Implement SQLite database session in <code className="text-brand-light">app/database.py</code></li>
            <li>Register <code className="text-brand-light">{endpoint}</code> routes in <code className="text-brand-light">app/main.py</code></li>
          </ul>
        </div>
      )}
    </div>
  );
}
