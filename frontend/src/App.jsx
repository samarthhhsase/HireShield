import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';

// Layouts
import PublicLayout from './layouts/PublicLayout';
import DashboardLayout from './layouts/DashboardLayout';

// Route Guard
import ProtectedRoute from './components/Common/ProtectedRoute';

// Pages
import Landing from './pages/Landing';
import Login from './pages/Login';
import Signup from './pages/Signup';
import Dashboard from './pages/Dashboard';
import Candidates from './pages/Candidates';
import CandidateDetails from './pages/CandidateDetails';
import RiskAnalysis from './pages/RiskAnalysis';
import Reports from './pages/Reports';
import Activity from './pages/Activity';
import { API_BASE_URL } from './api/client';

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Public Marketing Landing Routes */}
        <Route element={<PublicLayout />}>
          <Route path="/" element={<Landing />} />
        </Route>

        {/* Dedicated Enterprise Auth Pages */}
        <Route path="/login" element={<Login />} />
        <Route path="/signup" element={<Signup />} />
        {/* Backward-compatibility alias for /register */}
        <Route path="/register" element={<Navigate to="/signup" replace />} />

        {/* Authenticated Workspace Routes (Protected by JWT Guard) */}
        <Route
          element={
            <ProtectedRoute>
              <DashboardLayout />
            </ProtectedRoute>
          }
        >
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/jobs" element={<Candidates />} />
          <Route path="/jobs/:id" element={<CandidateDetails />} />
          <Route path="/candidates" element={<Navigate to="/jobs" replace />} />
          <Route path="/candidates/:id" element={<CandidateDetails />} />
          <Route path="/risk-analysis" element={<RiskAnalysis />} />
          <Route path="/risk-analysis/:id" element={<RiskAnalysis />} />
          <Route path="/scanner" element={<Navigate to="/risk-analysis" replace />} />
          <Route path="/reports" element={<Reports />} />
          <Route path="/activity" element={<Activity />} />
          
          {/* Settings & Profile stubs */}
          <Route path="/settings" element={
            <div className="p-6 rounded-xl bg-surface-100 border border-surface-border font-mono text-xs">
              <h2 className="text-base font-bold text-white mb-2">Platform Configuration // Settings</h2>
              <p className="text-text-muted">FastAPI host: {API_BASE_URL} &bull; Heuristic engine: active &bull; Logging: stdout</p>
            </div>
          } />
          <Route path="/profile" element={
            <div className="p-6 rounded-xl bg-surface-100 border border-surface-border font-mono text-xs">
              <h2 className="text-base font-bold text-white mb-2">Analyst Profile</h2>
              <p className="text-text-muted">Identity: Lead Security Analyst &bull; Clearance: Tier-3 SecOps &bull; Session: Active</p>
            </div>
          } />
        </Route>

        {/* Catch-all fallback */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
