import React, { useState, useEffect } from 'react';
import { Terminal, Check, AlertTriangle, ShieldCheck, Cpu, Clock, PauseCircle } from 'lucide-react';

export default function AITerminal({ 
  job = {}, 
  scores = {}, 
  redFlags = [], 
  contentAnalyzed = true,
  fetchStatus = 'FETCH_SUCCESS',
  httpStatus = null,
  contentSource = 'server_fetch',
  pipelineStages = [],
  isLoading = false 
}) {
  const [activeStep, setActiveStep] = useState(0);

  // Dynamic logs based on actual analysis state (Section 6 & 13)
  const isContentBlocked = !contentAnalyzed || fetchStatus === 'FETCH_BLOCKED';
  const isBrowserFallback = contentSource === 'browser_fallback' || fetchStatus === 'BROWSER_CONTENT_RECEIVED';

  const logs = isContentBlocked ? [
    'INIT_MODEL: Loading HireShield Linguistic & Behavioral Scanner...',
    `HTTP_EXTRACT: Page content unavailable — remote server returned ${httpStatus ? `HTTP ${httpStatus}` : 'access restriction'}.`,
    'SENSITIVE_LEXICON: Awaiting browser content — credential patterns pending.',
    'PAYMENT_MONITOR: Awaiting browser content — fee detection paused.',
    'URGENCY_DETECTOR: Awaiting browser content — recruitment pressure scan paused.',
    'SYNTHESIS: Waiting for page content — Layer B execution deferred.',
    'STATUS: Content analysis paused — Submit visible job text via Browser Fallback.',
  ] : isBrowserFallback ? [
    'CONTENT_RECEIVED: Ingested visible recruitment text from browser content fallback.',
    'NORMALIZING_TEXT: Tokenized job description payload and normalized whitespace.',
    'RUNNING_NLP: Scanning credential lexicon, financial demands, and pressure heuristics...',
    'ANALYZING_BEHAVIOR: Evaluating advance fee demands, security deposits, and identity requests...',
    'ANALYZING_LINGUISTICS: Evaluating urgency scarcity, coercive language, and guarantee claims...',
    'ANALYZING_STRUCTURE: Inspecting informal communication vectors (WhatsApp / Telegram)...',
    'CALCULATING_RISK: Synthesizing multi-layer risk score (35% B, 25% L, 20% S, 20% T)...',
    'ANALYSIS_COMPLETE: Browser content risk assessment complete. Threat telemetry ready.',
  ] : [
    'INIT_MODEL: Loading HireShield Linguistic & Behavioral Scanner...',
    'HTTP_EXTRACT: Isolated and tokenized recruitment content payload.',
    'SENSITIVE_LEXICON: Checking Aadhaar, PAN, banking, and credential patterns...',
    'PAYMENT_MONITOR: Evaluating fee, deposit, and upfront cost language...',
    'URGENCY_DETECTOR: Scanning for artificial scarcity and recruitment pressure...',
    'SYNTHESIS: Calculating behavioral weights and evaluating override matrix...',
    'STATUS: Threat analysis complete. Diagnostic findings ready.',
  ];

  useEffect(() => {
    if (isLoading) {
      const interval = setInterval(() => {
        setActiveStep((prev) => (prev < logs.length - 1 ? prev + 1 : prev));
      }, 350);
      return () => clearInterval(interval);
    } else {
      setActiveStep(logs.length - 1);
    }
  }, [isLoading, logs.length, isContentBlocked, isBrowserFallback]);

  const hasSensitiveFlag = redFlags.some((f) => (f.message || '').toLowerCase().includes('sensitive identity'));
  const hasPaymentFlag = redFlags.some((f) => (f.message || '').toLowerCase().includes('payment') || (f.message || '').toLowerCase().includes('fee'));
  const hasUrgencyFlag = redFlags.some((f) => (f.message || '').toLowerCase().includes('urgency'));
  const hasMessagingFlag = redFlags.some((f) => (f.message || '').toLowerCase().includes('messaging') || (f.message || '').toLowerCase().includes('telegram'));

  return (
    <div className="rounded-xl bg-surface-300 border border-surface-border overflow-hidden font-mono text-xs shadow-2xl">
      {/* Terminal Title Bar */}
      <div className="flex items-center justify-between px-4 py-2.5 bg-surface-200 border-b border-surface-border">
        <div className="flex items-center gap-2">
          <div className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-red-500/80" />
            <span className="w-2.5 h-2.5 rounded-full bg-amber-500/80" />
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-500/80" />
          </div>
          <span className="text-[11px] text-text-muted font-semibold ml-2">
            AI ANALYSIS // CONTENT ENGINE v1.0
          </span>
        </div>
        <div className="flex items-center gap-2">
          {isContentBlocked ? (
            <>
              <PauseCircle className="w-3.5 h-3.5 text-risk-medium" />
              <span className="text-[10px] text-risk-medium font-bold">AWAITING_BROWSER_CONTENT</span>
            </>
          ) : isBrowserFallback ? (
            <>
              <Cpu className="w-3.5 h-3.5 text-brand-light animate-pulse" />
              <span className="text-[10px] text-brand-light font-bold">BROWSER_FALLBACK_ANALYZED</span>
            </>
          ) : (
            <>
              <Cpu className="w-3.5 h-3.5 text-brand-light animate-pulse" />
              <span className="text-[10px] text-brand-light font-bold">ACTIVE_SESSION</span>
            </>
          )}
        </div>
      </div>

      {/* Terminal Console Output */}
      <div className="p-4 space-y-1.5 text-[11px] max-h-56 overflow-y-auto bg-[#040609] text-text-secondary leading-relaxed">
        {logs.slice(0, activeStep + 1).map((log, index) => (
          <div key={index} className="flex items-start gap-2">
            <span className={isContentBlocked && index === logs.length - 1 ? 'text-risk-medium' : 'text-brand-light'}>
              &gt;
            </span>
            <span className={
              index === activeStep 
                ? (isContentBlocked ? 'text-risk-medium font-bold' : 'text-white')
                : 'text-text-muted'
            }>
              {log}
            </span>
          </div>
        ))}
        {isLoading && (
          <div className="flex items-center gap-2 text-brand-light animate-pulse mt-2">
            <span className="inline-block w-2 h-3.5 bg-brand-light" />
            <span>Scanning candidate threat vector...</span>
          </div>
        )}
      </div>

      {/* Structured Findings Grid */}
      <div className="p-3 bg-surface-200/70 border-t border-surface-border grid grid-cols-2 sm:grid-cols-4 gap-2 text-[11px]">
        {/* Credential Integrity */}
        <div className="p-2 rounded bg-surface-100 border border-surface-border flex items-center justify-between">
          <span className="text-text-muted truncate">CREDENTIAL INTEGRITY</span>
          {isContentBlocked ? (
            <span className="text-text-muted flex items-center gap-1 font-semibold text-[10px]">
              <Clock className="w-3 h-3 text-risk-medium" /> PENDING
            </span>
          ) : hasSensitiveFlag ? (
            <span className="text-risk-critical flex items-center gap-1 font-bold">
              <AlertTriangle className="w-3.5 h-3.5" /> FLAG
            </span>
          ) : (
            <span className="text-risk-low flex items-center gap-1 font-bold">
              <Check className="w-3.5 h-3.5" /> PASS
            </span>
          )}
        </div>

        {/* Financial Demands */}
        <div className="p-2 rounded bg-surface-100 border border-surface-border flex items-center justify-between">
          <span className="text-text-muted truncate">FINANCIAL DEMANDS</span>
          {isContentBlocked ? (
            <span className="text-text-muted flex items-center gap-1 font-semibold text-[10px]">
              <Clock className="w-3 h-3 text-risk-medium" /> PENDING
            </span>
          ) : hasPaymentFlag ? (
            <span className="text-risk-critical flex items-center gap-1 font-bold">
              <AlertTriangle className="w-3.5 h-3.5" /> FEE_REQ
            </span>
          ) : (
            <span className="text-risk-low flex items-center gap-1 font-bold">
              <Check className="w-3.5 h-3.5" /> CLEAR
            </span>
          )}
        </div>

        {/* Pressure Tactics */}
        <div className="p-2 rounded bg-surface-100 border border-surface-border flex items-center justify-between">
          <span className="text-text-muted truncate">PRESSURE TACTICS</span>
          {isContentBlocked ? (
            <span className="text-text-muted flex items-center gap-1 font-semibold text-[10px]">
              <Clock className="w-3 h-3 text-risk-medium" /> PENDING
            </span>
          ) : hasUrgencyFlag ? (
            <span className="text-risk-high flex items-center gap-1 font-bold">
              <AlertTriangle className="w-3.5 h-3.5" /> URGENT
            </span>
          ) : (
            <span className="text-risk-low flex items-center gap-1 font-bold">
              <Check className="w-3.5 h-3.5" /> NORMAL
            </span>
          )}
        </div>

        {/* Contact Channel */}
        <div className="p-2 rounded bg-surface-100 border border-surface-border flex items-center justify-between">
          <span className="text-text-muted truncate">CONTACT CHANNEL</span>
          {isContentBlocked ? (
            <span className="text-text-muted flex items-center gap-1 font-semibold text-[10px]">
              <Clock className="w-3 h-3 text-risk-medium" /> PENDING
            </span>
          ) : hasMessagingFlag ? (
            <span className="text-risk-medium flex items-center gap-1 font-bold">
              <AlertTriangle className="w-3.5 h-3.5" /> INFORMAL
            </span>
          ) : (
            <span className="text-risk-low flex items-center gap-1 font-bold">
              <Check className="w-3.5 h-3.5" /> VERIFIED
            </span>
          )}
        </div>
      </div>
    </div>
  );
}
