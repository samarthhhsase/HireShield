import React, { useState, useMemo } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { 
  Shield, 
  Lock, 
  Mail, 
  User, 
  ArrowRight, 
  Eye, 
  EyeOff, 
  CheckCircle2, 
  AlertCircle, 
  ShieldCheck, 
  Activity, 
  Cpu, 
  Check, 
  X,
  Database
} from 'lucide-react';
import { signupUser } from '../api/auth';

export default function Signup() {
  const navigate = useNavigate();

  // Form inputs: First Name, Second Name, Email, Password, Confirm Password
  const [firstName, setFirstName] = useState('');
  const [secondName, setSecondName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');

  // UI state
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [serverError, setServerError] = useState(null);
  const [isSuccess, setIsSuccess] = useState(false);
  const [createdUser, setCreatedUser] = useState(null);

  // Touched states for validation feedback
  const [touched, setTouched] = useState({
    firstName: false,
    secondName: false,
    email: false,
    password: false,
    confirmPassword: false,
  });

  const markTouched = (field) => {
    setTouched((prev) => ({ ...prev, [field]: true }));
  };

  // Password strength evaluation
  const passwordCriteria = useMemo(() => {
    return {
      minLength: password.length >= 6,
      hasUpper: /[A-Z]/.test(password),
      hasLower: /[a-z]/.test(password),
      hasNumber: /[0-9]/.test(password),
    };
  }, [password]);

  const passwordScore = useMemo(() => {
    if (!password) return 0;
    let score = 0;
    if (passwordCriteria.minLength) score += 1;
    if (passwordCriteria.hasUpper) score += 1;
    if (passwordCriteria.hasLower) score += 1;
    if (passwordCriteria.hasNumber) score += 1;
    return score;
  }, [passwordCriteria, password]);

  const strengthLabel = useMemo(() => {
    if (passwordScore === 0) return { text: 'Empty', color: 'text-text-muted', barColor: 'bg-surface-border' };
    if (passwordScore <= 2) return { text: 'Weak', color: 'text-risk-critical', barColor: 'bg-risk-critical' };
    if (passwordScore === 3) return { text: 'Fair', color: 'text-risk-medium', barColor: 'bg-risk-medium' };
    return { text: 'Strong', color: 'text-risk-low', barColor: 'bg-risk-low' };
  }, [passwordScore]);

  // Validation checks
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  const isEmailValid = emailRegex.test(email.trim());
  const isFirstNameValid = firstName.trim().length >= 1;
  const isSecondNameValid = secondName.trim().length >= 1;
  const isPasswordValid = password.length >= 6;
  const doPasswordsMatch = password && confirmPassword && password === confirmPassword;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setServerError(null);

    // Validate all fields
    setTouched({
      firstName: true,
      secondName: true,
      email: true,
      password: true,
      confirmPassword: true,
    });

    if (!isFirstNameValid) {
      setServerError('First Name is required.');
      return;
    }
    if (!isSecondNameValid) {
      setServerError('Second Name is required.');
      return;
    }
    if (!isEmailValid) {
      setServerError('Please enter a valid email address.');
      return;
    }
    if (!isPasswordValid) {
      setServerError('Password must be at least 6 characters.');
      return;
    }
    if (!doPasswordsMatch) {
      setServerError('Passwords do not match.');
      return;
    }

    setLoading(true);

    try {
      const result = await signupUser({
        first_name: firstName,
        second_name: secondName,
        email,
        password,
        confirm_password: confirmPassword,
      });

      setCreatedUser(result.user);
      setIsSuccess(true);
    } catch (err) {
      console.error('Signup error:', err);
      setServerError(
        err.message ||
        err.detail ||
        'An error occurred while linking to the database. Please try again.'
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background text-text-primary flex selection:bg-brand-primary/30 selection:text-white relative overflow-hidden">
      {/* Background Cyber Grid */}
      <div className="fixed inset-0 bg-cyber-grid opacity-40 pointer-events-none" />
      <div className="fixed inset-0 bg-gradient-to-tr from-surface-300 via-transparent to-brand-primary/5 pointer-events-none" />

      <div className="w-full flex flex-col lg:flex-row min-h-screen z-10">
        {/* ================================================================= */}
        {/* LEFT SIDE: Brand Intelligence & Database Verification Presentation */}
        {/* ================================================================= */}
        <div className="lg:w-1/2 p-8 sm:p-12 lg:p-16 flex flex-col justify-between border-b lg:border-b-0 lg:border-r border-surface-border bg-surface-200/50 backdrop-blur-sm relative">
          {/* Subtle Ambient Radial Glow */}
          <div className="absolute top-1/3 left-1/4 w-96 h-96 bg-brand-primary/10 rounded-full blur-3xl pointer-events-none" />

          {/* Top Brand Tag */}
          <div className="relative z-10">
            <Link to="/" className="inline-flex items-center gap-3 group">
              <div className="w-10 h-10 rounded-xl bg-surface-100 border border-surface-border-highlight flex items-center justify-center text-brand-primary shadow-cyber group-hover:border-brand-primary transition-all">
                <Shield className="w-5 h-5 fill-brand-primary/20 stroke-brand-primary" />
              </div>
              <div>
                <span className="font-sans font-extrabold text-xl text-white tracking-tight">HIRE<span className="text-brand-light">SHIELD</span></span>
                <span className="block font-mono text-[9px] text-brand-light/80 tracking-widest uppercase">DATABASE LINKED</span>
              </div>
            </Link>
          </div>

          {/* Center: Mission Typography & Connected Database Telemetry */}
          <div className="my-12 lg:my-auto space-y-8 relative z-10">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-brand-primary/10 border border-brand-primary/30 text-brand-light font-mono text-[11px] tracking-wider uppercase">
              <span className="w-2 h-2 rounded-full bg-brand-light animate-ping" />
              SQLite Database Connected &bull; Real-Time Auth
            </div>

            <div className="space-y-4">
              <h1 className="text-3xl sm:text-4xl lg:text-5xl font-extrabold font-sans text-white tracking-tight leading-tight">
                Create your analyst account.
              </h1>
              <p className="text-base sm:text-lg text-text-secondary font-sans max-w-lg leading-relaxed">
                Enter your details to register directly into the HireShield database and unlock recruitment risk intelligence.
              </p>
            </div>

            {/* Database & Security Card */}
            <div className="relative w-full max-w-md h-56 rounded-2xl bg-surface-100/60 border border-surface-border p-6 overflow-hidden shadow-cyber">
              {/* Radar Rings */}
              <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
                <div className="w-72 h-72 rounded-full border border-brand-primary/10 animate-pulse" />
                <div className="absolute w-48 h-48 rounded-full border border-brand-primary/20" />
                <div className="absolute w-24 h-24 rounded-full border border-brand-primary/30" />
              </div>

              {/* Central Glowing Shield with Database Indicator */}
              <div className="relative z-10 h-full flex flex-col justify-between">
                <div className="flex items-center justify-between font-mono text-[10px] text-text-muted">
                  <span className="flex items-center gap-1.5 text-brand-light">
                    <Database className="w-3.5 h-3.5" /> DB_STATUS // CONNECTED
                  </span>
                  <span className="text-risk-low flex items-center gap-1">
                    <span className="w-1.5 h-1.5 rounded-full bg-risk-low animate-pulse" /> SYNCED
                  </span>
                </div>

                <div className="flex items-center justify-center gap-4 py-2">
                  <div className="w-16 h-16 rounded-2xl bg-surface-50 border border-brand-primary/40 flex items-center justify-center text-brand-primary shadow-cyber-lg">
                    <ShieldCheck className="w-8 h-8 text-brand-light" />
                  </div>
                  <div className="space-y-1">
                    <div className="text-sm font-bold font-sans text-white">HireShield SQLite Vault</div>
                    <div className="text-xs font-mono text-text-secondary">hireshield.db &bull; users table active</div>
                    <div className="text-[11px] font-mono text-brand-light">PBKDF2-HMAC-SHA256 Encryption</div>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-2 pt-2 border-t border-surface-border/60 font-mono text-[10px]">
                  <div className="text-text-muted">
                    Database Driver: <span className="text-white font-bold">SQLAlchemy / SQLite</span>
                  </div>
                  <div className="text-text-muted text-right">
                    Table: <span className="text-brand-light font-bold">users</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Bottom Security Assurance */}
          <div className="relative z-10 pt-4 flex items-center gap-4 font-mono text-xs text-text-muted">
            <div className="flex items-center gap-1.5">
              <Cpu className="w-3.5 h-3.5 text-brand-light" />
              <span>Persistent Storage</span>
            </div>
            <span>&bull;</span>
            <span>PBKDF2 Hash</span>
            <span>&bull;</span>
            <span>FastAPI v1.0</span>
          </div>
        </div>

        {/* ================================================================= */}
        {/* RIGHT SIDE: Account Provisioning Form or Success State            */}
        {/* ================================================================= */}
        <div className="lg:w-1/2 p-6 sm:p-12 lg:p-16 flex flex-col justify-center items-center relative">
          <div className="w-full max-w-md space-y-6">

            {/* ============================================================= */}
            {/* SUCCESS SCREEN STATE                                          */}
            {/* ============================================================= */}
            {isSuccess ? (
              <div className="p-8 rounded-2xl bg-surface-100 border border-surface-border-highlight glass-panel text-center space-y-6 animate-fadeIn shadow-cyber-lg">
                <div className="w-16 h-16 mx-auto rounded-2xl bg-risk-low/10 border border-risk-low/40 flex items-center justify-center text-risk-low shadow-risk-low animate-bounce">
                  <CheckCircle2 className="w-9 h-9" />
                </div>

                <div className="space-y-2">
                  <span className="font-mono text-[11px] text-risk-low tracking-widest uppercase font-semibold">
                    SAVED TO DATABASE // SUCCESS
                  </span>
                  <h2 className="text-2xl font-bold font-sans text-white tracking-tight">
                    ACCOUNT CREATED
                  </h2>
                  <p className="text-xs sm:text-sm text-text-secondary font-sans leading-relaxed">
                    Your details have been successfully stored in the HireShield database.
                  </p>
                </div>

                {createdUser && (
                  <div className="p-4 rounded-xl bg-surface-200 border border-surface-border font-mono text-xs text-left space-y-2">
                    <div className="text-[10px] text-text-muted uppercase tracking-wider">Registered Record</div>
                    <div className="text-white font-medium">
                      Name: {createdUser.first_name || ''} {createdUser.second_name || createdUser.full_name || createdUser.name}
                    </div>
                    <div className="text-text-secondary truncate">
                      Email: {createdUser.email}
                    </div>
                    <div className="text-brand-light text-[11px] flex items-center gap-1 mt-1 pt-1 border-t border-surface-border/40">
                      <Database className="w-3 h-3 text-brand-light" />
                      <span>Stored in: hireshield.db (users table)</span>
                    </div>
                  </div>
                )}

                <div className="pt-2 flex flex-col sm:flex-row gap-3">
                  <Link
                    to="/dashboard"
                    className="flex-1 py-3 px-4 rounded-xl bg-brand-primary hover:bg-brand-light text-white font-mono text-xs font-semibold tracking-wider flex items-center justify-center gap-2 shadow-cyber transition-all hover:scale-[1.01] active:scale-[0.99]"
                  >
                    <span>GO TO DASHBOARD</span>
                    <ArrowRight className="w-4 h-4" />
                  </Link>
                  <Link
                    to="/login"
                    className="py-3 px-4 rounded-xl bg-surface-200 hover:bg-surface-300 border border-surface-border text-text-primary font-mono text-xs font-semibold tracking-wider flex items-center justify-center gap-2 transition-colors"
                  >
                    <span>SIGN IN</span>
                  </Link>
                </div>

                <p className="text-[11px] font-mono text-text-muted">
                  Ready to access the HireShield Risk Engine
                </p>
              </div>
            ) : (
              /* =========================================================== */
              /* SIGNUP FORM: First Name, Second Name, Email, Password       */
              /* =========================================================== */
              <div className="space-y-6">
                <div className="space-y-2 text-left">
                  <div className="font-mono text-xs text-brand-light tracking-wider uppercase flex items-center gap-2">
                    <span className="w-1.5 h-1.5 rounded-full bg-brand-primary" />
                    CREATE YOUR ACCOUNT
                  </div>
                  <h2 className="text-2xl sm:text-3xl font-bold font-sans text-white tracking-tight">
                    SIGN UP
                  </h2>
                  <p className="text-xs sm:text-sm text-text-muted font-sans">
                    Please provide your name, email, and password.
                  </p>
                </div>

                {/* Server Error Notification */}
                {serverError && (
                  <div className="p-4 rounded-xl bg-risk-critical/10 border border-risk-critical/40 text-xs font-mono text-risk-critical flex items-start gap-3 animate-fadeIn">
                    <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
                    <div>
                      <div className="font-semibold uppercase tracking-wider">Registration Error</div>
                      <div className="text-[11px] opacity-90 mt-0.5 leading-relaxed">{serverError}</div>
                    </div>
                  </div>
                )}

                {/* Form Card */}
                <div className="p-6 sm:p-8 rounded-2xl bg-surface-100 border border-surface-border glass-panel">
                  <form onSubmit={handleSubmit} className="space-y-4 font-sans text-xs">
                    {/* First Name & Second Name Row */}
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                      {/* First Name */}
                      <div>
                        <div className="flex justify-between items-center mb-1.5">
                          <label className="text-text-secondary font-mono text-[11px] uppercase tracking-wider">
                            First Name <span className="text-risk-critical">*</span>
                          </label>
                          {touched.firstName && !isFirstNameValid && (
                            <span className="font-mono text-[10px] text-risk-critical">Required</span>
                          )}
                        </div>
                        <div className="relative">
                          <User className="w-4 h-4 text-text-muted absolute left-3 top-3" />
                          <input
                            type="text"
                            value={firstName}
                            onChange={(e) => setFirstName(e.target.value)}
                            onBlur={() => markTouched('firstName')}
                            required
                            className={`w-full pl-9 pr-3 py-2.5 rounded-lg bg-surface-200 border text-white text-xs font-mono transition-all focus:outline-none focus:ring-1 ${
                              touched.firstName && !isFirstNameValid
                                ? 'border-risk-critical/60 focus:border-risk-critical focus:ring-risk-critical'
                                : 'border-surface-border focus:border-brand-primary focus:ring-brand-primary'
                            }`}
                            placeholder="e.g. John"
                            id="signup-firstname"
                          />
                        </div>
                      </div>

                      {/* Second Name */}
                      <div>
                        <div className="flex justify-between items-center mb-1.5">
                          <label className="text-text-secondary font-mono text-[11px] uppercase tracking-wider">
                            Second Name <span className="text-risk-critical">*</span>
                          </label>
                          {touched.secondName && !isSecondNameValid && (
                            <span className="font-mono text-[10px] text-risk-critical">Required</span>
                          )}
                        </div>
                        <div className="relative">
                          <User className="w-4 h-4 text-text-muted absolute left-3 top-3" />
                          <input
                            type="text"
                            value={secondName}
                            onChange={(e) => setSecondName(e.target.value)}
                            onBlur={() => markTouched('secondName')}
                            required
                            className={`w-full pl-9 pr-3 py-2.5 rounded-lg bg-surface-200 border text-white text-xs font-mono transition-all focus:outline-none focus:ring-1 ${
                              touched.secondName && !isSecondNameValid
                                ? 'border-risk-critical/60 focus:border-risk-critical focus:ring-risk-critical'
                                : 'border-surface-border focus:border-brand-primary focus:ring-brand-primary'
                            }`}
                            placeholder="e.g. Doe"
                            id="signup-secondname"
                          />
                        </div>
                      </div>
                    </div>

                    {/* Email */}
                    <div>
                      <div className="flex justify-between items-center mb-1.5">
                        <label className="text-text-secondary font-mono text-[11px] uppercase tracking-wider">
                          Email <span className="text-risk-critical">*</span>
                        </label>
                        {touched.email && !isEmailValid && (
                          <span className="font-mono text-[10px] text-risk-critical">Invalid email</span>
                        )}
                      </div>
                      <div className="relative">
                        <Mail className="w-4 h-4 text-text-muted absolute left-3 top-3" />
                        <input
                          type="email"
                          value={email}
                          onChange={(e) => setEmail(e.target.value)}
                          onBlur={() => markTouched('email')}
                          required
                          className={`w-full pl-9 pr-3 py-2.5 rounded-lg bg-surface-200 border text-white text-xs font-mono transition-all focus:outline-none focus:ring-1 ${
                            touched.email && !isEmailValid
                              ? 'border-risk-critical/60 focus:border-risk-critical focus:ring-risk-critical'
                              : 'border-surface-border focus:border-brand-primary focus:ring-brand-primary'
                          }`}
                          placeholder="e.g. john.doe@enterprise.com"
                          id="signup-email"
                        />
                      </div>
                    </div>

                    {/* Password with Eye Toggle */}
                    <div>
                      <div className="flex justify-between items-center mb-1.5">
                        <label className="text-text-secondary font-mono text-[11px] uppercase tracking-wider">
                          Password <span className="text-risk-critical">*</span>
                        </label>
                        <span className={`font-mono text-[10px] ${strengthLabel.color}`}>
                          {strengthLabel.text}
                        </span>
                      </div>
                      <div className="relative">
                        <Lock className="w-4 h-4 text-text-muted absolute left-3 top-3" />
                        <input
                          type={showPassword ? 'text' : 'password'}
                          value={password}
                          onChange={(e) => setPassword(e.target.value)}
                          onBlur={() => markTouched('password')}
                          required
                          className={`w-full pl-9 pr-10 py-2.5 rounded-lg bg-surface-200 border text-white text-xs font-mono transition-all focus:outline-none focus:ring-1 ${
                            touched.password && !isPasswordValid
                              ? 'border-risk-critical/60 focus:border-risk-critical focus:ring-risk-critical'
                              : 'border-surface-border focus:border-brand-primary focus:ring-brand-primary'
                          }`}
                          placeholder="••••••••••••"
                          id="signup-password"
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

                      {/* Password criteria chips */}
                      <div className="flex flex-wrap gap-2 text-[10px] font-mono pt-1.5 text-text-muted">
                        <span className={`flex items-center gap-1 ${passwordCriteria.minLength ? 'text-risk-low' : ''}`}>
                          {passwordCriteria.minLength ? <Check className="w-3 h-3" /> : <span className="w-3 h-3 text-center">&bull;</span>}
                          6+ chars
                        </span>
                        <span className={`flex items-center gap-1 ${passwordCriteria.hasUpper ? 'text-risk-low' : ''}`}>
                          {passwordCriteria.hasUpper ? <Check className="w-3 h-3" /> : <span className="w-3 h-3 text-center">&bull;</span>}
                          Uppercase
                        </span>
                        <span className={`flex items-center gap-1 ${passwordCriteria.hasNumber ? 'text-risk-low' : ''}`}>
                          {passwordCriteria.hasNumber ? <Check className="w-3 h-3" /> : <span className="w-3 h-3 text-center">&bull;</span>}
                          Number
                        </span>
                      </div>
                    </div>

                    {/* Confirm Password */}
                    <div>
                      <div className="flex justify-between items-center mb-1.5">
                        <label className="text-text-secondary font-mono text-[11px] uppercase tracking-wider">
                          Confirm Password <span className="text-risk-critical">*</span>
                        </label>
                        {touched.confirmPassword && confirmPassword && (
                          doPasswordsMatch ? (
                            <span className="font-mono text-[10px] text-risk-low flex items-center gap-0.5">
                              <Check className="w-3 h-3" /> Matches
                            </span>
                          ) : (
                            <span className="font-mono text-[10px] text-risk-critical flex items-center gap-0.5">
                              <X className="w-3 h-3" /> Does not match
                            </span>
                          )
                        )}
                      </div>
                      <div className="relative">
                        <Lock className="w-4 h-4 text-text-muted absolute left-3 top-3" />
                        <input
                          type={showConfirmPassword ? 'text' : 'password'}
                          value={confirmPassword}
                          onChange={(e) => setConfirmPassword(e.target.value)}
                          onBlur={() => markTouched('confirmPassword')}
                          required
                          className={`w-full pl-9 pr-10 py-2.5 rounded-lg bg-surface-200 border text-white text-xs font-mono transition-all focus:outline-none focus:ring-1 ${
                            touched.confirmPassword && confirmPassword && !doPasswordsMatch
                              ? 'border-risk-critical/60 focus:border-risk-critical focus:ring-risk-critical'
                              : 'border-surface-border focus:border-brand-primary focus:ring-brand-primary'
                          }`}
                          placeholder="••••••••••••"
                          id="signup-confirm-password"
                        />
                        <button
                          type="button"
                          onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                          className="absolute right-3 top-2.5 text-text-muted hover:text-white transition-colors"
                          aria-label="Toggle confirm password visibility"
                        >
                          {showConfirmPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                        </button>
                      </div>
                    </div>

                    {/* Submit Button */}
                    <button
                      type="submit"
                      disabled={loading}
                      id="signup-submit-btn"
                      className="w-full py-3.5 rounded-xl bg-brand-primary hover:bg-brand-light disabled:opacity-50 text-white font-mono text-xs font-semibold tracking-wider flex items-center justify-center gap-2 shadow-cyber transition-all hover:scale-[1.01] active:scale-[0.99] mt-4 cursor-pointer"
                    >
                      {loading ? (
                        <>
                          <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                          <span>CONNECTING TO DATABASE...</span>
                        </>
                      ) : (
                        <>
                          <Shield className="w-4 h-4" />
                          <span>SIGN UP</span>
                        </>
                      )}
                    </button>
                  </form>

                  {/* Sign In Link */}
                  <div className="pt-5 mt-5 border-t border-surface-border text-center font-mono text-xs text-text-muted">
                    Already have an account?{' '}
                    <Link to="/login" className="text-brand-light hover:underline font-semibold">
                      Sign in
                    </Link>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
