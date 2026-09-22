import React, { useState } from 'react';
import { Outlet, Link, useLocation } from 'react-router-dom';
import Sidebar from '../components/Sidebar/Sidebar';
import { Menu, Search, PlusCircle, Bell, Shield, ArrowRight } from 'lucide-react';
import { API_BASE_URL } from '../api/client';

export default function DashboardLayout() {
  const [mobileSidebarOpen, setMobileSidebarOpen] = useState(false);
  const location = useLocation();

  const getPageTitle = (path) => {
    if (path.startsWith('/risk-analysis')) return 'Threat Analysis Engine';
    if (path.startsWith('/jobs') || path.startsWith('/candidates')) return 'Job Intelligence Registry';
    if (path.startsWith('/reports')) return 'Security Audit Reports';
    if (path.startsWith('/activity')) return 'API Telemetry & Activity';
    if (path.startsWith('/settings')) return 'Platform Configuration';
    if (path.startsWith('/profile')) return 'Analyst Profile';
    return 'Security Operations Dashboard';
  };

  return (
    <div className="min-h-screen bg-background text-text-primary flex selection:bg-brand-primary/30 selection:text-white">
      {/* Persistent Sidebar */}
      <Sidebar mobileOpen={mobileSidebarOpen} setMobileOpen={setMobileSidebarOpen} />

      {/* Main Workspace Area */}
      <div className="flex-1 lg:pl-64 flex flex-col min-w-0">
        {/* Top Header */}
        <header className="h-16 border-b border-surface-border bg-surface-200/80 backdrop-blur-md px-4 sm:px-6 lg:px-8 flex items-center justify-between sticky top-0 z-30">
          <div className="flex items-center gap-3">
            <button
              onClick={() => setMobileSidebarOpen(true)}
              className="p-2 rounded-lg text-text-muted hover:text-white hover:bg-surface-100 lg:hidden"
              aria-label="Open sidebar"
            >
              <Menu className="w-5 h-5" />
            </button>
            <div>
              <h1 className="text-sm font-semibold text-white tracking-tight font-sans">
                {getPageTitle(location.pathname)}
              </h1>
              <div className="text-[10px] font-mono text-text-muted">
                SESSION // SEC-OPS // LIVE INTELLIGENCE
              </div>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <Link
              to="/risk-analysis"
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-brand-primary hover:bg-brand-light text-white text-xs font-mono font-semibold tracking-wide shadow-cyber transition-all"
            >
              <PlusCircle className="w-3.5 h-3.5" />
              <span className="hidden sm:inline">New Threat Scan</span>
            </Link>
          </div>
        </header>

        {/* Workspace Canvas */}
        <main className="flex-1 p-4 sm:p-6 lg:p-8 overflow-y-auto max-w-7xl w-full mx-auto">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
