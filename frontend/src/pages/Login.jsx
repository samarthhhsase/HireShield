import React, { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { 
  Shield, 
  Lock, 
  Mail, 
  ArrowRight, 
  Eye, 
  EyeOff, 
  CheckCircle2, 
  AlertCircle, 
  ShieldCheck, 
  Activity, 
  Cpu, 
  KeyRound, 
  LogIn 
} from 'lucide-react';
import { loginUser } from '../api/auth';

export default function Login() {
  const navigate = useNavigate();
  const location = useLocation();

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Where to redirect after login (default /dashboard)
  const from = location.state?.from?.pathname || '/dashboard';

  const handleSignIn = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      await loginUser(email.trim(), password);
      navigate(from, { replace: true });
    } catch (err) {
      console.error('Login error:', err);
      setError(
        err.message ||
        err.detail ||
        'Authentication rejected. Verify your work email and password.'
      );
    } finally {
      setLoading(false);
    }
  };

  const handleFillDemo = () => {
    setEmail('analyst@hireshield.ai');
    setPassword('Password123!');
    setError(null);
  };

  return (
    <div className="min-h-screen bg-background text-text-primary flex selection:bg-brand-primary/30 selection:text-white relative overflow-hidden">
      {/* Background Cyber Grid */}
      <div className="fixed inset-0 bg-cyber-grid opacity-40 pointer-events-none" />
      <div className="fixed inset-0 bg-gradient-to-tr from-surface-300 via-transparent to-brand-primary/5 pointer-events-none" />

      <div className="w-full flex flex-col lg:flex-row min-h-screen z-10">
        {/* ================================================================= */}
        {/* LEFT SIDE: Brand Intelligence & Cybersecurity Visual Presentation */}
        {/* ================================================================= */}
        <div className="lg:w-1/2 p-8 sm:p-12 lg:p-16 flex flex-col justify-between border-b lg:border-b-0 lg:border-r border-surface-border bg-surface-200/50 backdrop-blur-sm relative">
          <div className="absolute top-1/3 left-1/4 w-96 h-96 bg-brand-primary/10 rounded-full blur-3xl pointer-events-none" />

          {/* Top Brand Tag */}
          <div className="relative z-10">
            <Link to="/" className="inline-flex items-center gap-3 group">
              <div className="w-10 h-10 rounded-xl bg-surface-100 border border-surface-border-highlight flex items-center justify-center text-brand-primary shadow-cyber group-hover:border-brand-primary transition-all">
                <Shield className="w-5 h-5 fill-brand-primary/20 stroke-brand-primary" />
              </div>
              <div>
                <span className="font-sans font-extrabold text-xl text-white tracking-tight">HIRE<span className="text-brand-light">SHIELD</span></span>
                <span className="block font-mono text-[9px] text-brand-light/80 tracking-widest uppercase">ENTERPRISE INTELLIGENCE</span>
              </div>
            </Link>
          </div>

          {/* Center: Mission Typography & Radar Visual */}
          <div className="my-12 lg:my-auto space-y-8 relative z-10">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-brand-primary/10 border border-brand-primary/30 text-brand-light font-mono text-[11px] tracking-wider uppercase">
              <span className="w-2 h-2 rounded-full bg-brand-light animate-ping" />
              Zero-Trust Recruitment Risk Engine
            </div>

            <div className="space-y-4">
              <h1 className="text-3xl sm:text-4xl lg:text-5xl font-extrabold font-sans text-white tracking-tight leading-tight">
                Secure the hiring decision.
              </h1>
              <p className="text-base sm:text-lg text-text-secondary font-sans max-w-lg leading-relaxed">
                Detect recruitment risk, candidate threat signals, and deceptive job patterns before it becomes an enterprise problem.
              </p>
            </div>

            {/* Shield & Network Radar Visualization */}
            <div className="relative w-full max-w-md h-56 rounded-2xl bg-surface-100/60 border border-surface-border p-6 overflow-hidden shadow-cyber">
              {/* Radar Rings */}
              <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
                <div className="w-72 h-72 rounded-full border border-brand-primary/10 animate-pulse" />
                <div className="absolute w-48 h-48 rounded-full border border-brand-primary/20" />
                <div className="absolute w-24 h-24 rounded-full border border-brand-primary/30" />
              </div>

              {/* Central Glowing Shield */}
              <div className="relative z-10 h-full flex flex-col justify-between">
                <div className="flex items-center justify-between font-mono text-[10px] text-text-muted">
                  <span className="flex items-center gap-1.5 text-brand-light">
                    <Activity className="w-3.5 h-3.5" /> SECURE CONSOLE // GATEWAY
                  </span>
                  <span className="text-risk-low flex items-center gap-1">
                    <span className="w-1.5 h-1.5 rounded-full bg-risk-low animate-pulse" /> PROTECTED
                  </span>
                </div>

                <div className="flex items-center justify-center gap-4 py-2">
                  <div className="w-16 h-16 rounded-2xl bg-surface-50 border border-brand-primary/40 flex items-center justify-center text-brand-primary shadow-cyber-lg">
                    <ShieldCheck className="w-8 h-8 text-brand-light" />
                  </div>
                  <div className="space-y-1">
                    <div className="text-sm font-bold font-sans text-white">HireShield Authenticator</div>
                    <div className="text-xs font-mono text-text-secondary">JWT Cryptographic Session Gateway</div>
                    <div className="text-[11px] font-mono text-brand-light">Status: TLS 1.3 Active // Tamper-Proof</div>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-2 pt-2 border-t border-surface-border/60 font-mono text-[10px]">
                  <div className="text-text-muted">
                    Session Protocol: <span className="text-white font-bold">HMAC-SHA256</span>
                  </div>
                  <div className="text-text-muted text-right">
                    Clearance: <span className="text-brand-light font-bold">Role-Based RBAC</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Bottom Security Assurance */}
          <div className="relative z-10 pt-4 flex items-center gap-4 font-mono text-xs text-text-muted">
            <div className="flex items-center gap-1.5">
              <Cpu className="w-3.5 h-3.5 text-brand-light" />
              <span>SOC2 Type II Ready</span>
            </div>
            <span>&bull;</span>
            <span>PBKDF2 Password Hashing</span>
            <span>&bull;</span>
            <span>Zero Plaintext Storage</span>
          </div>
        </div>

        {/* ================================================================= */}
        {/* RIGHT SIDE: Login Authentication Form                             */}
        {/* ================================================================= */}
        <div className="lg:w-1/2 p-6 sm:p-12 lg:p-16 flex flex-col justify-center items-center relative">
          <div className="w-full max-w-md space-y-6">
            <div className="space-y-2 text-left">
              <div className="font-mono text-xs text-brand-light tracking-wider uppercase flex items-center gap-2">
                <span className="w-1.5 h-1.5 rounded-full bg-brand-primary" />
                SECURITY OPERATIONS GATEWAY
              </div>
              <h2 className="text-2xl sm:text-3xl font-bold font-sans text-white tracking-tight">
                SIGN IN TO HIRESHIELD
              </h2>
              <p className="text-xs sm:text-sm text-text-muted font-sans">
                Access your recruitment threat intelligence workspace.
              </p>
            </div>

            {/* Quick Demo Credentials Autofill Helper */}
            <div className="p-3 rounded-xl bg-brand-primary/10 border border-brand-primary/30 text-xs font-mono flex items-center justify-between">
              <div className="flex items-center gap-2 text-brand-light">
                <CheckCircle2 className="w-4 h-4 flex-shrink-0" />
                <span>FastAPI Auth Gateway Online</span>
              </div>
              <button
                type="button"
                onClick={handleFillDemo}
                className="text-[11px] text-text-muted hover:text-white flex items-center gap-1.5 transition-colors underline cursor-pointer"
                title="Auto-fill default seeded analyst credentials"
              >
                <KeyRound className="w-3.5 h-3.5 text-brand-light" />
                <span>Fill Demo</span>
              </button>
            </div>

            {/* Error Notification */}
            {error && (
              <div className="p-4 rounded-xl bg-risk-critical/10 border border-risk-critical/40 text-xs font-mono text-risk-critical flex items-start gap-3 animate-fadeIn">
                <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
                <div>
                  <div className="font-semibold uppercase tracking-wider">Authentication Rejected</div>
                  <div className="text-[11px] opacity-90 mt-0.5 leading-relaxed">{error}</div>
                </div>
              </div>
            )}

            {/* Login Form Card */}
            <div className="p-6 sm:p-8 rounded-2xl bg-surface-100 border border-surface-border glass-panel">
              <form onSubmit={handleSignIn} className="space-y-4 font-sans text-xs">
                {/* Work Email */}
                <div>
                  <label className="block text-text-secondary font-mono text-[11px] mb-1.5 uppercase tracking-wider">
                    Work Email
                  </label>
                  <div className="relative">
                    <Mail className="w-4 h-4 text-text-muted absolute left-3 top-3" />
                    <input
                      type="email"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      required
                      className="w-full pl-9 pr-3 py-2.5 rounded-lg bg-surface-200 border border-surface-border text-white text-xs font-mono transition-all focus:outline-none focus:border-brand-primary focus:ring-1 focus:ring-brand-primary"
                      placeholder="analyst@hireshield.ai"
                    />
                  </div>
                </div>

                {/* Password with Eye Toggle */}
                <div>
                  <label className="block text-text-secondary font-mono text-[11px] mb-1.5 uppercase tracking-wider">
                    Password
                  </label>
                  <div className="relative">
                    <Lock className="w-4 h-4 text-text-muted absolute left-3 top-3" />
                    <input
                      type={showPassword ? 'text' : 'password'}
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      required
                      className="w-full pl-9 pr-10 py-2.5 rounded-lg bg-surface-200 border border-surface-border text-white text-xs font-mono transition-all focus:outline-none focus:border-brand-primary focus:ring-1 focus:ring-brand-primary"
                      placeholder="••••••••••••"
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute right-3 top-2.5 text-text-muted hover:text-white transition-colors"
                      aria-label="Toggle password visibility"
                    >
                      {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                    </button>
                  </div>
                </div>

                {/* Submit Button */}
                <button
                  type="submit"
                  disabled={loading}
                  className="w-full py-3.5 rounded-xl bg-brand-primary hover:bg-brand-light disabled:opacity-50 text-white font-mono text-xs font-semibold tracking-wider flex items-center justify-center gap-2 shadow-cyber transition-all hover:scale-[1.01] active:scale-[0.99] mt-3 cursor-pointer"
                >
                  {loading ? (
                    <>
                      <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                      <span>AUTHENTICATING...</span>
                    </>
                  ) : (
                    <>
                      <LogIn className="w-4 h-4" />
                      <span>SIGN IN</span>
                    </>
                  )}
                </button>
              </form>

              {/* Create Account Link */}
              <div className="pt-5 mt-5 border-t border-surface-border text-center font-mono text-xs text-text-muted">
                Don't have an account?{' '}
                <Link to="/signup" className="text-brand-light hover:underline font-semibold">
                  Create account
                </Link>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
