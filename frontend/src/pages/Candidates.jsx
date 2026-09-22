import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { 
  Users, 
  Search, 
  Filter, 
  PlusCircle, 
  LayoutGrid, 
  Table as TableIcon,
  ArrowUpDown,
  RefreshCw
} from 'lucide-react';
import CandidateTable from '../components/CandidateTable/CandidateTable';
import CandidateCard from '../components/CandidateCard/CandidateCard';
import { getCandidatesList } from '../api/candidates';

export default function Candidates() {
  const [candidates, setCandidates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedRisk, setSelectedRisk] = useState('ALL');
  const [viewMode, setViewMode] = useState('table'); // 'table' | 'grid'
  const [sortBy, setSortBy] = useState('date'); // 'date' | 'score-desc' | 'score-asc'

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const data = await getCandidatesList();
      setCandidates(data);
    } catch (err) {
      console.error('Failed to load candidates', err);
    } finally {
      setLoading(false);
    }
  };

  // Filter & Search Logic
  const filteredCandidates = candidates.filter((c) => {
    const nameMatch = (c.candidateName || c.job?.title || '').toLowerCase().includes(searchTerm.toLowerCase());
    const urlMatch = (c.url || '').toLowerCase().includes(searchTerm.toLowerCase());
    const riskMatch = selectedRisk === 'ALL' || (c.risk_level || '').toUpperCase() === selectedRisk;
    return (nameMatch || urlMatch) && riskMatch;
  });

  // Sorting
  const sortedCandidates = [...filteredCandidates].sort((a, b) => {
    if (sortBy === 'score-desc') return (b.risk_score || 0) - (a.risk_score || 0);
    if (sortBy === 'score-asc') return (a.risk_score || 0) - (b.risk_score || 0);
    return new Date(b.scannedAt || 0) - new Date(a.scannedAt || 0);
  });

  return (
    <div className="space-y-6 font-sans">

      {/* Header & Controls */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-white tracking-tight">
            Job Intelligence Registry
          </h2>
          <p className="text-xs text-text-muted mt-0.5 font-sans">
            Indexed job postings and active threat analysis dossiers
          </p>
        </div>

        <div className="flex items-center gap-3">
          {/* View mode toggle */}
          <div className="flex items-center p-1 rounded-lg bg-surface-100 border border-surface-border text-text-muted">
            <button
              onClick={() => setViewMode('table')}
              className={`p-1.5 rounded ${viewMode === 'table' ? 'bg-surface-200 text-white' : 'hover:text-white'}`}
              title="Table view"
            >
              <TableIcon className="w-4 h-4" />
            </button>
            <button
              onClick={() => setViewMode('grid')}
              className={`p-1.5 rounded ${viewMode === 'grid' ? 'bg-surface-200 text-white' : 'hover:text-white'}`}
              title="Grid card view"
            >
              <LayoutGrid className="w-4 h-4" />
            </button>
          </div>

          <Link
            to="/risk-analysis"
            className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-lg bg-brand-primary hover:bg-brand-light text-white text-xs font-mono font-semibold tracking-wide shadow-cyber transition-all"
          >
            <PlusCircle className="w-4 h-4" />
            <span>Scan New Job</span>
          </Link>
        </div>
      </div>

      {/* Search & Filter Bar */}
      <div className="p-4 rounded-xl bg-surface-100 border border-surface-border flex flex-col md:flex-row items-stretch md:items-center gap-3">
        {/* Search Input */}
        <div className="relative flex-1">
          <Search className="w-4 h-4 text-text-muted absolute left-3 top-2.5" />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search candidate name, role, or target URL..."
            className="w-full pl-9 pr-3 py-2 rounded-lg bg-surface-200 border border-surface-border text-white text-xs font-mono focus:outline-none focus:border-brand-primary"
          />
        </div>

        {/* Risk Filter Select */}
        <div className="flex items-center gap-2 font-mono text-xs">
          <Filter className="w-3.5 h-3.5 text-text-muted" />
          <select
            value={selectedRisk}
            onChange={(e) => setSelectedRisk(e.target.value)}
            className="py-2 px-3 rounded-lg bg-surface-200 border border-surface-border text-text-secondary text-xs font-mono focus:outline-none focus:border-brand-primary"
          >
            <option value="ALL">All Risk Tiers</option>
            <option value="LOW">Low Risk</option>
            <option value="MEDIUM">Medium Risk</option>
            <option value="HIGH">High Risk</option>
            <option value="CRITICAL">Critical Risk</option>
          </select>
        </div>

        {/* Sort Select */}
        <div className="flex items-center gap-2 font-mono text-xs">
          <ArrowUpDown className="w-3.5 h-3.5 text-text-muted" />
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            className="py-2 px-3 rounded-lg bg-surface-200 border border-surface-border text-text-secondary text-xs font-mono focus:outline-none focus:border-brand-primary"
          >
            <option value="date">Sort: Latest Scans</option>
            <option value="score-desc">Sort: Highest Risk</option>
            <option value="score-asc">Sort: Lowest Risk</option>
          </select>
        </div>
      </div>

      {/* Main Results View */}
      {viewMode === 'table' ? (
        <CandidateTable candidates={sortedCandidates} isLoading={loading} />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {sortedCandidates.map((c) => (
            <CandidateCard key={c.id} candidate={c} />
          ))}
        </div>
      )}
    </div>
  );
}
