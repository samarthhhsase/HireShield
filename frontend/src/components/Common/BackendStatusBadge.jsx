import React, { useState, useEffect } from 'react';
import { checkBackendHealth } from '../../api/analysis';
import { API_BASE_URL } from '../../api/client';
import { Server, CheckCircle2, AlertTriangle, RefreshCw } from 'lucide-react';

export default function BackendStatusBadge({ compact = false }) {
  const [status, setStatus] = useState('checking'); // 'online' | 'offline' | 'checking'
  const [latency, setLatency] = useState(null);
  const [lastChecked, setLastChecked] = useState(null);
  const portLabel = API_BASE_URL.split(':').pop().replace(/[^0-9]/g, '') || '8001';

  const performHealthCheck = async () => {
    try {
      const data = await checkBackendHealth();
      if (data.status === 'healthy' || data.status === 'ok') {
        setStatus('online');
        setLatency(data.latencyMs || 8);
      } else {
        setStatus('offline');
      }
    } catch {
      setStatus('offline');
      setLatency(null);
    } finally {
      setLastChecked(new Date().toLocaleTimeString());
    }
  };

  useEffect(() => {
    performHealthCheck();
    const interval = setInterval(performHealthCheck, 12000);
    return () => clearInterval(interval);
  }, []);

  if (compact) {
    return (
      <div 
        className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-[11px] font-mono border transition-all ${
          status === 'online'
            ? 'bg-risk-low/10 text-risk-low border-risk-low/30'
            : status === 'offline'
            ? 'bg-risk-critical/10 text-risk-critical border-risk-critical/30'
            : 'bg-surface-100 text-text-muted border-surface-border'
        }`}
        title={`Backend: ${status.toUpperCase()} • Last checked: ${lastChecked || 'N/A'}`}
      >
        <span className={`w-1.5 h-1.5 rounded-full ${
          status === 'online' ? 'bg-risk-low animate-pulse' : status === 'offline' ? 'bg-risk-critical' : 'bg-text-muted'
        }`} />
        <span>{status === 'online' ? 'SYSTEM ONLINE' : status === 'offline' ? 'SYSTEM OFFLINE' : 'CHECKING...'}</span>
      </div>
    );
  }

  return (
    <div className="flex items-center justify-between p-3 rounded-lg bg-surface-200 border border-surface-border text-xs font-mono">
      <div className="flex items-center gap-2.5">
        <div className={`p-1.5 rounded-md ${
          status === 'online' ? 'bg-risk-low/10 text-risk-low' : 'bg-risk-critical/10 text-risk-critical'
        }`}>
          <Server className="w-3.5 h-3.5" />
        </div>
        <div>
          <div className="flex items-center gap-2">
            <span className="font-semibold text-text-primary">FastAPI Risk Backend</span>
            <span className={`w-1.5 h-1.5 rounded-full ${
              status === 'online' ? 'bg-risk-low animate-pulse' : 'bg-risk-critical'
            }`} />
            <span className={status === 'online' ? 'text-risk-low font-medium' : 'text-risk-critical font-medium'}>
              {status === 'online' ? 'ONLINE' : 'UNREACHABLE'}
            </span>
          </div>
          <div className="text-text-muted text-[11px] mt-0.5">
            {API_BASE_URL} {latency ? `• Ping ${latency}ms` : ''}
          </div>
        </div>
      </div>

      <button
        onClick={performHealthCheck}
        className="p-1 text-text-muted hover:text-text-primary transition-colors"
        title="Refresh health status"
      >
        <RefreshCw className="w-3 h-3 hover:rotate-180 transition-transform duration-500" />
      </button>
    </div>
  );
}
