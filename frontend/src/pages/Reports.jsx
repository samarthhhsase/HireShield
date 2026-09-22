import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { FileText, Download, Printer, Shield, Search, ArrowRight, ExternalLink } from 'lucide-react';
import { getCandidatesList } from '../api/candidates';
import { generatePdfReport } from '../utils/generatePdfReport';

export default function Reports() {
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadReports() {
      try {
        const list = await getCandidatesList();
        setReports(list);
      } catch (err) {
        console.error('Failed to load reports', err);
      } finally {
        setLoading(false);
      }
    }
    loadReports();
  }, []);

  const handlePrint = (report) => {
    window.print();
  };

  const handleDownloadPdf = (report) => {
    generatePdfReport(report);
  };

  return (
    <div className="space-y-6 font-sans">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-white tracking-tight">
            Security Intelligence Reports
          </h2>
          <p className="text-xs text-text-muted mt-0.5">
            Compiled risk assessments, behavioral evidence summaries, and audit logs
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {reports.map((rep) => (
          <div key={rep.id} className="p-5 rounded-xl bg-surface-100 border border-surface-border glass-panel flex flex-col justify-between space-y-4">
            <div>
              <div className="flex items-center justify-between font-mono text-xs text-text-muted mb-2">
                <span>{rep.id}</span>
                <span className={`px-2 py-0.5 rounded text-[10px] font-bold border ${
                  rep.risk_level === 'CRITICAL' ? 'bg-risk-critical/15 text-risk-critical border-risk-critical/30' :
                  rep.risk_level === 'HIGH' ? 'bg-risk-high/15 text-risk-high border-risk-high/30' :
                  rep.risk_level === 'MEDIUM' ? 'bg-risk-medium/15 text-risk-medium border-risk-medium/30' :
                  'bg-risk-low/15 text-risk-low border-risk-low/30'
                }`}>
                  {rep.risk_level} ({rep.risk_score})
                </span>
              </div>

              <h3 className="font-semibold text-text-primary text-sm line-clamp-1">
                {rep.candidateName || rep.job?.title || 'Target Dossier'}
              </h3>
              <p className="text-xs text-text-muted mt-1 font-mono truncate">
                {rep.url}
              </p>

              <div className="mt-4 pt-3 border-t border-surface-border/60 text-[11px] font-mono text-text-secondary space-y-1">
                <div className="flex justify-between">
                  <span>Behavioral Flags:</span>
                  <span className="text-white font-bold">{rep.red_flags?.length || 0}</span>
                </div>
                <div className="flex justify-between">
                  <span>SSL Validation:</span>
                  <span className={rep.technical_checks?.ssl_valid ? 'text-risk-low' : 'text-risk-critical'}>
                    {rep.technical_checks?.ssl_valid ? 'SECURE' : 'INSECURE'}
                  </span>
                </div>
              </div>
            </div>

            <div className="pt-3 border-t border-surface-border flex items-center justify-between font-mono text-xs">
              <button
                onClick={() => handleDownloadPdf(rep)}
                className="inline-flex items-center gap-1.5 text-text-muted hover:text-brand-light transition-colors cursor-pointer"
                title="Download PDF Audit Report"
              >
                <Download className="w-3.5 h-3.5" />
                <span>PDF</span>
              </button>

              <Link
                to={`/risk-analysis/${rep.id}`}
                state={{ candidateData: rep }}
                className="inline-flex items-center gap-1 text-brand-light hover:text-white transition-colors"
              >
                <span>View Full Report</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </Link>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
