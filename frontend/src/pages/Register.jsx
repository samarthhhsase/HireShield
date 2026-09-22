import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Shield, Lock, Mail, User, ArrowRight, UserPlus, AlertCircle, CheckCircle2 } from 'lucide-react';
import { registerUser } from '../api/auth';

export default function Register() {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [role, setRole] = useState('Security Analyst');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  const handleSignUp = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      await registerUser(name, email, password, role);
      navigate('/dashboard');
    } catch (err) {
      console.error('Registration error:', err);
      setError(
        err.message ||
        err.detail ||
        'Could not register analyst profile. Please check requirements.'
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background flex flex-col justify-center py-12 sm:px-6 lg:px-8 relative selection:bg-brand-primary/30 selection:text-white">
      <div className="fixed inset-0 bg-cyber-grid opacity-50 pointer-events-none" />

      <div className="sm:mx-auto sm:w-full sm:max-w-md z-10 text-center space-y-3">
        <Link to="/" className="inline-flex items-center gap-2.5">
          <div className="w-10 h-10 rounded-xl bg-surface-100 border border-brand-primary/40 flex items-center justify-center text-brand-primary shadow-cyber">
            <Shield className="w-5 h-5 fill-brand-primary/20 stroke-brand-primary" />
          </div>
          <span className="font-sans font-extrabold text-xl text-white tracking-tight">HireShield</span>
        </Link>
        <h2 className="text-xl font-bold text-white tracking-tight font-sans">
          Register Security Analyst
        </h2>
        <p className="text-xs text-text-muted font-mono">
          PROVISION CREDENTIALS // IDENTITY ENROLLMENT
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md z-10 px-4">
        {/* Active Backend Endpoint Indicator */}
        <div className="mb-4 p-3 rounded-lg bg-risk-low/10 border border-risk-low/30 text-xs font-mono flex items-center justify-between text-risk-low">
          <div className="flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 flex-shrink-0" />
            <span>POST /api/auth/register (Online)</span>
          </div>
          <span className="text-[11px] opacity-80 font-sans">SQLite Persistence</span>
        </div>

        {error && (
          <div className="mb-4 p-3.5 rounded-lg bg-risk-critical/10 border border-risk-critical/40 text-xs font-mono text-risk-critical flex items-start gap-2.5 animate-fadeIn">
            <AlertCircle className="w-4 h-4 flex-shrink-0 mt-0.5" />
            <div>
              <div className="font-semibold">REGISTRATION FAILED</div>
              <div className="text-[11px] opacity-90 mt-0.5">{error}</div>
            </div>
          </div>
        )}

        <div className="p-6 sm:p-8 rounded-xl bg-surface-100 border border-surface-border glass-panel space-y-6">
          <form onSubmit={handleSignUp} className="space-y-4 font-sans text-xs">
            <div>
              <label className="block text-text-secondary font-mono text-[11px] mb-1.5 uppercase tracking-wider">
                Full Name
              </label>
              <div className="relative">
                <User className="w-4 h-4 text-text-muted absolute left-3 top-3" />
                <input
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  required
                  className="w-full pl-9 pr-3 py-2.5 rounded-lg bg-surface-200 border border-surface-border text-white text-xs font-mono focus:outline-none focus:border-brand-primary focus:ring-1 focus:ring-brand-primary transition-all"
                  placeholder="Alex Mercer"
                />
              </div>
            </div>

            <div>
              <label className="block text-text-secondary font-mono text-[11px] mb-1.5 uppercase tracking-wider">
                Enterprise Email
              </label>
              <div className="relative">
                <Mail className="w-4 h-4 text-text-muted absolute left-3 top-3" />
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  className="w-full pl-9 pr-3 py-2.5 rounded-lg bg-surface-200 border border-surface-border text-white text-xs font-mono focus:outline-none focus:border-brand-primary focus:ring-1 focus:ring-brand-primary transition-all"
                  placeholder="analyst@enterprise.com"
                />
              </div>
            </div>

            <div>
              <label className="block text-text-secondary font-mono text-[11px] mb-1.5 uppercase tracking-wider">
                Security Password (Min. 6 chars)
              </label>
              <div className="relative">
                <Lock className="w-4 h-4 text-text-muted absolute left-3 top-3" />
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  minLength={6}
                  className="w-full pl-9 pr-3 py-2.5 rounded-lg bg-surface-200 border border-surface-border text-white text-xs font-mono focus:outline-none focus:border-brand-primary focus:ring-1 focus:ring-brand-primary transition-all"
                  placeholder="••••••••••••"
                />
              </div>
            </div>

            <div>
              <label className="block text-text-secondary font-mono text-[11px] mb-1.5 uppercase tracking-wider">
                Analyst Clearance Level
              </label>
              <select
                value={role}
                onChange={(e) => setRole(e.target.value)}
                className="w-full px-3 py-2.5 rounded-lg bg-surface-200 border border-surface-border text-white text-xs font-mono focus:outline-none focus:border-brand-primary focus:ring-1 focus:ring-brand-primary transition-all"
              >
                <option value="Security Analyst">Security Analyst</option>
                <option value="Lead Security Analyst">Lead Security Analyst</option>
                <option value="Threat Intelligence Officer">Threat Intelligence Officer</option>
                <option value="Chief Information Security Officer">Chief Information Security Officer</option>
              </select>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full py-3 rounded-lg bg-brand-primary hover:bg-brand-light disabled:opacity-50 text-white font-mono text-xs font-semibold tracking-wider flex items-center justify-center gap-2 shadow-cyber transition-all hover:scale-[1.01] active:scale-[0.99] mt-2 cursor-pointer"
            >
              {loading ? (
                <>
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  <span>Enrolling Analyst Profile...</span>
                </>
              ) : (
                <>
                  <UserPlus className="w-4 h-4" />
                  <span>Register & Launch Workspace</span>
                </>
              )}
            </button>
          </form>

          <div className="pt-4 border-t border-surface-border text-center font-mono text-[11px] text-text-muted">
            Already have an analyst account?{' '}
            <Link to="/login" className="text-brand-light hover:underline">
              Sign In
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
