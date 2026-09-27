import React from 'react';
import { AlertOctagon, RefreshCw, Home, ShieldAlert } from 'lucide-react';

export default class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('HireShield ErrorBoundary caught an unhandled error:', error, errorInfo);
    this.setState({ errorInfo });
  }

  handleReset = () => {
    this.setState({ hasError: false, error: null, errorInfo: null });
    if (this.props.onReset) {
      this.props.onReset();
    }
  };

  handleReload = () => {
    window.location.reload();
  };

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }

      return (
        <div className="min-h-[350px] p-8 rounded-2xl bg-surface-100 border border-risk-critical/40 glass-panel flex flex-col items-center justify-center text-center space-y-5 font-sans my-6 max-w-2xl mx-auto shadow-2xl">
          <div className="w-16 h-16 rounded-2xl bg-risk-critical/10 border border-risk-critical/30 flex items-center justify-center text-risk-critical shadow-cyber animate-pulse">
            <ShieldAlert className="w-8 h-8" />
          </div>

          <div className="space-y-1.5">
            <div className="flex items-center justify-center gap-2 font-mono text-xs text-risk-critical font-bold uppercase tracking-wider">
              <AlertOctagon className="w-4 h-4" />
              <span>UI SHIELD INTERCEPT // RUNTIME EXCEPTION CAUGHT</span>
            </div>
            <h2 className="text-xl font-bold text-white tracking-tight">
              Risk Interface Recovered Successfully
            </h2>
            <p className="text-xs text-text-muted max-w-md mx-auto leading-relaxed">
              An unexpected render anomaly was intercepted by HireShield&apos;s UI Error Boundary. The screen was protected from unmounting.
            </p>
          </div>

          {this.state.error && (
            <div className="w-full p-3.5 rounded-lg bg-surface-200/80 border border-surface-border text-left font-mono text-[11px] text-risk-medium overflow-x-auto max-h-32">
              <span className="text-text-muted font-bold block mb-1">Exception Details:</span>
              <code>{this.state.error.toString()}</code>
            </div>
          )}

          <div className="flex items-center gap-3 pt-2">
            <button
              type="button"
              onClick={this.handleReset}
              className="px-5 py-2.5 rounded-lg bg-brand-primary hover:bg-brand-light text-white font-mono text-xs font-bold tracking-wider flex items-center gap-2 shadow-cyber transition-all cursor-pointer"
            >
              <RefreshCw className="w-4 h-4" />
              <span>Reset &amp; Retry</span>
            </button>
            <button
              type="button"
              onClick={() => { window.location.href = '/dashboard'; }}
              className="px-4 py-2.5 rounded-lg bg-surface-200 hover:bg-surface-300 text-text-secondary hover:text-white border border-surface-border font-mono text-xs font-semibold flex items-center gap-2 transition-all cursor-pointer"
            >
              <Home className="w-4 h-4" />
              <span>Go to Dashboard</span>
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
