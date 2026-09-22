import React, { useState, useEffect } from 'react';
import { Activity as ActivityIcon, Server, Shield, CheckCircle2, RefreshCw } from 'lucide-react';
import { apiClient, API_BASE_URL } from '../api/client';
import { getSessionScans } from '../api/analysis';

export default function Activity() {
  const [activities, setActivities] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchActivities = async () => {
    setLoading(true);
    try {
      const resp = await apiClient.get('/api/activity');
      if (Array.isArray(resp.data) && resp.data.length > 0) {
        setActivities(resp.data);
        return;
      }
    } catch (err) {
      console.warn('Could not fetch /api/activity, using session scans fallback', err);
    }
    // Fallback to local session scans if backend returns empty or unavailable
    const scans = getSessionScans();
    const formatted = scans.map((s, idx) => ({
      id: `EVT-${idx + 100}`,
      timestamp: s.scannedAt || new Date().toISOString(),
      method: 'POST',
      endpoint: '/api/scan',
      target: s.url,
      status: 200,
      riskScore: s.risk_score,
      riskLevel: s.risk_level,
    }));
    setActivities(formatted);
    setLoading(false);
  };

  useEffect(() => {
    fetchActivities();
  }, []);

  return (
    <div className="space-y-6 font-sans">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-white tracking-tight">
            API Telemetry & Activity Audit
          </h2>
          <p className="text-xs text-text-muted mt-0.5">
            Real-time record of outbound network scans and risk engine invocations
          </p>
        </div>
        <button
          onClick={fetchActivities}
          className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-lg bg-surface-200 hover:bg-surface-300 text-text-secondary hover:text-white border border-surface-border transition-colors"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          Refresh
        </button>
      </div>

      <div className="rounded-xl bg-surface-100 border border-surface-border overflow-hidden font-mono text-xs">
        <div className="px-4 py-3 bg-surface-200 border-b border-surface-border text-text-muted flex justify-between uppercase text-[11px]">
          <span>Event Stream // Recent Invocations</span>
          <span>Target Backend: {API_BASE_URL}</span>
        </div>

        {activities.length === 0 ? (
          <div className="p-8 text-center text-text-muted">
            No API activity recorded in this browser session yet. Run a scan from the Risk Analysis page.
          </div>
        ) : (
          <div className="divide-y divide-surface-border/60">
            {activities.map((act) => (
              <div key={act.id} className="p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3 hover:bg-surface-200/50">
                <div className="flex items-center gap-3">
                  <span className="px-2 py-0.5 rounded bg-brand-primary/10 text-brand-light font-bold text-[10px] border border-brand-primary/20">
                    {act.method}
                  </span>
                  <div>
                    <div className="font-semibold text-white">{act.endpoint}</div>
                    <div className="text-text-muted text-[11px] truncate max-w-md">{act.target}</div>
                  </div>
                </div>

                <div className="flex items-center gap-4 text-[11px]">
                  <span className="text-risk-low font-bold flex items-center gap-1">
                    <CheckCircle2 className="w-3.5 h-3.5" /> {act.status} OK
                  </span>
                  <span className="text-text-secondary">
                    Risk: {act.riskScore}/100 ({act.riskLevel})
                  </span>
                  <span className="text-text-muted">
                    {new Date(act.timestamp).toLocaleTimeString()}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
