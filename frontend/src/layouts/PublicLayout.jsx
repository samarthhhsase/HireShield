import React from 'react';
import { Outlet } from 'react-router-dom';
import Navbar from '../components/Navbar/Navbar';
import { API_BASE_URL } from '../api/client';

export default function PublicLayout() {
  return (
    <div className="min-h-screen bg-background text-text-primary flex flex-col selection:bg-brand-primary/30 selection:text-white relative">
      {/* Background Cyber Grid */}
      <div className="fixed inset-0 bg-cyber-grid opacity-60 pointer-events-none z-0" />
      <div className="fixed inset-0 bg-gradient-to-b from-transparent via-background/60 to-background pointer-events-none z-0" />

      {/* Global Navbar */}
      <Navbar />

      {/* Page Content */}
      <main className="flex-1 z-10">
        <Outlet />
      </main>

      {/* Footer */}
      <footer className="border-t border-surface-border bg-surface-200/50 py-12 px-4 sm:px-6 lg:px-8 z-10 font-sans text-xs">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-6">
          <div className="flex items-center gap-3">
            <span className="font-bold text-white tracking-tight">HireShield</span>
            <span className="text-text-muted">|</span>
            <span className="text-text-muted">AI-Powered Recruitment Risk Intelligence & Candidate Verification</span>
          </div>

          <div className="flex items-center gap-6 font-mono text-[11px] text-text-muted">
            <span>FastAPI Risk Engine</span>
            <span>Status: Operational</span>
          </div>
        </div>
      </footer>
    </div>
  );
}
