import React, { useState, useRef } from 'react';
import { 
  Globe, 
  FileText, 
  FileUp, 
  FormInput, 
  FileCode, 
  Play, 
  RefreshCw, 
  UploadCloud, 
  X, 
  CheckCircle2, 
  AlertCircle, 
  Sparkles, 
  Building2, 
  Briefcase,
  AlertTriangle,
  Info
} from 'lucide-react';

export default function MultiInputScanner({
  activeTab,
  setActiveTab,
  scanning,
  targetUrl,
  setTargetUrl,
  onScanUrl,
  onScanPdf,
  onScanForm,
  onScanText,
  presets = [],
}) {
  // PDF state
  const [pdfFile, setPdfFile] = useState(null);
  const [pdfError, setPdfError] = useState(null);
  const [pdfCompany, setPdfCompany] = useState('');
  const [pdfTitle, setPdfTitle] = useState('');
  const [dragOver, setDragOver] = useState(false);
  const fileInputRef = useRef(null);

  // Google Form state
  const [formUrl, setFormUrl] = useState('');

  // Paste Text state
  const [rawText, setRawText] = useState('');
  const [textCompany, setTextCompany] = useState('');
  const [textTitle, setTextTitle] = useState('');

  // Text Presets for Instant Testing
  const textPresets = [
    {
      label: '🚩 Scam: Upfront ₹2,999 Fee',
      title: 'Urgent Data Entry Associate',
      company: 'Global Talent Pvt Ltd',
      text: 'URGENT HIRING: We are immediately recruiting Remote Operations Associates. Salary: ₹75,000 per month. No prior experience required. Immediate joining available. Candidates must pay a mandatory one-time registration fee and security deposit of ₹2,999 to confirm employment. Pay via UPI or Google Pay within 24 hours to secure your slot. Contact recruiter directly on WhatsApp: +91 9876543210.',
    },
    {
      label: '🚩 Scam: Aadhaar & PAN Trap',
      title: 'Back Office Assistant',
      company: 'Swift Career Sol',
      text: 'OFFICIAL SELECTION NOTICE: Congratulations! You have been shortlisted for the Data Verification role. Before the initial interview or offer confirmation, all candidates are required to submit their full Aadhaar card number, PAN card photocopy, and bank account details for immediate background check and payroll verification. Contact our hiring executive on Telegram @FastHiringTeam to proceed.',
    },
    {
      label: '🚩 Scam: Unrealistic Salary & WhatsApp',
      title: 'Work From Home Typist',
      company: 'Premier Tech Services',
      text: 'Guaranteed Part-Time Job Opportunity! Earn ₹1,20,000 to ₹1,80,000 per month working 2 hours a day from home. 100% placement guaranteed. No interview, no resume required. Contact our HR manager only via WhatsApp at +91 9998887776 for immediate spot offer letter and task assignment.',
    },
    {
      label: '✅ Legit: Senior Frontend Engineer',
      title: 'Senior Frontend Engineer (React/TypeScript)',
      company: 'Acme Systems Technologies',
      text: 'Acme Systems is hiring a Senior Frontend Engineer to lead our client-facing web architecture. Requirements: 5+ years of experience with React, TypeScript, and modern CSS. Competitive salary commensurate with experience (₹22,00,000 - ₹30,00,000 per annum), comprehensive health insurance, and flexible remote work options. We do not charge any recruitment or application fees at any stage of our interview process. Applications accepted exclusively through our verified careers portal.',
    },
  ];

  // PDF Handlers
  const handlePdfFileSelection = (file) => {
    setPdfError(null);
    if (!file) return;

    // Check extension / MIME
    const isPdf = file.type === 'application/pdf' || file.name.toLowerCase().endsWith('.pdf');
    if (!isPdf) {
      setPdfError('Invalid file format. Please upload a valid PDF document (.pdf).');
      return;
    }

    // Check size limit: 10MB
    const maxSize = 10 * 1024 * 1024;
    if (file.size > maxSize) {
      setPdfError(`File size exceeds 10MB limit (${(file.size / (1024 * 1024)).toFixed(2)}MB).`);
      return;
    }

    setPdfFile(file);
    if (!pdfTitle) {
      // Clean filename for prefill
      const cleanName = file.name.replace(/\.[^/.]+$/, '').replace(/[_-]/g, ' ');
      setPdfTitle(cleanName);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handlePdfFileSelection(e.dataTransfer.files[0]);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setDragOver(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setDragOver(false);
  };

  const clearPdf = () => {
    setPdfFile(null);
    setPdfError(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <div className="p-6 rounded-2xl bg-surface-100 border border-surface-border glass-panel space-y-6 font-sans">
      {/* 1. Header & Title */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 font-mono text-xs text-brand-light uppercase tracking-wider mb-1">
            <span>MULTI-INPUT RISK PIPELINE // HIRESHIELD v2.0</span>
            <span className="w-1.5 h-1.5 rounded-full bg-brand-light animate-pulse" />
          </div>
          <h2 className="text-2xl font-extrabold text-white tracking-tight">
            What would you like to scan?
          </h2>
          <p className="text-xs text-text-muted mt-1 font-sans">
            Choose your recruitment evidence source. All inputs are evaluated through HireShield's unified multi-vector risk engine.
          </p>
        </div>
      </div>

      {/* 2. Four Interactive Input Mode Tabs */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
        {/* Tab 1: Job URL */}
        <button
          type="button"
          onClick={() => setActiveTab('URL')}
          className={`p-3.5 rounded-xl border text-left transition-all cursor-pointer relative overflow-hidden ${
            activeTab === 'URL'
              ? 'bg-brand-primary/10 border-brand-primary text-white shadow-cyber'
              : 'bg-surface-200/60 border-surface-border text-text-secondary hover:bg-surface-200 hover:text-white'
          }`}
        >
          <div className="flex items-center gap-2.5 mb-1.5">
            <div className={`p-1.5 rounded-lg ${activeTab === 'URL' ? 'bg-brand-primary text-white' : 'bg-surface-300 text-brand-light'}`}>
              <Globe className="w-4 h-4" />
            </div>
            <span className="text-xs font-bold tracking-wide">Job URL</span>
          </div>
          <p className="text-[11px] text-text-muted leading-snug">
            Analyze a recruitment website or job posting link.
          </p>
          {activeTab === 'URL' && (
            <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-brand-light" />
          )}
        </button>

        {/* Tab 2: Upload PDF */}
        <button
          type="button"
          onClick={() => setActiveTab('PDF')}
          className={`p-3.5 rounded-xl border text-left transition-all cursor-pointer relative overflow-hidden ${
            activeTab === 'PDF'
              ? 'bg-brand-primary/10 border-brand-primary text-white shadow-cyber'
              : 'bg-surface-200/60 border-surface-border text-text-secondary hover:bg-surface-200 hover:text-white'
          }`}
        >
          <div className="flex items-center gap-2.5 mb-1.5">
            <div className={`p-1.5 rounded-lg ${activeTab === 'PDF' ? 'bg-brand-primary text-white' : 'bg-surface-300 text-brand-light'}`}>
              <FileUp className="w-4 h-4" />
            </div>
            <span className="text-xs font-bold tracking-wide">Upload PDF</span>
          </div>
          <p className="text-[11px] text-text-muted leading-snug">
            Analyze job offers, appointment letters, and PDFs.
          </p>
          {activeTab === 'PDF' && (
            <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-brand-light" />
          )}
        </button>

        {/* Tab 3: Google Form */}
        <button
          type="button"
          onClick={() => setActiveTab('FORM')}
          className={`p-3.5 rounded-xl border text-left transition-all cursor-pointer relative overflow-hidden ${
            activeTab === 'FORM'
              ? 'bg-brand-primary/10 border-brand-primary text-white shadow-cyber'
              : 'bg-surface-200/60 border-surface-border text-text-secondary hover:bg-surface-200 hover:text-white'
          }`}
        >
          <div className="flex items-center gap-2.5 mb-1.5">
            <div className={`p-1.5 rounded-lg ${activeTab === 'FORM' ? 'bg-brand-primary text-white' : 'bg-surface-300 text-brand-light'}`}>
              <FormInput className="w-4 h-4" />
            </div>
            <span className="text-xs font-bold tracking-wide">Google Form</span>
          </div>
          <p className="text-[11px] text-text-muted leading-snug">
            Analyze recruitment and candidate application forms.
          </p>
          {activeTab === 'FORM' && (
            <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-brand-light" />
          )}
        </button>

        {/* Tab 4: Paste Job Text */}
        <button
          type="button"
          onClick={() => setActiveTab('TEXT')}
          className={`p-3.5 rounded-xl border text-left transition-all cursor-pointer relative overflow-hidden ${
            activeTab === 'TEXT'
              ? 'bg-brand-primary/10 border-brand-primary text-white shadow-cyber'
              : 'bg-surface-200/60 border-surface-border text-text-secondary hover:bg-surface-200 hover:text-white'
          }`}
        >
          <div className="flex items-center gap-2.5 mb-1.5">
            <div className={`p-1.5 rounded-lg ${activeTab === 'TEXT' ? 'bg-brand-primary text-white' : 'bg-surface-300 text-brand-light'}`}>
              <FileCode className="w-4 h-4" />
            </div>
            <span className="text-xs font-bold tracking-wide">Paste Job Text</span>
          </div>
          <p className="text-[11px] text-text-muted leading-snug">
            Analyze copied job descriptions or recruiter messages.
          </p>
          {activeTab === 'TEXT' && (
            <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-brand-light" />
          )}
        </button>
      </div>

      {/* 3. Tab Specific Input Body */}

      {/* MODE 1: JOB URL (Preserves 100% existing functionality) */}
      {activeTab === 'URL' && (
        <div className="space-y-4">
          <form
            onSubmit={(e) => {
              e.preventDefault();
              onScanUrl(targetUrl);
            }}
            className="flex flex-col sm:flex-row items-stretch gap-3"
          >
            <div className="relative flex-1">
              <Globe className="w-4 h-4 text-brand-light absolute left-3.5 top-3.5" />
              <input
                type="url"
                value={targetUrl}
                onChange={(e) => setTargetUrl(e.target.value)}
                placeholder="https://company.com/careers/listing-target"
                required
                disabled={scanning}
                className="w-full pl-10 pr-4 py-3 rounded-lg bg-surface-200 border border-surface-border text-white text-xs font-mono focus:outline-none focus:border-brand-primary focus:ring-1 focus:ring-brand-primary transition-all disabled:opacity-50"
              />
            </div>

            <button
              type="submit"
              disabled={scanning || !targetUrl.trim()}
              className="px-6 py-3 rounded-lg bg-brand-primary hover:bg-brand-light disabled:bg-surface-300 text-white font-mono text-xs font-bold tracking-wider flex items-center justify-center gap-2 shadow-cyber transition-all hover:scale-[1.01] active:scale-[0.99] disabled:scale-100 flex-shrink-0 cursor-pointer"
            >
              {scanning ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  <span>Scanning Pipeline...</span>
                </>
              ) : (
                <>
                  <Play className="w-4 h-4 fill-current" />
                  <span>Execute Risk Scan</span>
                </>
              )}
            </button>
          </form>

          {targetUrl && (targetUrl.includes('forms.gle') || (targetUrl.includes('google.com') && targetUrl.includes('/forms'))) && (
            <div className="flex items-center gap-2 p-2.5 rounded-lg bg-brand-primary/10 border border-brand-primary/30 text-[11px] text-brand-light font-mono">
              <Sparkles className="w-3.5 h-3.5 flex-shrink-0" />
              <span>Google Form detected! HireShield will automatically extract questions and audit for deceptive PII collection.</span>
            </div>
          )}

          {/* Preset Targets */}
          <div className="flex items-center gap-2 flex-wrap pt-1 font-mono text-[11px]">
            <span className="text-text-muted">Preset Test Targets:</span>
            {presets.map((p) => (
              <button
                key={p.label}
                type="button"
                onClick={() => {
                  setTargetUrl(p.url);
                  onScanUrl(p.url);
                }}
                disabled={scanning}
                className="px-2.5 py-1 rounded bg-surface-200 hover:bg-surface-300 text-text-secondary border border-surface-border hover:border-brand-light/30 transition-colors cursor-pointer"
                title={p.desc}
              >
                {p.label}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* MODE 2: UPLOAD PDF */}
      {activeTab === 'PDF' && (
        <div className="space-y-4">
          {/* Metadata Optional Inputs */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div className="relative">
              <Building2 className="w-3.5 h-3.5 text-text-muted absolute left-3 top-3" />
              <input
                type="text"
                value={pdfCompany}
                onChange={(e) => setPdfCompany(e.target.value)}
                placeholder="Issuing Company / Employer (Optional)"
                disabled={scanning}
                className="w-full pl-9 pr-3 py-2 rounded-lg bg-surface-200 border border-surface-border text-white text-xs font-sans focus:outline-none focus:border-brand-primary transition-all disabled:opacity-50"
              />
            </div>
            <div className="relative">
              <Briefcase className="w-3.5 h-3.5 text-text-muted absolute left-3 top-3" />
              <input
                type="text"
                value={pdfTitle}
                onChange={(e) => setPdfTitle(e.target.value)}
                placeholder="Job Role / Offer Title (Optional)"
                disabled={scanning}
                className="w-full pl-9 pr-3 py-2 rounded-lg bg-surface-200 border border-surface-border text-white text-xs font-sans focus:outline-none focus:border-brand-primary transition-all disabled:opacity-50"
              />
            </div>
          </div>

          {/* Drag and Drop Zone */}
          <div
            onDrop={handleDrop}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onClick={() => !pdfFile && fileInputRef.current?.click()}
            className={`p-6 sm:p-8 rounded-xl border-2 border-dashed transition-all text-center flex flex-col items-center justify-center cursor-pointer ${
              dragOver
                ? 'border-brand-light bg-brand-primary/10 scale-[1.01]'
                : pdfFile
                ? 'border-brand-primary/60 bg-surface-200/60 cursor-default'
                : 'border-surface-border hover:border-brand-primary/50 bg-surface-200/40 hover:bg-surface-200/70'
            }`}
          >
            <input
              type="file"
              ref={fileInputRef}
              accept=".pdf,application/pdf"
              onChange={(e) => e.target.files && handlePdfFileSelection(e.target.files[0])}
              className="hidden"
              disabled={scanning}
            />

            {!pdfFile ? (
              <div className="space-y-3">
                <div className="w-12 h-12 rounded-xl bg-surface-300 border border-surface-border flex items-center justify-center text-brand-light mx-auto">
                  <UploadCloud className="w-6 h-6" />
                </div>
                <div>
                  <p className="text-xs font-bold text-white font-mono">
                    DRAG & DROP RECRUITMENT PDF OR <span className="text-brand-light underline">BROWSE FILES</span>
                  </p>
                  <p className="text-[11px] text-text-muted mt-1">
                    Supports Offer Letters, Job Descriptions, and Contract PDFs up to 10MB
                  </p>
                </div>
              </div>
            ) : (
              <div className="w-full flex items-center justify-between p-3.5 rounded-lg bg-surface-300 border border-brand-primary/40">
                <div className="flex items-center gap-3 min-w-0">
                  <div className="p-2 rounded bg-brand-primary/20 text-brand-light border border-brand-primary/30 flex-shrink-0">
                    <FileText className="w-5 h-5" />
                  </div>
                  <div className="text-left min-w-0">
                    <div className="text-xs font-bold text-white truncate font-mono">
                      {pdfFile.name}
                    </div>
                    <div className="text-[10px] text-text-muted font-mono">
                      {(pdfFile.size / 1024).toFixed(1)} KB &bull; application/pdf
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-2 flex-shrink-0">
                  <button
                    type="button"
                    onClick={(e) => {
                      e.stopPropagation();
                      clearPdf();
                    }}
                    disabled={scanning}
                    className="p-1.5 rounded hover:bg-surface-200 text-text-muted hover:text-white transition-colors cursor-pointer"
                    title="Remove file"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>
              </div>
            )}
          </div>

          {pdfError && (
            <div className="flex items-center gap-2 p-3 rounded-lg bg-risk-critical/10 border border-risk-critical/30 text-xs font-mono text-risk-critical">
              <AlertCircle className="w-4 h-4 flex-shrink-0" />
              <span>{pdfError}</span>
            </div>
          )}

          {/* Action Row */}
          <div className="flex flex-col sm:flex-row items-center justify-between gap-3 pt-1">
            <div className="flex items-center gap-2 text-[11px] text-text-muted font-mono">
              <Info className="w-3.5 h-3.5 text-brand-light flex-shrink-0" />
              <span>Scanned / image-only PDFs are handled gracefully with instant text fallback.</span>
            </div>

            <button
              type="button"
              disabled={scanning || !pdfFile}
              onClick={() => onScanPdf(pdfFile, { company: pdfCompany, title: pdfTitle })}
              className="w-full sm:w-auto px-6 py-2.5 rounded-lg bg-brand-primary hover:bg-brand-light disabled:bg-surface-300 text-white font-mono text-xs font-bold tracking-wider flex items-center justify-center gap-2 shadow-cyber transition-all hover:scale-[1.01] active:scale-[0.99] disabled:scale-100 flex-shrink-0 cursor-pointer"
            >
              {scanning ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  <span>Extracting & Auditing PDF...</span>
                </>
              ) : (
                <>
                  <Play className="w-4 h-4 fill-current" />
                  <span>Analyze PDF Document</span>
                </>
              )}
            </button>
          </div>
        </div>
      )}

      {/* MODE 3: GOOGLE FORM URL */}
      {activeTab === 'FORM' && (
        <div className="space-y-4">
          <form
            onSubmit={(e) => {
              e.preventDefault();
              if (formUrl.trim()) onScanForm(formUrl.trim());
            }}
            className="flex flex-col sm:flex-row items-stretch gap-3"
          >
            <div className="relative flex-1">
              <FormInput className="w-4 h-4 text-brand-light absolute left-3.5 top-3.5" />
              <input
                type="url"
                value={formUrl}
                onChange={(e) => setFormUrl(e.target.value)}
                placeholder="https://forms.gle/xyz123 or https://docs.google.com/forms/d/e/.../viewform"
                required
                disabled={scanning}
                className="w-full pl-10 pr-4 py-3 rounded-lg bg-surface-200 border border-surface-border text-white text-xs font-mono focus:outline-none focus:border-brand-primary focus:ring-1 focus:ring-brand-primary transition-all disabled:opacity-50"
              />
            </div>

            <button
              type="submit"
              disabled={scanning || !formUrl.trim()}
              className="px-6 py-3 rounded-lg bg-brand-primary hover:bg-brand-light disabled:bg-surface-300 text-white font-mono text-xs font-bold tracking-wider flex items-center justify-center gap-2 shadow-cyber transition-all hover:scale-[1.01] active:scale-[0.99] disabled:scale-100 flex-shrink-0 cursor-pointer"
            >
              {scanning ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  <span>Auditing Form Questions...</span>
                </>
              ) : (
                <>
                  <Play className="w-4 h-4 fill-current" />
                  <span>Analyze Form</span>
                </>
              )}
            </button>
          </form>

          <div className="p-3.5 rounded-lg bg-surface-200/70 border border-surface-border text-xs text-text-secondary space-y-1.5">
            <div className="flex items-center gap-2 font-mono text-brand-light font-bold text-[11px]">
              <Sparkles className="w-3.5 h-3.5" />
              <span>GOOGLE FORM PII & FRAUD HEURISTICS</span>
            </div>
            <p className="text-[11px] text-text-muted leading-relaxed">
              Scrutinizes publicly accessible form fields for suspicious requests including Aadhaar numbers, PAN cards, passports, bank account details, UPI ID collections, and registration fee clauses.
            </p>
            <p className="text-[11px] text-text-muted font-mono pt-1">
              Tip: If Google restricts automated access or requires login, click <strong>Paste Job Text</strong> above to paste the form questions directly.
            </p>
          </div>
        </div>
      )}

      {/* MODE 4: PASTE JOB TEXT */}
      {activeTab === 'TEXT' && (
        <div className="space-y-4">
          {/* Metadata Optional Inputs */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div className="relative">
              <Building2 className="w-3.5 h-3.5 text-text-muted absolute left-3 top-3" />
              <input
                type="text"
                value={textCompany}
                onChange={(e) => setTextCompany(e.target.value)}
                placeholder="Target Company / Recruiter Name (Optional)"
                disabled={scanning}
                className="w-full pl-9 pr-3 py-2 rounded-lg bg-surface-200 border border-surface-border text-white text-xs font-sans focus:outline-none focus:border-brand-primary transition-all disabled:opacity-50"
              />
            </div>
            <div className="relative">
              <Briefcase className="w-3.5 h-3.5 text-text-muted absolute left-3 top-3" />
              <input
                type="text"
                value={textTitle}
                onChange={(e) => setTextTitle(e.target.value)}
                placeholder="Job Role / Headline (Optional)"
                disabled={scanning}
                className="w-full pl-9 pr-3 py-2 rounded-lg bg-surface-200 border border-surface-border text-white text-xs font-sans focus:outline-none focus:border-brand-primary transition-all disabled:opacity-50"
              />
            </div>
          </div>

          {/* Text Area */}
          <div className="relative">
            <textarea
              rows={6}
              value={rawText}
              onChange={(e) => setRawText(e.target.value)}
              placeholder="Paste copied job descriptions, WhatsApp/Telegram recruitment pitches, or email job offers here..."
              disabled={scanning}
              className="w-full p-4 rounded-xl bg-surface-200 border border-surface-border text-white text-xs font-sans leading-relaxed focus:outline-none focus:border-brand-primary focus:ring-1 focus:ring-brand-primary transition-all disabled:opacity-50 resize-y min-h-[140px]"
            />
            <div className="absolute right-3 bottom-3 text-[10px] font-mono text-text-muted bg-surface-300/80 px-2 py-0.5 rounded border border-surface-border">
              {rawText.length} characters
            </div>
          </div>

          {/* Preset Buttons for Quick Demo Testing */}
          <div className="space-y-2">
            <div className="text-[11px] font-mono text-text-muted flex items-center gap-1.5">
              <span>Quick Test Presets (Instant Demo):</span>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-2">
              {textPresets.map((preset, idx) => (
                <button
                  key={idx}
                  type="button"
                  onClick={() => {
                    setRawText(preset.text);
                    setTextTitle(preset.title);
                    setTextCompany(preset.company);
                  }}
                  disabled={scanning}
                  className="p-2.5 rounded-lg bg-surface-200 hover:bg-surface-300 border border-surface-border hover:border-brand-primary/40 text-left transition-colors cursor-pointer group"
                >
                  <div className="text-xs font-bold text-white group-hover:text-brand-light truncate">
                    {preset.label}
                  </div>
                  <div className="text-[10px] text-text-muted truncate mt-0.5">
                    {preset.company} &bull; {preset.title}
                  </div>
                </button>
              ))}
            </div>
          </div>

          {/* Action Row */}
          <div className="flex items-center justify-end pt-1">
            <button
              type="button"
              disabled={scanning || rawText.trim().length < 15}
              onClick={() => onScanText({ text: rawText.trim(), title: textTitle, company: textCompany })}
              className="px-6 py-2.5 rounded-lg bg-brand-primary hover:bg-brand-light disabled:bg-surface-300 text-white font-mono text-xs font-bold tracking-wider flex items-center justify-center gap-2 shadow-cyber transition-all hover:scale-[1.01] active:scale-[0.99] disabled:scale-100 cursor-pointer"
            >
              {scanning ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  <span>Evaluating Job Text...</span>
                </>
              ) : (
                <>
                  <Play className="w-4 h-4 fill-current" />
                  <span>Analyze Job Text</span>
                </>
              )}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
