import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { 
  Users, 
  Briefcase,
  SearchCode, 
  AlertOctagon, 
  Activity, 
  ArrowRight, 
  ShieldCheck, 
  TrendingUp, 
  Search,
  PlusCircle,
  ExternalLink
} from 'lucide-react';
import CandidateTable from '../components/CandidateTable/CandidateTable';
import { getCandidatesList } from '../api/candidates';
import { getStoredUser } from '../api/auth';
import { API_BASE_URL } from '../api/client';
import { 
  ResponsiveContainer, 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  Tooltip, 
  Cell 
} from 'recharts';

export default function Dashboard() {
  const [candidates, setCandidates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [quickScanUrl, setQuickScanUrl] = useState('');
  const user = getStoredUser() || { name: 'Security Analyst' };
  const navigate = useNavigate();

  useEffect(() => {
    async function loadDashboardData() {
      try {
        const list = await getCandidatesList();
        setCandidates(list);
      } catch (err) {
        console.error('Failed to load candidate list', err);
      } finally {
        setLoading(false);
      }
    }
    loadDashboardData();
  }, []);

  // Compute Metrics based on candidates
  const totalCandidates = candidates.length;
  const analysesCompleted = candidates.length;
  const highRiskCount = candidates.filter(
    (c) => (c.risk_level || '').toUpperCase() === 'HIGH' || (c.risk_level || '').toUpperCase() === 'CRITICAL'
  ).length;
  const averageRisk = totalCandidates > 0
    ? Math.round(candidates.reduce((acc, curr) => acc + (curr.risk_score || 0), 0) / totalCandidates)
    : 0;

  // Chart data: Distribution of risk levels
  const riskDistribution = [
    { name: 'Low Risk', count: candidates.filter((c) => c.risk_level === 'LOW').length, color: '#10B981' },
    { name: 'Medium Risk', count: candidates.filter((c) => c.risk_level === 'MEDIUM').length, color: '#F59E0B' },
    { name: 'High Risk', count: candidates.filter((c) => c.risk_level === 'HIGH').length, color: '#F97316' },
    { name: 'Critical', count: candidates.filter((c) => c.risk_level === 'CRITICAL').length, color: '#EF4444' },
  ];

  const handleQuickScan = (e) => {
    e.preventDefault();
    if (quickScanUrl.trim()) {
      navigate('/risk-analysis', { state: { initialUrl: quickScanUrl.trim() } });
    }
  };

  return (
    <div className="space-y-8 font-sans">
      {/* 1. Greeting & Hero Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-6 rounded-2xl bg-surface-100 border border-surface-border glass-panel">
        <div>
          <div className="text-xs font-mono text-brand-light uppercase tracking-wider mb-1">
            SECURITY INTELLIGENCE CONSOLE
          </div>
          <h2 className="text-2xl font-extrabold text-white tracking-tight">
            Good afternoon, {user.name}
          </h2>
          <p className="text-xs text-text-muted mt-1 font-sans">
            Real-time threat monitoring and recruitment risk telemetry connected to backend {API_BASE_URL}.
          </p>
        </div>

        {/* Quick URL Scan Box */}
        <form onSubmit={handleQuickScan} className="flex items-center gap-2 max-w-md w-full">
          <div className="relative flex-1">
            <Search className="w-4 h-4 text-text-muted absolute left-3 top-2.5" />
            <input
              type="url"
              value={quickScanUrl}
              onChange={(e) => setQuickScanUrl(e.target.value)}
              placeholder="Quick scan URL (https://...)"
              className="w-full pl-9 pr-3 py-2 rounded-lg bg-surface-200 border border-surface-border text-white text-xs font-mono focus:outline-none focus:border-brand-primary"
            />
          </div>
          <button
            type="submit"
            className="px-4 py-2 rounded-lg bg-brand-primary hover:bg-brand-light text-white text-xs font-mono font-semibold whitespace-nowrap shadow-cyber transition-all"
          >
            Run Scan
          </button>
        </form>
      </div>

      {/* 2. Summary Metric Cards: TOTAL JOBS, ANALYSES COMPLETED, HIGH RISK, AVERAGE RISK */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Total Jobs */}
        <div className="p-5 rounded-xl bg-surface-100 border border-surface-border glass-panel-hover">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-mono text-text-muted uppercase tracking-wider">
              TOTAL JOBS
            </span>
            <div className="p-2 rounded-lg bg-brand-primary/10 text-brand-light">
              <Briefcase className="w-4 h-4" />
            </div>
          </div>
          <div className="text-3xl font-extrabold text-white font-mono mt-3">
            {totalCandidates}
          </div>
          <div className="text-[11px] text-text-muted mt-1 font-mono">
            Analyzed & indexed job postings
          </div>
        </div>

        {/* Analyses Completed */}
        <div className="p-5 rounded-xl bg-surface-100 border border-surface-border glass-panel-hover">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-mono text-text-muted uppercase tracking-wider">
              ANALYSES COMPLETED
            </span>
            <div className="p-2 rounded-lg bg-risk-low/10 text-risk-low">
              <SearchCode className="w-4 h-4" />
            </div>
          </div>
          <div className="text-3xl font-extrabold text-white font-mono mt-3">
            {analysesCompleted}
          </div>
          <div className="text-[11px] text-risk-low mt-1 font-mono flex items-center gap-1">
            <span>100% processing rate</span>
          </div>
        </div>

        {/* High Risk / Critical */}
        <div className="p-5 rounded-xl bg-surface-100 border border-surface-border glass-panel-hover">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-mono text-text-muted uppercase tracking-wider">
              HIGH RISK
            </span>
            <div className="p-2 rounded-lg bg-risk-critical/10 text-risk-critical">
              <AlertOctagon className="w-4 h-4" />
            </div>
          </div>
          <div className="text-3xl font-extrabold text-risk-critical font-mono mt-3">
            {highRiskCount}
          </div>
          <div className="text-[11px] text-text-muted mt-1 font-mono">
            Flagged for review
          </div>
        </div>

        {/* Average Risk Score */}
        <div className="p-5 rounded-xl bg-surface-100 border border-surface-border glass-panel-hover">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-mono text-text-muted uppercase tracking-wider">
              AVERAGE RISK
            </span>
            <div className="p-2 rounded-lg bg-brand-primary/10 text-brand-light">
              <Activity className="w-4 h-4" />
            </div>
          </div>
          <div className="text-3xl font-extrabold text-white font-mono mt-3 flex items-baseline">
            <span>{averageRisk}</span>
            <span className="text-xs font-mono text-text-muted ml-1">/100</span>
          </div>
          <div className="text-[11px] text-text-muted mt-1 font-mono">
            Weighted platform average
          </div>
        </div>
      </div>

      {/* 3. Risk Overview Chart & Telemetry */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Risk Distribution Chart */}
        <div className="lg:col-span-8 p-6 rounded-xl bg-surface-100 border border-surface-border glass-panel space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-sm font-bold text-white tracking-tight">
                Risk Overview // Threat Tier Distribution
              </h3>
              <p className="text-xs text-text-muted mt-0.5">
                Distribution of candidate and posting dossiers across risk levels
              </p>
            </div>
            <span className="font-mono text-[11px] text-brand-light bg-brand-primary/10 px-2.5 py-1 rounded border border-brand-primary/20">
              REAL-TIME MATRIX
            </span>
          </div>

          <div className="h-64 w-full pt-4">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={riskDistribution} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <XAxis 
                  dataKey="name" 
                  stroke="#9AA6B5" 
                  fontSize={11} 
                  tickLine={false} 
                  fontFamily="JetBrains Mono, monospace" 
                />
                <YAxis 
                  stroke="#9AA6B5" 
                  fontSize={11} 
                  tickLine={false} 
                  allowDecimals={false}
                  fontFamily="JetBrains Mono, monospace" 
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#07111F',
                    borderColor: 'rgba(30, 58, 102, 0.4)',
                    borderRadius: '8px',
                    fontSize: '11px',
                    fontFamily: 'JetBrains Mono, monospace',
                  }}
                  itemStyle={{ color: '#F5F7FA' }}
                  cursor={{ fill: 'rgba(22, 119, 232, 0.08)' }}
                />
                <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                  {riskDistribution.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Live Risk Engine Info Box */}
        <div className="lg:col-span-4 p-6 rounded-xl bg-surface-100 border border-surface-border glass-panel flex flex-col justify-between space-y-4">
          <div>
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs font-mono text-brand-light font-semibold">
                ACTIVE PIPELINE
              </span>
              <span className="w-2 h-2 rounded-full bg-brand-light animate-pulse" />
            </div>

            <h4 className="text-sm font-bold text-white mb-1">
              HireShield FastAPI Engine
            </h4>
            <p className="text-xs text-text-muted leading-relaxed mb-4">
              Scrapes job targets, inspects DNS/SSL, executes behavioral heuristics, and produces explainable red flag evidence.
            </p>

            <div className="space-y-2 font-mono text-xs">
              <div className="p-2.5 rounded bg-surface-200 border border-surface-border flex justify-between">
                <span className="text-text-muted">Behavioral Weight</span>
                <span className="text-white font-bold">35%</span>
              </div>
              <div className="p-2.5 rounded bg-surface-200 border border-surface-border flex justify-between">
                <span className="text-text-muted">Linguistic Weight</span>
                <span className="text-white font-bold">25%</span>
              </div>
              <div className="p-2.5 rounded bg-surface-200 border border-surface-border flex justify-between">
                <span className="text-text-muted">Structural Weight</span>
                <span className="text-white font-bold">20%</span>
              </div>
              <div className="p-2.5 rounded bg-surface-200 border border-surface-border flex justify-between">
                <span className="text-text-muted">Technical Weight</span>
                <span className="text-white font-bold">20%</span>
              </div>
            </div>
          </div>

          <Link
            to="/risk-analysis"
            className="w-full py-2.5 rounded-lg bg-brand-primary hover:bg-brand-light text-white text-xs font-mono font-semibold flex items-center justify-center gap-2 shadow-cyber transition-all"
          >
            <span>Launch Deep Scan</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>
      </div>

      {/* 4. Recent Candidate Analyses Table */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-base font-bold text-white tracking-tight font-sans">
              Recent Analyses // Job Registry
            </h3>
            <p className="text-xs text-text-muted font-sans mt-0.5">
              Evaluated job postings and threat dossiers
            </p>
          </div>

          <Link
            to="/jobs"
            className="text-xs font-mono text-brand-light hover:text-white transition-colors flex items-center gap-1"
          >
            <span>View All ({candidates.length})</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        <CandidateTable candidates={candidates.slice(0, 6)} isLoading={loading} />
      </div>
    </div>
  );
}
