import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { 
  Shield, 
  ArrowRight, 
  CheckCircle2, 
  AlertTriangle, 
  AlertOctagon, 
  FileSearch, 
  Cpu, 
  Lock, 
  Globe, 
  Database,
  Layers,
  Search,
  ExternalLink,
  ChevronRight,
  Terminal as TerminalIcon,
  ShieldCheck,
  Activity
} from 'lucide-react';
import ShieldHero from '../components/ShieldAnimation/ShieldHero';
import RadialScoreGauge from '../components/RiskScore/RadialScoreGauge';
import AITerminal from '../components/RiskAnalysis/AITerminal';
import InstallExtensionSection from '../components/InstallExtension/InstallExtensionSection';

export default function Landing() {
  const [demoTab, setDemoTab] = useState('low'); // 'low' | 'critical'

  return (
    <div className="space-y-28 sm:space-y-36 pb-20">
      {/* 1. HERO SECTION */}
      <section className="relative pt-32 sm:pt-40 lg:pt-48 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Subtle decorative glow elements */}
        <div className="absolute top-20 left-1/2 -translate-x-1/2 w-[600px] h-[350px] bg-brand-primary/10 blur-[130px] rounded-full pointer-events-none" />

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 lg:gap-8 items-center">
          {/* Left Column: Headline, Description & CTAs */}
          <div className="lg:col-span-7 space-y-6 text-left">
            {/* Status Telemetry Strip */}
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-surface-100/90 border border-surface-border text-[11px] font-mono">
              <span className="w-2 h-2 rounded-full bg-brand-light animate-pulse" />
              <span className="text-brand-light font-semibold">AI ENGINE ● ONLINE</span>
              <span className="text-text-muted">|</span>
              <span className="text-text-secondary">RISK ENGINE ● ACTIVE</span>
            </div>

            {/* Oversized Headline */}
            <h1 className="text-4xl sm:text-6xl lg:text-6xl font-extrabold tracking-tight text-white leading-[1.08]">
              Hire with confidence.{' '}
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-brand-light via-blue-400 to-indigo-300">
                Detect risk before you hire.
              </span>
            </h1>

            {/* Supporting Text */}
            <p className="text-base sm:text-lg text-text-secondary leading-relaxed max-w-2xl font-sans">
              HireShield analyzes job postings, recruitment domains, AI/NLP signals and technical evidence to identify potential hiring scams and provide explainable risk intelligence.
            </p>

            {/* CTAs */}
            <div className="pt-2 flex flex-col sm:flex-row items-stretch sm:items-center gap-4">
              <Link
                to="/risk-analysis"
                className="inline-flex items-center justify-center gap-2.5 px-6 py-3.5 rounded-lg bg-brand-primary hover:bg-brand-light text-white font-mono text-sm font-semibold tracking-wide shadow-cyber-lg transition-all hover:scale-[1.02] active:scale-[0.98]"
              >
                <span>Analyze a Job</span>
                <ArrowRight className="w-4 h-4" />
              </Link>

              <a
                href="#how-it-works"
                className="inline-flex items-center justify-center gap-2 px-6 py-3.5 rounded-lg bg-surface-100 hover:bg-surface-200 text-text-primary border border-surface-border font-mono text-sm transition-all hover:border-brand-primary/40"
              >
                <span>See How It Works</span>
                <ChevronRight className="w-4 h-4 text-text-muted" />
              </a>
            </div>

            {/* Technical Sub-telemetry */}
            <div className="pt-6 border-t border-surface-border/60 grid grid-cols-3 gap-4 font-mono text-xs">
              <div>
                <div className="text-text-muted text-[10px] uppercase">ANALYSIS ENGINE</div>
                <div className="text-white font-bold mt-0.5">FASTAPI v1.0</div>
              </div>
              <div>
                <div className="text-text-muted text-[10px] uppercase">RISK COMPUTATION</div>
                <div className="text-risk-low font-bold mt-0.5">BEHAVIOR-FIRST</div>
              </div>
              <div>
                <div className="text-text-muted text-[10px] uppercase">SIGNAL DETECTION</div>
                <div className="text-brand-light font-bold mt-0.5">4-TIER MATRIX</div>
              </div>
            </div>
          </div>

          {/* Right Column: Hero Shield Visualization */}
          <div className="lg:col-span-5 flex items-center justify-center">
            <ShieldHero score={27} level="LOW RISK" />
          </div>
        </div>
      </section>

      {/* 2. HOW WE FIND FAKE JOBS / DETECTION MATRIX */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-3xl mx-auto mb-16 space-y-3">
          <div className="inline-flex items-center gap-2 font-mono text-xs text-brand-light uppercase tracking-widest bg-brand-primary/10 px-3 py-1 rounded border border-brand-primary/20">
            DETECTION INTELLIGENCE // HOW WE CATCH FAKE JOBS
          </div>
          <h2 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight">
            How HireShield Identifies Fake Jobs & Scams
          </h2>
          <p className="text-sm sm:text-base text-text-muted leading-relaxed font-sans">
            Scammers disguise fraudulent job offers behind spoofed brands, artificial urgency, and advance fee traps. HireShield cross-examines listings across 4 deep forensic intelligence vectors before you apply or respond.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5 font-sans">
          {/* Card 01: Payment Fraud */}
          <div className="p-6 rounded-lg bg-surface-100 border border-surface-border glass-panel-hover space-y-4">
            <div className="font-mono text-xs text-brand-light font-bold tracking-wider">01 // PAYMENT FRAUD</div>
            <h3 className="text-base font-bold text-white tracking-tight">
              ADVANCE FEE & DEPOSIT TRAPS
            </h3>
            <p className="text-xs text-text-muted leading-relaxed">
              Instantly detects demands for "mandatory onboarding charges," equipment courier fees, training deposits, or cryptocurrency transfers before an interview.
            </p>
          </div>

          {/* Card 02: Impersonation */}
          <div className="p-6 rounded-lg bg-surface-100 border border-surface-border glass-panel-hover space-y-4">
            <div className="font-mono text-xs text-brand-light font-bold tracking-wider">02 // IMPERSONATION</div>
            <h3 className="text-base font-bold text-white tracking-tight">
              BRAND & DOMAIN SPOOFING
            </h3>
            <p className="text-xs text-text-muted leading-relaxed">
              Uncovers lookalike typosquatting domains, newly registered scam portals, unverified TLDs, and fake career sites masquerading as legitimate enterprise employers.
            </p>
          </div>

          {/* Card 03: Communication */}
          <div className="p-6 rounded-lg bg-surface-100 border border-surface-border glass-panel-hover space-y-4">
            <div className="font-mono text-xs text-brand-light font-bold tracking-wider">03 // COMMUNICATION</div>
            <h3 className="text-base font-bold text-white tracking-tight">
              OFF-PLATFORM & RECRUITER CHANNELS
            </h3>
            <p className="text-xs text-text-muted leading-relaxed">
              Flags suspicious recruiters routing candidates to Telegram, WhatsApp, or Signal for "immediate text interviews," as well as free @gmail or disposable burner addresses.
            </p>
          </div>

          {/* Card 04: Harvesting */}
          <div className="p-6 rounded-lg bg-surface-100 border border-surface-border glass-panel-hover space-y-4">
            <div className="font-mono text-xs text-brand-light font-bold tracking-wider">04 // HARVESTING</div>
            <h3 className="text-base font-bold text-white tracking-tight">
              CREDENTIAL & IDENTITY THEFT
            </h3>
            <p className="text-xs text-text-muted leading-relaxed">
              Catches premature solicitations for government IDs (Aadhaar, PAN, SSN), bank credentials, and OTPs disguised as "hiring documentation."
            </p>
          </div>
        </div>
      </section>

      {/* 3. HOW HIRESHIELD WORKS */}
      <section id="how-it-works" className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-3xl mx-auto mb-16 space-y-3">
          <div className="inline-flex items-center gap-2 font-mono text-xs text-brand-light uppercase tracking-widest bg-brand-primary/10 px-3 py-1 rounded border border-brand-primary/20">
            Pipeline Architecture // 4-Stage Engine
          </div>
          <h2 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight">
            How HireShield Works
          </h2>
          <p className="text-sm sm:text-base text-text-muted leading-relaxed font-sans">
            From suspicious job links to explainable fraud intelligence in sub-second inference.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 relative">
          {/* Step 01 */}
          <div className="p-6 rounded-lg bg-surface-100 border border-surface-border relative group glass-panel-hover">
            <div className="flex items-center justify-between mb-4">
              <span className="font-mono text-xs font-bold text-brand-light px-2 py-0.5 rounded bg-surface-200 border border-surface-border">
                01 — COLLECT
              </span>
              <FileSearch className="w-5 h-5 text-brand-primary" />
            </div>
            <h3 className="text-sm font-bold text-white mb-2">Data Ingestion</h3>
            <p className="text-xs text-text-muted leading-relaxed">
              Job postings, recruiter emails, or career page URLs enter the engine via browser extension or direct input.
            </p>
            <a
              href="#install-extension"
              className="inline-flex items-center gap-1 mt-2.5 font-mono text-[11px] text-brand-light hover:underline"
            >
              <span>How to Install Extension</span>
              <ArrowRight className="w-3 h-3" />
            </a>
          </div>

          {/* Step 02 */}
          <div className="p-6 rounded-lg bg-surface-100 border border-surface-border relative group glass-panel-hover">
            <div className="flex items-center justify-between mb-4">
              <span className="font-mono text-xs font-bold text-brand-light px-2 py-0.5 rounded bg-surface-200 border border-surface-border">
                02 — ANALYZE
              </span>
              <Cpu className="w-5 h-5 text-brand-primary" />
            </div>
            <h3 className="text-sm font-bold text-white mb-2">Multimodal AI/NLP</h3>
            <p className="text-xs text-text-muted leading-relaxed">
              AI/NLP and technical analysis process available signals: lexical urgency, payment solicitations, DNS, and SSL.
            </p>
          </div>

          {/* Step 03 */}
          <div className="p-6 rounded-lg bg-surface-100 border border-surface-border relative group glass-panel-hover">
            <div className="flex items-center justify-between mb-4">
              <span className="font-mono text-xs font-bold text-brand-light px-2 py-0.5 rounded bg-surface-200 border border-surface-border">
                03 — SCORE
              </span>
              <Activity className="w-5 h-5 text-brand-primary" />
            </div>
            <h3 className="text-sm font-bold text-white mb-2">Risk Engine</h3>
            <p className="text-xs text-text-muted leading-relaxed">
              The risk engine combines supported signals into a weighted risk assessment with critical behavioral overrides.
            </p>
          </div>

          {/* Step 04 */}
          <div className="p-6 rounded-lg bg-surface-100 border border-surface-border relative group glass-panel-hover">
            <div className="flex items-center justify-between mb-4">
              <span className="font-mono text-xs font-bold text-brand-light px-2 py-0.5 rounded bg-surface-200 border border-surface-border">
                04 — EXPLAIN
              </span>
              <ShieldCheck className="w-5 h-5 text-brand-primary" />
            </div>
            <h3 className="text-sm font-bold text-white mb-2">Explainable Dossier</h3>
            <p className="text-xs text-text-muted leading-relaxed">
              The platform shows the exact factors, extracted text evidence, and technical signals contributing to the result.
            </p>
          </div>
        </div>
      </section>

      {/* 4. RISK INTELLIGENCE SECTION */}
      <section id="risk-intelligence" className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="rounded-2xl bg-surface-200/90 border border-surface-border p-6 sm:p-10 relative overflow-hidden shadow-2xl">
          {/* Header */}
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-8 border-b border-surface-border/80">
            <div>
              <div className="font-mono text-xs text-brand-light uppercase tracking-wider mb-1">
                Risk Intelligence // Diagnostic View
              </div>
              <h2 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
                See the threat behind the job offer.
              </h2>
            </div>

            {/* Toggle demo score illustration */}
            <div className="flex items-center gap-2 p-1 rounded-lg bg-surface-100 border border-surface-border font-mono text-xs">
              <button
                onClick={() => setDemoTab('low')}
                className={`px-3 py-1.5 rounded transition-all ${
                  demoTab === 'low'
                    ? 'bg-brand-primary text-white font-bold'
                    : 'text-text-muted hover:text-white'
                }`}
              >
                Verified Clean (24)
              </button>
              <button
                onClick={() => setDemoTab('critical')}
                className={`px-3 py-1.5 rounded transition-all ${
                  demoTab === 'critical'
                    ? 'bg-risk-critical text-white font-bold'
                    : 'text-text-muted hover:text-white'
                }`}
              >
                High Risk Scam (85)
              </button>
            </div>
          </div>

          {/* Sample Data Disclosure */}
          <div className="py-3 px-4 rounded bg-surface-100/80 border border-surface-border/80 my-6 font-mono text-[11px] text-text-muted flex items-center justify-between">
            <span>[SAMPLE DATA ILLUSTRATION FOR LANDING PAGE PREVIEW]</span>
            <span className="text-brand-light">AUDIT_REF: HS-2026-00421 // JOB_POSTING</span>
          </div>

          {/* Conceptual Job Scam Analysis Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">
            {/* Left Gauge */}
            <div className="lg:col-span-4 flex flex-col items-center justify-center p-6 rounded-xl bg-surface-100 border border-surface-border">
              <RadialScoreGauge
                score={demoTab === 'low' ? 24 : 85}
                level={demoTab === 'low' ? 'LOW' : 'CRITICAL'}
                size={190}
              />
              <div className="mt-4 text-center font-mono text-xs text-text-muted">
                Confidence Level: <span className="text-white font-bold">96.4%</span>
              </div>
            </div>

            {/* Right Signal Breakdown */}
            <div className="lg:col-span-8 space-y-4">
              <div className="text-xs font-mono font-semibold uppercase tracking-wider text-text-secondary">
                Signal Breakdown // Diagnostic Weights
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 font-mono text-xs">
                <div className="p-3.5 rounded-lg bg-surface-100 border border-surface-border">
                  <div className="flex justify-between text-text-secondary mb-1">
                    <span>Domain & Brand Authenticity</span>
                    <span className="font-bold text-white">{demoTab === 'low' ? '18%' : '78%'}</span>
                  </div>
                  <div className="w-full h-1.5 rounded-full bg-surface-200">
                    <div 
                      className={`h-full rounded-full ${demoTab === 'low' ? 'bg-risk-low' : 'bg-risk-critical'}`}
                      style={{ width: demoTab === 'low' ? '18%' : '78%' }}
                    />
                  </div>
                </div>

                <div className="p-3.5 rounded-lg bg-surface-100 border border-surface-border">
                  <div className="flex justify-between text-text-secondary mb-1">
                    <span>NLP Urgency Signals</span>
                    <span className="font-bold text-white">{demoTab === 'low' ? '12%' : '85%'}</span>
                  </div>
                  <div className="w-full h-1.5 rounded-full bg-surface-200">
                    <div 
                      className={`h-full rounded-full ${demoTab === 'low' ? 'bg-risk-low' : 'bg-risk-critical'}`}
                      style={{ width: demoTab === 'low' ? '12%' : '85%' }}
                    />
                  </div>
                </div>

                <div className="p-3.5 rounded-lg bg-surface-100 border border-surface-border">
                  <div className="flex justify-between text-text-secondary mb-1">
                    <span>Technical Signals (SSL/DNS)</span>
                    <span className="font-bold text-white">{demoTab === 'low' ? '7%' : '65%'}</span>
                  </div>
                  <div className="w-full h-1.5 rounded-full bg-surface-200">
                    <div 
                      className={`h-full rounded-full ${demoTab === 'low' ? 'bg-risk-low' : 'bg-risk-critical'}`}
                      style={{ width: demoTab === 'low' ? '7%' : '65%' }}
                    />
                  </div>
                </div>

                <div className="p-3.5 rounded-lg bg-surface-100 border border-surface-border">
                  <div className="flex justify-between text-text-secondary mb-1">
                    <span>Verification Signals</span>
                    <span className="font-bold text-white">{demoTab === 'low' ? '4%' : '90%'}</span>
                  </div>
                  <div className="w-full h-1.5 rounded-full bg-surface-200">
                    <div 
                      className={`h-full rounded-full ${demoTab === 'low' ? 'bg-risk-low' : 'bg-risk-critical'}`}
                      style={{ width: demoTab === 'low' ? '4%' : '90%' }}
                    />
                  </div>
                </div>
              </div>

              {/* Detected Flags for Critical tab */}
              {demoTab === 'critical' && (
                <div className="p-3.5 rounded-lg bg-risk-critical/10 border border-risk-critical/30 font-mono text-xs text-risk-critical space-y-1">
                  <div className="font-bold flex items-center gap-1.5">
                    <AlertOctagon className="w-4 h-4" /> THREAT DETECTED: Upfront Registration Fee Required
                  </div>
                  <p className="text-[11px] text-text-secondary">
                    Posting explicitly requests ₹2,500 advance deposit and sensitive Aadhaar credentials before interview.
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>
      </section>

      {/* 5. AI / NLP SECTION */}
      <section id="ai-nlp" className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">
          <div className="lg:col-span-5 space-y-5">
            <div className="inline-flex items-center gap-2 font-mono text-xs text-brand-light uppercase tracking-widest bg-brand-primary/10 px-3 py-1 rounded border border-brand-primary/20">
              Heuristic & LLM Scanner // NLP Engine
            </div>
            <h2 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight">
              Deep Linguistic & Behavioral Analysis
            </h2>
            <p className="text-sm sm:text-base text-text-secondary leading-relaxed font-sans">
              HireShield inspects raw textual content for deceptive recruitment patterns: pressure tactics, guaranteed income promises, sensitive banking or government identity requests, and unofficial communication channels.
            </p>

            <ul className="space-y-3 font-mono text-xs text-text-muted">
              <li className="flex items-center gap-2.5">
                <CheckCircle2 className="w-4 h-4 text-brand-light flex-shrink-0" />
                <span>Detection of Aadhaar, PAN, OTP, and banking credential solicitations</span>
              </li>
              <li className="flex items-center gap-2.5">
                <CheckCircle2 className="w-4 h-4 text-brand-light flex-shrink-0" />
                <span>Identification of upfront fee, deposit, or verification charges</span>
              </li>
              <li className="flex items-center gap-2.5">
                <CheckCircle2 className="w-4 h-4 text-brand-light flex-shrink-0" />
                <span>Extraction of informal messaging vectors (WhatsApp, Telegram)</span>
              </li>
            </ul>
          </div>

          <div className="lg:col-span-7">
            <AITerminal 
              scores={{ behavioral: 15, linguistic: 10, structural: 0, technical: 5 }}
              redFlags={[]}
              isLoading={false}
            />
          </div>
        </div>
      </section>

      {/* 6. EXPLAINABLE RISK SECTION */}
      <section id="explainable-risk" className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-3xl mx-auto mb-16 space-y-3">
          <div className="inline-flex items-center gap-2 font-mono text-xs text-brand-light uppercase tracking-widest bg-brand-primary/10 px-3 py-1 rounded border border-brand-primary/20">
            Explainable AI // Transparent Reasoning
          </div>
          <h2 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight">
            Don't just show a score. Show why.
          </h2>
          <p className="text-sm sm:text-base text-text-muted leading-relaxed font-sans">
            Black-box scoring is unacceptable in recruitment risk. HireShield surfaces the exact signals, evidence sentences, and network checks behind every score calculation.
          </p>
        </div>

        <div className="p-8 rounded-2xl bg-surface-100 border border-surface-border glass-panel">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 font-mono text-xs">
            <div className="p-5 rounded-lg bg-surface-200 border border-surface-border space-y-2">
              <div className="text-brand-light font-bold">1. EVIDENCE EXTRACTION</div>
              <p className="text-text-muted text-[11px] leading-relaxed">
                Highlights direct phrases in job descriptions or recruiter messages that triggered fraud and fee traps.
              </p>
            </div>

            <div className="p-5 rounded-lg bg-surface-200 border border-surface-border space-y-2">
              <div className="text-brand-light font-bold">2. MATHEMATICAL AUDIT</div>
              <p className="text-text-muted text-[11px] leading-relaxed">
                Provides the exact weighted linear equation (35% Behavioral + 25% Linguistic + 20% Structural + 20% Technical).
              </p>
            </div>

            <div className="p-5 rounded-lg bg-surface-200 border border-surface-border space-y-2">
              <div className="text-brand-light font-bold">3. CRITICAL OVERRIDES</div>
              <p className="text-text-muted text-[11px] leading-relaxed">
                Identifies dangerous combinations (e.g. sensitive identity demands + advance fees) that force high-risk classifications.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* 7. HOW TO INSTALL HIRESHIELD EXTENSION */}
      <InstallExtensionSection />

      {/* 8. FINAL CTA */}
      <section className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 text-center space-y-6">
        <div className="p-10 sm:p-16 rounded-3xl bg-gradient-to-b from-surface-100 via-surface-200 to-surface-300 border border-surface-border shadow-2xl relative overflow-hidden">
          <div className="absolute inset-0 bg-cyber-grid opacity-30 pointer-events-none" />
          
          <h2 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight relative z-10">
            Ready to make smarter hiring decisions?
          </h2>
          <p className="text-sm sm:text-base text-text-muted max-w-xl mx-auto font-sans relative z-10">
            Scan job postings and verify recruitment targets with HireShield's live risk engine today.
          </p>

          <div className="pt-4 relative z-10">
            <Link
              to="/risk-analysis"
              className="inline-flex items-center gap-2 px-8 py-4 rounded-xl bg-brand-primary hover:bg-brand-light text-white font-mono text-sm font-bold shadow-cyber-lg transition-all hover:scale-105 active:scale-95"
            >
              <span>Analyze a Job Now</span>
              <ArrowRight className="w-4 h-4" />
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}
