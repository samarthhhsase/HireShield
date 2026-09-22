import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Shield, Menu, X, ArrowRight, Chrome } from 'lucide-react';

export default function Navbar() {
  const [scrolled, setScrolled] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [showExtensionModal, setShowExtensionModal] = useState(false);
  const [extensionAdded, setExtensionAdded] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 20);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const scrollToSection = (id) => {
    setMobileMenuOpen(false);
    const element = document.getElementById(id);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' });
    } else {
      navigate(`/#${id}`);
    }
  };

  const handleConfirmAddExtension = () => {
    setExtensionAdded(true);
    const link = document.createElement('a');
    link.href = '/hireshield-extension.zip';
    link.download = 'hireshield-extension.zip';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    setTimeout(() => {
      setShowExtensionModal(false);
      setExtensionAdded(false);
    }, 1800);
  };

  return (
    <header 
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
        scrolled 
          ? 'bg-background/90 backdrop-blur-md border-b border-surface-border py-3 shadow-xl' 
          : 'bg-transparent py-5'
      }`}
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex items-center justify-between">
        {/* Left: Brand Identity */}
        <Link to="/" className="flex items-center gap-2.5 group select-none">
          <div className="w-9 h-9 rounded-lg bg-surface-100 border border-brand-primary/40 flex items-center justify-center text-brand-primary shadow-cyber group-hover:border-brand-primary transition-all">
            <Shield className="w-5 h-5 fill-brand-primary/20 stroke-brand-primary group-hover:scale-105 transition-transform" />
          </div>
          <div className="flex flex-col">
            <div className="flex items-center gap-1.5">
              <span className="font-sans font-extrabold text-base tracking-tight text-white group-hover:text-brand-light transition-colors">
                HireShield
              </span>
              <span className="px-1.5 py-0.2 text-[9px] font-mono font-bold tracking-wider text-brand-light bg-brand-primary/15 border border-brand-primary/30 rounded">
                INTELLIGENCE
              </span>
            </div>
          </div>
        </Link>

        {/* Center: Desktop Navigation Links */}
        <nav className="hidden lg:flex items-center gap-8 text-xs font-mono tracking-wider text-text-secondary">
          <button 
            onClick={() => scrollToSection('how-it-works')}
            className="hover:text-white transition-colors uppercase tracking-widest text-[11px]"
          >
            How It Works
          </button>
          <button 
            onClick={() => scrollToSection('risk-intelligence')}
            className="hover:text-white transition-colors uppercase tracking-widest text-[11px]"
          >
            Risk Intelligence
          </button>
          <button 
            onClick={() => scrollToSection('ai-nlp')}
            className="hover:text-white transition-colors uppercase tracking-widest text-[11px]"
          >
            AI / NLP
          </button>
          <button 
            onClick={() => scrollToSection('explainable-risk')}
            className="hover:text-white transition-colors uppercase tracking-widest text-[11px]"
          >
            Explainable Risk
          </button>
          <button 
            onClick={() => scrollToSection('install-extension')}
            className="hover:text-white transition-colors uppercase tracking-widest text-[11px] text-brand-light font-semibold"
          >
            Install Guide
          </button>
        </nav>

        {/* Right: Actions */}
        <div className="hidden sm:flex items-center gap-3">
          {/* Enhanced Chrome Extension Pill UI */}
          <button 
            type="button"
            onClick={() => setShowExtensionModal(true)}
            className="group flex items-center gap-2 px-3 py-1.5 rounded-full bg-surface-100/90 hover:bg-surface-200 border border-brand-primary/30 hover:border-brand-primary text-text-secondary hover:text-white text-xs font-mono transition-all duration-200 shadow-sm hover:shadow-cyber cursor-pointer"
            title="Get HireShield Chrome Extension"
          >
            <div className="w-4 h-4 rounded-full bg-brand-primary/20 flex items-center justify-center">
              <Chrome className="w-3 h-3 text-brand-light group-hover:scale-110 transition-transform" />
            </div>
            <span className="text-[11px] font-medium tracking-wide">Chrome Extension</span>
            <span className="px-1.5 py-0.2 text-[8px] font-bold bg-brand-primary/20 text-brand-light border border-brand-primary/40 rounded-full">
              FREE
            </span>
          </button>

          <Link
            to="/login"
            className="text-xs font-mono font-medium text-text-secondary hover:text-white transition-colors px-2.5 py-1.5"
          >
            Sign In
          </Link>

          <Link
            to="/risk-analysis"
            className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-brand-primary hover:bg-brand-light text-white text-xs font-mono font-semibold tracking-wide shadow-cyber transition-all hover:scale-[1.02] active:scale-[0.98]"
          >
            <span>Analyze a Job</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        {/* Mobile Hamburger Toggle */}
        <div className="flex sm:hidden items-center gap-2">
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="p-2 rounded-lg text-text-secondary hover:text-white hover:bg-surface-100 transition-colors"
            aria-label="Toggle navigation menu"
          >
            {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>
        </div>
      </div>

      {/* Mobile Drawer Menu */}
      {mobileMenuOpen && (
        <div className="sm:hidden bg-surface-200/98 border-b border-surface-border px-4 pt-3 pb-6 space-y-4 font-mono text-xs">
          {/* Elevated Extension Option for Mobile */}
          <button 
            type="button"
            onClick={() => { setMobileMenuOpen(false); setShowExtensionModal(true); }}
            className="w-full flex items-center justify-between p-3 rounded-xl bg-surface-100 border border-brand-primary/30 text-white font-mono text-xs hover:border-brand-primary transition-all"
          >
            <div className="flex items-center gap-2.5">
              <div className="w-6 h-6 rounded-full bg-brand-primary/20 flex items-center justify-center">
                <Chrome className="w-3.5 h-3.5 text-brand-light" />
              </div>
              <span className="font-semibold">Chrome Extension</span>
            </div>
            <span className="px-2 py-0.5 text-[9px] font-bold bg-brand-primary/20 text-brand-light border border-brand-primary/40 rounded-full">
              INSTALL
            </span>
          </button>

          <div className="flex flex-col space-y-3 pt-2">
            <button 
              onClick={() => scrollToSection('how-it-works')}
              className="text-left py-2 text-text-secondary hover:text-white border-b border-surface-border/50"
            >
              How It Works
            </button>
            <button 
              onClick={() => scrollToSection('risk-intelligence')}
              className="text-left py-2 text-text-secondary hover:text-white border-b border-surface-border/50"
            >
              Risk Intelligence
            </button>
            <button 
              onClick={() => scrollToSection('ai-nlp')}
              className="text-left py-2 text-text-secondary hover:text-white border-b border-surface-border/50"
            >
              AI / NLP
            </button>
            <button 
              onClick={() => scrollToSection('explainable-risk')}
              className="text-left py-2 text-text-secondary hover:text-white border-b border-surface-border/50"
            >
              Explainable Risk
            </button>
            <button 
              onClick={() => scrollToSection('install-extension')}
              className="text-left py-2 text-brand-light font-semibold hover:text-white"
            >
              Install Guide
            </button>
          </div>

          <div className="pt-2 flex flex-col gap-2.5">
            <Link
              to="/login"
              onClick={() => setMobileMenuOpen(false)}
              className="w-full text-center py-2.5 rounded border border-surface-border text-text-primary hover:bg-surface-100"
            >
              Sign In
            </Link>
            <Link
              to="/risk-analysis"
              onClick={() => setMobileMenuOpen(false)}
              className="w-full text-center py-2.5 rounded bg-brand-primary text-white font-bold"
            >
              Analyze a Job
            </Link>
          </div>
        </div>
      )}

      {/* Extension Native Browser Prompt Dialog */}
      {showExtensionModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-background/80 backdrop-blur-sm">
          <div className="bg-[#182234] border border-[#2e3d57] rounded-xl max-w-sm w-full p-5 shadow-2xl relative font-sans text-sm text-white">
            <div className="flex items-start gap-3.5 mb-4">
              <div className="w-10 h-10 rounded-lg bg-blue-500/20 border border-blue-400/40 flex items-center justify-center text-xl shrink-0">
                🛡️
              </div>
              <div>
                <h3 className="font-bold text-base text-white leading-tight">
                  Add "HireShield"?
                </h3>
                <p className="text-xs text-slate-400 mt-0.5">
                  Recruitment Threat Intelligence &amp; Scam Detection
                </p>
              </div>
            </div>

            <div className="border-t border-b border-slate-700/60 py-3 mb-4 space-y-2 text-xs text-slate-300">
              <div className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
                It can:
              </div>
              <div className="flex items-start gap-2">
                <span className="text-blue-400 font-bold">•</span>
                <span>Read visible recruitment postings across job websites</span>
              </div>
              <div className="flex items-start gap-2">
                <span className="text-blue-400 font-bold">•</span>
                <span>Detect upfront fee demands, scam signals &amp; credential fraud</span>
              </div>
              <div className="flex items-start gap-2">
                <span className="text-blue-400 font-bold">•</span>
                <span>Verify corporate domain security and HTTPS infrastructure</span>
              </div>
            </div>

            {extensionAdded ? (
              <div className="p-3 bg-emerald-500/15 border border-emerald-500/30 rounded-lg text-emerald-400 text-xs font-semibold flex items-center gap-2 mb-3">
                <span>✅</span>
                <span>Adding HireShield to your browser...</span>
              </div>
            ) : null}

            <div className="flex items-center justify-end gap-2.5">
              <button
                type="button"
                onClick={() => setShowExtensionModal(false)}
                className="px-4 py-2 rounded-lg bg-slate-700/80 hover:bg-slate-700 text-slate-300 text-xs font-medium transition-colors"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={handleConfirmAddExtension}
                className="px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-xs font-bold shadow-lg shadow-blue-600/30 transition-all"
              >
                Add extension
              </button>
            </div>

            <div className="pt-3 border-t border-slate-700/60 mt-3 text-center">
              <button
                type="button"
                onClick={() => {
                  setShowExtensionModal(false);
                  scrollToSection('install-extension');
                }}
                className="text-[11px] text-blue-400 hover:text-blue-300 underline font-mono cursor-pointer"
              >
                Need help installing? View Step-by-Step Guide →
              </button>
            </div>
          </div>
        </div>
      )}
    </header>
  );
}
