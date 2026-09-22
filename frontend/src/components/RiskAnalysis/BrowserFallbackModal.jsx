import React, { useState, useEffect } from 'react';
import { 
  ShieldAlert, 
  X, 
  Send, 
  RefreshCw, 
  FileText, 
  Sparkles, 
  AlertTriangle,
  CheckCircle2,
  Cpu,
  Shield
} from 'lucide-react';

export default function BrowserFallbackModal({
  isOpen,
  onClose,
  targetUrl = '',
  initialTitle = '',
  initialCompany = '',
  onSubmit,
}) {
  const [url, setUrl] = useState(targetUrl);
  const [title, setTitle] = useState(initialTitle);
  const [company, setCompany] = useState(initialCompany);
  const [content, setContent] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [validationError, setValidationError] = useState(null);
  const [loadingStep, setLoadingStep] = useState(0);

  // Sync state when props change
  useEffect(() => {
    setUrl(targetUrl);
    setTitle(initialTitle);
    setCompany(initialCompany);
  }, [targetUrl, initialTitle, initialCompany]);

  // Telemetry stages for loading state (Requirement 16)
  const loadingSteps = [
    'Receiving browser content...',
    'Normalizing job description...',
    'Running NLP...',
    'Evaluating behavioral signals...',
    'Calculating risk...',
  ];

  useEffect(() => {
    let timer;
    if (isSubmitting) {
      setLoadingStep(0);
      timer = setInterval(() => {
        setLoadingStep((prev) => (prev < loadingSteps.length - 1 ? prev + 1 : prev));
      }, 350);
    }
    return () => {
      if (timer) clearInterval(timer);
    };
  }, [isSubmitting]);

  if (!isOpen) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setValidationError(null);

    const trimmedContent = content.trim();
    if (!trimmedContent) {
      setValidationError('Job description must not be empty. Please paste the visible text from the job posting.');
      return;
    }

    if (trimmedContent.length < 15) {
      setValidationError('The submitted job description is too brief to evaluate. Please provide the full visible text.');
      return;
    }

    if (trimmedContent.length > 100000) {
      setValidationError('Submitted content exceeds the maximum allowable limit of 100,000 characters.');
      return;
    }

    setIsSubmitting(true);
    try {
      await onSubmit({
        url: url.trim(),
        title: title.trim(),
        company: company.trim(),
        content: trimmedContent,
      });
      // Reset and close on success
      setContent('');
      setValidationError(null);
      onClose();
    } catch (err) {
      console.error('Fallback submission error:', err);
      setValidationError(
        err.message || 
        err.detail || 
        'HireShield could not analyze the submitted content. Please verify that the job description was pasted correctly and try again.'
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleFillCleanSample = () => {
    setTitle('Integration Engineering Software Engineer');
    setCompany('Apple Inc.');
    setContent(
      "Apple is seeking an Integration Engineering Software Engineer to join our CoreOS team. " +
      "You will develop automated testing frameworks, CI/CD infrastructure, and regression verification " +
      "across macOS and iOS architectures. Requires BS/MS in Computer Science, 4+ years of C++, Python, " +
      "and distributed systems experience. Excellent compensation, comprehensive health benefits, and 401(k)."
    );
    setValidationError(null);
  };

  const handleFillSuspiciousSample = () => {
    setTitle('URGENT HIRING: Data Entry Operator');
    setCompany('Fast Cash Ventures');
    setContent(
      "URGENT HIRING: Immediate joining without interview! 100% guaranteed job placement. " +
      "Earn ₹50,000 monthly with no experience required. Mandatory registration fee of ₹1,500 " +
      "required as refundable security deposit before onboarding. Please send your Aadhaar card, " +
      "PAN card, and bank account details on WhatsApp to +91-9876543210. Limited slots available, " +
      "apply within 24 hours to secure placement!!!!!"
    );
    setValidationError(null);
  };

  return (
    <div className="fixed inset-0 bg-black/85 backdrop-blur-md z-50 flex items-center justify-center p-4 overflow-y-auto animate-fadeIn font-sans">
      <div className="relative max-w-2xl w-full bg-surface-100 border border-brand-primary/40 rounded-2xl shadow-2xl overflow-hidden glass-panel">
        {/* Header Bar */}
        <div className="px-6 py-5 bg-surface-200 border-b border-surface-border flex items-start justify-between gap-4">
          <div className="flex items-start gap-3">
            <div className="p-2.5 rounded-xl bg-brand-primary/10 text-brand-light border border-brand-primary/30 mt-0.5">
              <FileText className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-mono text-xs font-bold text-brand-light uppercase tracking-wider">
                  BROWSER CONTENT FALLBACK
                </span>
                <span className="px-2 py-0.5 rounded-full text-[10px] font-mono bg-risk-low/10 text-risk-low border border-risk-low/30">
                  LOCAL RISK ENGINE
                </span>
              </div>
              <h3 className="text-base font-bold text-white mt-1">
                Analyze Visible Job Page Content
              </h3>
              <p className="text-xs text-text-muted mt-0.5 leading-relaxed">
                The target website blocked automated access. Paste the visible job description below and HireShield will analyze the content locally through the risk engine.
              </p>
            </div>
          </div>

          <button
            type="button"
            onClick={onClose}
            disabled={isSubmitting}
            className="p-1.5 rounded-lg bg-surface-300 hover:bg-surface-400 text-text-muted hover:text-white transition-colors cursor-pointer disabled:opacity-50"
            title="Close Fallback Panel"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Body */}
        {isSubmitting ? (
          /* Loading State (Requirement 16) */
          <div className="p-10 space-y-6 text-center font-mono">
            <div className="w-16 h-16 rounded-2xl bg-brand-primary/10 border border-brand-primary/40 flex items-center justify-center text-brand-light mx-auto shadow-cyber animate-pulse">
              <Cpu className="w-8 h-8 animate-spin" />
            </div>

            <div className="space-y-1.5">
              <div className="text-xs text-brand-light tracking-widest uppercase font-bold">
                HIRE SHIELD
              </div>
              <div className="text-lg font-extrabold text-white tracking-tight">
                CONTENT ANALYSIS
              </div>
            </div>

            {/* Step Sequence */}
            <div className="max-w-md mx-auto space-y-2 text-left bg-surface-200/80 p-4 rounded-xl border border-surface-border">
              {loadingSteps.map((step, idx) => (
                <div key={idx} className="flex items-center gap-2.5 text-xs">
                  {idx < loadingStep ? (
                    <CheckCircle2 className="w-4 h-4 text-risk-low flex-shrink-0" />
                  ) : idx === loadingStep ? (
                    <RefreshCw className="w-4 h-4 text-brand-light animate-spin flex-shrink-0" />
                  ) : (
                    <span className="w-4 h-4 rounded-full border border-surface-border inline-block flex-shrink-0" />
                  )}
                  <span className={idx === loadingStep ? 'text-white font-bold' : idx < loadingStep ? 'text-text-muted' : 'text-text-muted/60'}>
                    {step}
                  </span>
                </div>
              ))}
            </div>

            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-bold text-brand-light bg-brand-primary/10 border border-brand-primary/30 uppercase tracking-wider">
              <span>ANALYSIS IN PROGRESS</span>
            </div>
          </div>
        ) : (
          /* Form Body */
          <form onSubmit={handleSubmit} className="p-6 space-y-4">
            {/* Error Notification */}
            {validationError && (
              <div className="p-3.5 rounded-xl bg-risk-critical/10 border border-risk-critical/30 text-xs font-mono text-risk-critical flex items-start gap-2.5">
                <AlertTriangle className="w-4 h-4 mt-0.5 flex-shrink-0" />
                <div className="flex-1 leading-relaxed">
                  <span className="font-bold">CONTENT ANALYSIS NOTICE: </span>
                  <span>{validationError}</span>
                </div>
              </div>
            )}

            {/* Quick Demo Fill Buttons */}
            <div className="flex items-center justify-between gap-2 flex-wrap pb-1 font-mono text-[11px]">
              <span className="text-text-muted">Quick Test Sample Text:</span>
              <div className="flex items-center gap-2">
                <button
                  type="button"
                  onClick={handleFillCleanSample}
                  className="px-2.5 py-1 rounded bg-surface-200 hover:bg-surface-300 text-brand-light border border-surface-border hover:border-brand-primary/40 transition-colors cursor-pointer"
                >
                  Fill Clean Sample (Apple)
                </button>
                <button
                  type="button"
                  onClick={handleFillSuspiciousSample}
                  className="px-2.5 py-1 rounded bg-surface-200 hover:bg-surface-300 text-risk-high border border-surface-border hover:border-risk-high/40 transition-colors cursor-pointer"
                >
                  Fill Suspicious Sample (Fee/Scam)
                </button>
              </div>
            </div>

            {/* URL Field (Pre-filled) */}
            <div>
              <label className="block text-text-secondary font-mono text-[11px] mb-1 uppercase tracking-wider">
                Target URL (Pre-filled from scan)
              </label>
              <input
                type="url"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                placeholder="https://company.com/job-listing"
                className="w-full px-3.5 py-2.5 rounded-lg bg-surface-200 border border-surface-border text-white text-xs font-mono focus:outline-none focus:border-brand-primary"
              />
            </div>

            {/* Two-Column Title & Company */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div>
                <label className="block text-text-secondary font-mono text-[11px] mb-1 uppercase tracking-wider">
                  Job Title <span className="text-text-muted normal-case font-normal">(Optional)</span>
                </label>
                <input
                  type="text"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  placeholder="e.g. Senior Software Engineer"
                  className="w-full px-3.5 py-2 rounded-lg bg-surface-200 border border-surface-border text-white text-xs font-mono focus:outline-none focus:border-brand-primary"
                />
              </div>
              <div>
                <label className="block text-text-secondary font-mono text-[11px] mb-1 uppercase tracking-wider">
                  Company <span className="text-text-muted normal-case font-normal">(Optional)</span>
                </label>
                <input
                  type="text"
                  value={company}
                  onChange={(e) => setCompany(e.target.value)}
                  placeholder="e.g. Acme Corp"
                  className="w-full px-3.5 py-2 rounded-lg bg-surface-200 border border-surface-border text-white text-xs font-mono focus:outline-none focus:border-brand-primary"
                />
              </div>
            </div>

            {/* Job Description Textarea */}
            <div>
              <div className="flex items-center justify-between mb-1">
                <label className="block text-text-secondary font-mono text-[11px] uppercase tracking-wider">
                  Job Description *
                </label>
                <span className="font-mono text-[10px] text-text-muted">
                  {content.length} characters &bull; {content.trim() ? content.trim().split(/\s+/).length : 0} words
                </span>
              </div>
              <textarea
                value={content}
                onChange={(e) => setContent(e.target.value)}
                required
                rows={7}
                placeholder="Paste visible job description here..."
                className="w-full p-3.5 rounded-lg bg-surface-200 border border-surface-border text-white text-xs font-mono focus:outline-none focus:border-brand-primary leading-relaxed placeholder:text-text-muted/60"
              />
              <p className="text-[11px] text-text-muted mt-1 font-sans">
                Paste readable text from your browser. Do not require raw HTML tags.
              </p>
            </div>

            {/* Action Bar */}
            <div className="flex items-center justify-end gap-3 pt-3 border-t border-surface-border">
              <button
                type="button"
                onClick={onClose}
                className="px-4 py-2.5 rounded-lg bg-surface-200 hover:bg-surface-300 text-text-muted hover:text-white font-mono text-xs transition-colors cursor-pointer"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={!content.trim()}
                className="px-6 py-2.5 rounded-lg bg-brand-primary hover:bg-brand-light disabled:opacity-50 text-white font-mono text-xs font-bold tracking-wider flex items-center gap-2 shadow-cyber transition-all cursor-pointer"
              >
                <Send className="w-3.5 h-3.5" />
                <span>ANALYZE CONTENT</span>
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
}
