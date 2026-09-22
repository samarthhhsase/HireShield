import React, { useState } from 'react';
import { 
  Download, 
  FolderArchive, 
  FolderOpen, 
  Chrome, 
  FolderInput, 
  Pin, 
  Search, 
  Check, 
  Copy, 
  AlertCircle, 
  HelpCircle, 
  ChevronDown, 
  ChevronUp, 
  ExternalLink, 
  ShieldCheck, 
  Sliders, 
  CheckCircle2,
  Info,
  Zap
} from 'lucide-react';

export default function InstallExtensionSection() {
  const [copiedUrl, setCopiedUrl] = useState(false);
  const [downloading, setDownloading] = useState(false);
  const [openFaq, setOpenFaq] = useState(null);

  const handleDownload = () => {
    setDownloading(true);
    const link = document.createElement('a');
    link.href = '/hireshield-extension.zip';
    link.download = 'hireshield-extension.zip';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    setTimeout(() => {
      setDownloading(false);
    }, 2000);
  };

  const handleCopyChromeUrl = () => {
    navigator.clipboard.writeText('chrome://extensions/');
    setCopiedUrl(true);
    setTimeout(() => setCopiedUrl(false), 2200);
  };

  const toggleFaq = (index) => {
    setOpenFaq(openFaq === index ? null : index);
  };

  const troubleshootingItems = [
    {
      id: 1,
      question: '"Load unpacked" button does not appear or is grayed out',
      badge: 'Configuration',
      solution: (
        <div className="space-y-2 text-text-secondary text-xs sm:text-sm">
          <p>
            Make sure the <strong className="text-white">"Developer mode"</strong> switch in the top-right corner of{' '}
            <code className="px-1.5 py-0.5 rounded bg-surface-300 text-brand-light font-mono text-xs">chrome://extensions/</code> is toggled <strong className="text-emerald-400">ON</strong>.
          </p>
          <p className="text-text-muted">
            The button will appear immediately on the top-left toolbar once Developer mode is activated.
          </p>
        </div>
      )
    },
    {
      id: 2,
      question: 'Chrome displays error: "Manifest file is missing or unreadable"',
      badge: 'Folder Selection',
      solution: (
        <div className="space-y-2 text-text-secondary text-xs sm:text-sm">
          <p>
            This error means you selected the wrong folder level. Please make sure you selected the extracted folder that contains{' '}
            <code className="px-1.5 py-0.5 rounded bg-surface-300 text-brand-light font-mono text-xs">manifest.json</code> directly inside it.
          </p>
          <ul className="list-disc list-inside space-y-1 text-text-muted text-xs">
            <li>Do <span className="text-risk-critical font-semibold">NOT</span> select the unextracted <code className="text-white">.zip</code> file.</li>
            <li>Do <span className="text-risk-critical font-semibold">NOT</span> select a parent folder that contains another nested HireShield folder.</li>
            <li>Open the extracted folder in File Explorer / Finder first to confirm <code className="text-white">manifest.json</code> is visible, then choose that exact folder.</li>
          </ul>
        </div>
      )
    },
    {
      id: 3,
      question: 'Extension shows "Offline" or fails to connect',
      badge: 'Network / Backend',
      solution: (
        <div className="space-y-2 text-text-secondary text-xs sm:text-sm">
          <p>
            Make sure you are using the latest extension package downloaded directly from the HireShield website.
          </p>
          <p className="text-text-muted">
            The extension connects directly to the live production cloud backend on Railway (<span className="text-brand-light font-mono text-xs">hireshield-production.up.railway.app</span>). You do <strong className="text-white">NOT</strong> need to run any local server, terminal, Python, or Node.js.
          </p>
        </div>
      )
    },
    {
      id: 4,
      question: 'Extension does not appear in the toolbar after loading',
      badge: 'Visibility',
      solution: (
        <div className="space-y-2 text-text-secondary text-xs sm:text-sm">
          <p>
            Chrome automatically puts newly loaded extensions under the puzzle-piece icon (<strong className="text-white">Extensions 🧩</strong>) in your top-right browser bar.
          </p>
          <p className="text-text-muted">
            Click the puzzle-piece icon, locate <strong className="text-white">HireShield</strong> in the list, and click the <strong className="text-brand-light">Pin icon</strong>. If it still doesn't appear, refresh <code className="px-1.5 py-0.5 rounded bg-surface-300 text-white font-mono text-xs">chrome://extensions/</code> or click the reload arrow on the HireShield card.
          </p>
        </div>
      )
    }
  ];

  return (
    <section id="install-extension" className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 scroll-mt-24">
      {/* Section Header */}
      <div className="text-center max-w-3xl mx-auto mb-12 sm:mb-16 space-y-4">
        <div className="inline-flex items-center gap-2 font-mono text-xs text-brand-light uppercase tracking-widest bg-brand-primary/10 px-3 py-1 rounded-full border border-brand-primary/25 shadow-sm">
          <Chrome className="w-3.5 h-3.5 text-brand-light" />
          <span>EXTENSION DEPLOYMENT // QUICK START GUIDE</span>
        </div>

        <h2 className="text-3xl sm:text-4xl lg:text-5xl font-extrabold text-white tracking-tight">
          How to Install the HireShield Extension
        </h2>

        <p className="text-sm sm:text-base text-text-secondary leading-relaxed font-sans max-w-2xl mx-auto">
          Get real-time recruitment fraud detection directly inside your browser. Follow these 6 straightforward steps to install HireShield in under 60 seconds.
        </p>

        {/* Informational Context Banner */}
        <div className="p-4 sm:p-5 rounded-xl bg-surface-100/90 border border-brand-primary/30 shadow-lg text-left flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div className="flex items-start gap-3">
            <div className="w-8 h-8 rounded-lg bg-brand-primary/20 border border-brand-primary/40 flex items-center justify-center shrink-0 mt-0.5">
              <Info className="w-4 h-4 text-brand-light" />
            </div>
            <div>
              <div className="font-mono text-xs text-brand-light font-bold uppercase tracking-wider">
                Developer-Installed Chrome Extension
              </div>
              <p className="text-xs text-text-muted mt-0.5 leading-relaxed font-sans">
                HireShield is currently available as a developer-installed Chrome extension and is not yet published on the Chrome Web Store. 
                You only need to complete these steps <strong className="text-white">once</strong>.
              </p>
            </div>
          </div>

          <button
            type="button"
            onClick={handleDownload}
            disabled={downloading}
            className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-5 py-2.5 rounded-lg bg-brand-primary hover:bg-brand-light text-white font-mono text-xs font-bold tracking-wide shadow-cyber transition-all hover:scale-[1.02] active:scale-[0.98] shrink-0 cursor-pointer"
          >
            <Download className={`w-4 h-4 ${downloading ? 'animate-bounce' : ''}`} />
            <span>{downloading ? 'Downloading ZIP...' : 'Download Extension (.ZIP)'}</span>
          </button>
        </div>
      </div>

      {/* 6 Steps Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 font-sans">
        
        {/* STEP 1 */}
        <div className="p-6 rounded-xl bg-surface-100 border border-surface-border glass-panel-hover flex flex-col justify-between relative group shadow-sm">
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="font-mono text-xs font-extrabold text-brand-light px-2.5 py-1 rounded-md bg-brand-primary/15 border border-brand-primary/30">
                STEP 01
              </span>
              <div className="w-8 h-8 rounded-lg bg-surface-200 border border-surface-border flex items-center justify-center text-brand-light group-hover:text-white transition-colors">
                <Download className="w-4 h-4" />
              </div>
            </div>

            <div>
              <h3 className="text-lg font-bold text-white tracking-tight mb-1.5">
                Download HireShield
              </h3>
              <p className="text-xs text-text-muted leading-relaxed">
                Click the <strong className="text-white font-semibold">"Download Extension"</strong> button on the HireShield website to get the package.
              </p>
            </div>

            <div className="p-3.5 rounded-lg bg-surface-200/90 border border-surface-border/80 text-xs space-y-2">
              <div className="flex items-center justify-between text-[11px] font-mono text-text-muted">
                <span>DOWNLOAD FORMAT:</span>
                <span className="text-emerald-400 font-semibold">ZIP ARCHIVE (.zip)</span>
              </div>
              <div className="flex items-center justify-between text-[11px] font-mono text-text-muted">
                <span>FILE NAME:</span>
                <span className="text-white">hireshield-extension.zip</span>
              </div>
            </div>
          </div>

          <div className="pt-5 mt-4 border-t border-surface-border/60">
            <button
              type="button"
              onClick={handleDownload}
              className="w-full flex items-center justify-center gap-2 py-2 px-3 rounded-lg bg-surface-200 hover:bg-brand-primary/20 text-text-primary hover:text-white border border-surface-border hover:border-brand-primary/40 font-mono text-xs transition-all cursor-pointer"
            >
              <Download className="w-3.5 h-3.5 text-brand-light" />
              <span>Download ZIP Package</span>
            </button>
          </div>
        </div>

        {/* STEP 2 */}
        <div className="p-6 rounded-xl bg-surface-100 border border-surface-border glass-panel-hover flex flex-col justify-between relative group shadow-sm">
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="font-mono text-xs font-extrabold text-brand-light px-2.5 py-1 rounded-md bg-brand-primary/15 border border-brand-primary/30">
                STEP 02
              </span>
              <div className="w-8 h-8 rounded-lg bg-surface-200 border border-surface-border flex items-center justify-center text-brand-light group-hover:text-white transition-colors">
                <FolderArchive className="w-4 h-4" />
              </div>
            </div>

            <div>
              <h3 className="text-lg font-bold text-white tracking-tight mb-1.5">
                Extract the ZIP
              </h3>
              <p className="text-xs text-text-muted leading-relaxed">
                Locate the downloaded ZIP file in your <strong className="text-white font-semibold">Downloads</strong> folder and extract it:
              </p>
            </div>

            <div className="space-y-2 text-xs text-text-secondary">
              <div className="flex items-start gap-2">
                <span className="w-4 h-4 rounded-full bg-surface-200 border border-surface-border text-brand-light font-mono text-[10px] flex items-center justify-center shrink-0 mt-0.5">1</span>
                <span>Right-click the ZIP file</span>
              </div>
              <div className="flex items-start gap-2">
                <span className="w-4 h-4 rounded-full bg-surface-200 border border-surface-border text-brand-light font-mono text-[10px] flex items-center justify-center shrink-0 mt-0.5">2</span>
                <span>Select <strong className="text-white">"Extract All..."</strong></span>
              </div>
              <div className="flex items-start gap-2">
                <span className="w-4 h-4 rounded-full bg-surface-200 border border-surface-border text-brand-light font-mono text-[10px] flex items-center justify-center shrink-0 mt-0.5">3</span>
                <span>Choose a convenient location</span>
              </div>
              <div className="flex items-start gap-2">
                <span className="w-4 h-4 rounded-full bg-surface-200 border border-surface-border text-brand-light font-mono text-[10px] flex items-center justify-center shrink-0 mt-0.5">4</span>
                <span>Click <strong className="text-white">"Extract"</strong></span>
              </div>
            </div>
          </div>

          {/* Directory Tree Callout */}
          <div className="pt-4 mt-3 border-t border-surface-border/60">
            <div className="p-3 rounded-lg bg-surface-300/80 border border-surface-border font-mono text-[11px] text-text-muted">
              <div className="text-brand-light font-semibold mb-1 flex items-center gap-1.5">
                <FolderOpen className="w-3.5 h-3.5" />
                <span>Extracted Folder Contents:</span>
              </div>
              <div className="text-[10px] text-text-secondary leading-tight pl-1 space-y-0.5">
                <div>📁 HireShield Extension/</div>
                <div className="text-emerald-400 font-bold">├── manifest.json  ⭐</div>
                <div>├── popup.html</div>
                <div>├── popup.js</div>
                <div>├── popup.css</div>
                <div>├── content.js</div>
                <div>├── background.js</div>
                <div>└── icons/</div>
              </div>
              <div className="text-[10px] text-brand-light/90 mt-2 font-sans italic">
                *The extracted folder must contain manifest.json directly inside it.
              </div>
            </div>
          </div>
        </div>

        {/* STEP 3 */}
        <div className="p-6 rounded-xl bg-surface-100 border border-surface-border glass-panel-hover flex flex-col justify-between relative group shadow-sm">
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="font-mono text-xs font-extrabold text-brand-light px-2.5 py-1 rounded-md bg-brand-primary/15 border border-brand-primary/30">
                STEP 03
              </span>
              <div className="w-8 h-8 rounded-lg bg-surface-200 border border-surface-border flex items-center justify-center text-brand-light group-hover:text-white transition-colors">
                <Chrome className="w-4 h-4" />
              </div>
            </div>

            <div>
              <h3 className="text-lg font-bold text-white tracking-tight mb-1.5">
                Open Chrome Extensions
              </h3>
              <p className="text-xs text-text-muted leading-relaxed">
                Open Google Chrome and navigate to the extensions configuration page:
              </p>
            </div>

            {/* chrome://extensions address bar mockup */}
            <div className="p-3 rounded-lg bg-surface-200 border border-surface-border space-y-2">
              <div className="text-[10px] font-mono text-text-muted uppercase">Open in Chrome:</div>
              <div className="flex items-center justify-between gap-2 px-3 py-1.5 rounded bg-surface-300 border border-surface-border/80 font-mono text-xs text-white">
                <span className="truncate">chrome://extensions/</span>
                <button
                  type="button"
                  onClick={handleCopyChromeUrl}
                  title="Copy URL to clipboard"
                  className="p-1 rounded hover:bg-surface-100 text-text-muted hover:text-white transition-colors cursor-pointer"
                >
                  {copiedUrl ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                </button>
              </div>
              {copiedUrl && (
                <div className="text-[10px] font-mono text-emerald-400 text-center">
                  URL copied! Paste into Chrome's address bar.
                </div>
              )}
            </div>

            {/* Developer Mode Toggle Visual */}
            <div className="p-3 rounded-lg bg-surface-200/90 border border-surface-border/80 space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-xs font-medium text-white">Developer mode</span>
                <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-brand-primary/20 border border-brand-primary/50 text-[11px] font-mono font-bold text-brand-light">
                  <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
                  <span>TURN ON</span>
                </div>
              </div>
              <p className="text-[11px] text-text-muted leading-relaxed">
                Turn <strong className="text-white">ON</strong> the "Developer mode" switch in the <strong className="text-white">top-right corner</strong> of the page.
              </p>
            </div>
          </div>

          <div className="pt-3 mt-3 border-t border-surface-border/60 font-mono text-[11px] text-text-muted flex items-center gap-1.5">
            <Sliders className="w-3.5 h-3.5 text-brand-light" />
            <span>Enables developer installation mode</span>
          </div>
        </div>

        {/* STEP 4 */}
        <div className="p-6 rounded-xl bg-surface-100 border border-surface-border glass-panel-hover flex flex-col justify-between relative group shadow-sm">
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="font-mono text-xs font-extrabold text-brand-light px-2.5 py-1 rounded-md bg-brand-primary/15 border border-brand-primary/30">
                STEP 04
              </span>
              <div className="w-8 h-8 rounded-lg bg-surface-200 border border-surface-border flex items-center justify-center text-brand-light group-hover:text-white transition-colors">
                <FolderInput className="w-4 h-4" />
              </div>
            </div>

            <div>
              <h3 className="text-lg font-bold text-white tracking-tight mb-1.5">
                Load the Extension
              </h3>
              <p className="text-xs text-text-muted leading-relaxed">
                Load the extracted extension folder into Google Chrome:
              </p>
            </div>

            <div className="space-y-2 text-xs text-text-secondary">
              <div className="flex items-start gap-2">
                <span className="w-4 h-4 rounded-full bg-surface-200 border border-surface-border text-brand-light font-mono text-[10px] flex items-center justify-center shrink-0 mt-0.5">1</span>
                <span>Click <strong className="text-white font-semibold">"Load unpacked"</strong> in the top-left corner.</span>
              </div>
              <div className="flex items-start gap-2">
                <span className="w-4 h-4 rounded-full bg-surface-200 border border-surface-border text-brand-light font-mono text-[10px] flex items-center justify-center shrink-0 mt-0.5">2</span>
                <span>Select the extracted <strong className="text-white">HireShield Extension</strong> folder.</span>
              </div>
              <div className="flex items-start gap-2">
                <span className="w-4 h-4 rounded-full bg-surface-200 border border-surface-border text-brand-light font-mono text-[10px] flex items-center justify-center shrink-0 mt-0.5">3</span>
                <span>Click <strong className="text-white font-semibold">"Select Folder"</strong>.</span>
              </div>
            </div>

            {/* Important Warning Callout */}
            <div className="p-3 rounded-lg bg-risk-medium/10 border border-risk-medium/30 text-[11px] text-text-secondary space-y-1">
              <div className="font-bold text-risk-medium flex items-center gap-1">
                <AlertCircle className="w-3.5 h-3.5 shrink-0" />
                <span>Important Folder Rule:</span>
              </div>
              <p className="text-text-muted leading-relaxed">
                Select the folder containing <code className="text-white font-mono">manifest.json</code> directly, <strong className="text-white">NOT</strong> the ZIP file and <strong className="text-white">NOT</strong> a parent folder containing another HireShield folder.
              </p>
            </div>
          </div>

          <div className="pt-3 mt-3 border-t border-surface-border/60 font-mono text-[11px] text-text-muted flex items-center gap-1.5">
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
            <span>HireShield will load immediately into Chrome</span>
          </div>
        </div>

        {/* STEP 5 */}
        <div className="p-6 rounded-xl bg-surface-100 border border-surface-border glass-panel-hover flex flex-col justify-between relative group shadow-sm">
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="font-mono text-xs font-extrabold text-brand-light px-2.5 py-1 rounded-md bg-brand-primary/15 border border-brand-primary/30">
                STEP 05
              </span>
              <div className="w-8 h-8 rounded-lg bg-surface-200 border border-surface-border flex items-center justify-center text-brand-light group-hover:text-white transition-colors">
                <Pin className="w-4 h-4" />
              </div>
            </div>

            <div>
              <h3 className="text-lg font-bold text-white tracking-tight mb-1.5">
                Pin HireShield
              </h3>
              <p className="text-xs text-text-muted leading-relaxed">
                Pin HireShield to keep it conveniently visible in your browser toolbar:
              </p>
            </div>

            <div className="space-y-2 text-xs text-text-secondary">
              <div className="flex items-start gap-2">
                <span className="w-4 h-4 rounded-full bg-surface-200 border border-surface-border text-brand-light font-mono text-[10px] flex items-center justify-center shrink-0 mt-0.5">1</span>
                <span>Click the Extensions puzzle-piece icon (<strong className="text-white font-semibold">🧩</strong>) in Chrome's toolbar.</span>
              </div>
              <div className="flex items-start gap-2">
                <span className="w-4 h-4 rounded-full bg-surface-200 border border-surface-border text-brand-light font-mono text-[10px] flex items-center justify-center shrink-0 mt-0.5">2</span>
                <span>Find <strong className="text-white">HireShield</strong> in the dropdown menu.</span>
              </div>
              <div className="flex items-start gap-2">
                <span className="w-4 h-4 rounded-full bg-surface-200 border border-surface-border text-brand-light font-mono text-[10px] flex items-center justify-center shrink-0 mt-0.5">3</span>
                <span>Click the <strong className="text-brand-light font-semibold">pin icon (📌)</strong> to keep it visible.</span>
              </div>
            </div>

            <div className="p-3 rounded-lg bg-surface-200/90 border border-surface-border/80 flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-brand-primary/20 border border-brand-primary/40 flex items-center justify-center shrink-0">
                <ShieldCheck className="w-4 h-4 text-brand-light" />
              </div>
              <div className="text-xs">
                <div className="font-semibold text-white">HireShield Always Visible</div>
                <div className="text-[11px] text-text-muted">Quick access on every job portal you visit</div>
              </div>
            </div>
          </div>

          <div className="pt-3 mt-3 border-t border-surface-border/60 font-mono text-[11px] text-text-muted flex items-center gap-1.5">
            <Zap className="w-3.5 h-3.5 text-brand-light" />
            <span>Ready for one-click security checks</span>
          </div>
        </div>

        {/* STEP 6 */}
        <div className="p-6 rounded-xl bg-surface-100 border border-surface-border glass-panel-hover flex flex-col justify-between relative group shadow-sm">
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="font-mono text-xs font-extrabold text-brand-light px-2.5 py-1 rounded-md bg-brand-primary/15 border border-brand-primary/30">
                STEP 06
              </span>
              <div className="w-8 h-8 rounded-lg bg-surface-200 border border-surface-border flex items-center justify-center text-brand-light group-hover:text-white transition-colors">
                <Search className="w-4 h-4" />
              </div>
            </div>

            <div>
              <h3 className="text-lg font-bold text-white tracking-tight mb-1.5">
                Use HireShield
              </h3>
              <p className="text-xs text-text-muted leading-relaxed">
                Scan job postings and instantly view risk scores and fraud explanations:
              </p>
            </div>

            <div className="space-y-2 text-xs text-text-secondary">
              <div className="flex items-start gap-2">
                <span className="w-4 h-4 rounded-full bg-surface-200 border border-surface-border text-brand-light font-mono text-[10px] flex items-center justify-center shrink-0 mt-0.5">1</span>
                <span>Open a job listing website (LinkedIn, Indeed, Naukri, or career page).</span>
              </div>
              <div className="flex items-start gap-2">
                <span className="w-4 h-4 rounded-full bg-surface-200 border border-surface-border text-brand-light font-mono text-[10px] flex items-center justify-center shrink-0 mt-0.5">2</span>
                <span>Click the <strong className="text-white">HireShield extension icon</strong>.</span>
              </div>
              <div className="flex items-start gap-2">
                <span className="w-4 h-4 rounded-full bg-surface-200 border border-surface-border text-brand-light font-mono text-[10px] flex items-center justify-center shrink-0 mt-0.5">3</span>
                <span>Click <strong className="text-brand-light font-semibold">"Scan" / "Analyze"</strong>.</span>
              </div>
            </div>

            <div className="p-3 rounded-lg bg-emerald-500/10 border border-emerald-500/30 text-xs text-emerald-400 space-y-0.5">
              <div className="font-semibold flex items-center gap-1.5">
                <CheckCircle2 className="w-3.5 h-3.5" />
                <span>Instant Forensic Intelligence</span>
              </div>
              <p className="text-[11px] text-text-secondary">
                HireShield will analyze the job and display its risk score and explanation.
              </p>
            </div>
          </div>

          <div className="pt-3 mt-3 border-t border-surface-border/60 font-mono text-[11px] text-text-muted flex items-center gap-1.5">
            <Check className="w-3.5 h-3.5 text-emerald-400" />
            <span>Protected against recruitment scams</span>
          </div>
        </div>

      </div>

      {/* Production Infrastructure Callout Card */}
      <div className="mt-10 p-6 sm:p-8 rounded-2xl bg-surface-100 border border-surface-border/90 relative overflow-hidden shadow-xl">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-center">
          <div className="lg:col-span-8 space-y-3">
            <div className="flex items-center gap-2 font-mono text-xs text-brand-light font-semibold uppercase tracking-wider">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
              <span>PRODUCTION BACKEND // ZERO SETUP REQUIRED</span>
            </div>
            
            <h3 className="text-xl sm:text-2xl font-bold text-white tracking-tight">
              Connects directly to the live HireShield production cloud.
            </h3>

            <p className="text-xs sm:text-sm text-text-secondary leading-relaxed font-sans">
              The extension connects directly to the production HireShield backend (<span className="text-brand-light font-mono text-xs">https://hireshield-production.up.railway.app/</span>). 
              Deep dossiers and audit reports open directly on our hosted platform (<span className="text-brand-light font-mono text-xs">https://frontend-theta-nine-39.vercel.app/risk-analysis</span>). 
              You do <strong className="text-white">NOT</strong> need to run localhost servers or install Python/Node.js.
            </p>

            <div className="flex flex-wrap gap-4 pt-1 font-mono text-xs text-text-muted">
              <div className="flex items-center gap-1.5">
                <span className="text-brand-light">API Backend:</span>
                <span className="text-white font-medium">hireshield-production.up.railway.app</span>
              </div>
              <div className="flex items-center gap-1.5">
                <span className="text-brand-light">Full Analysis:</span>
                <span className="text-white font-medium">frontend-theta-nine-39.vercel.app/risk-analysis</span>
              </div>
            </div>
          </div>

          <div className="lg:col-span-4 flex flex-col sm:flex-row lg:flex-col gap-3 justify-center">
            <button
              type="button"
              onClick={handleDownload}
              className="inline-flex items-center justify-center gap-2.5 px-6 py-3.5 rounded-xl bg-brand-primary hover:bg-brand-light text-white font-mono text-xs font-bold tracking-wide shadow-cyber transition-all hover:scale-[1.02] active:scale-[0.98] cursor-pointer"
            >
              <Download className="w-4 h-4" />
              <span>Download Extension (.ZIP)</span>
            </button>

            <a
              href="https://frontend-theta-nine-39.vercel.app/risk-analysis"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center justify-center gap-2 px-5 py-3 rounded-xl bg-surface-200 hover:bg-surface-300 text-text-secondary hover:text-white border border-surface-border font-mono text-xs transition-all"
            >
              <span>View Full Analysis</span>
              <ExternalLink className="w-3.5 h-3.5 text-text-muted" />
            </a>
          </div>
        </div>
      </div>

      {/* Troubleshooting Section */}
      <div className="mt-12 sm:mt-16 pt-10 border-t border-surface-border/80">
        <div className="text-center max-w-2xl mx-auto mb-8 space-y-2">
          <div className="inline-flex items-center gap-1.5 font-mono text-xs text-text-muted uppercase tracking-wider">
            <HelpCircle className="w-3.5 h-3.5 text-brand-light" />
            <span>Troubleshooting Guide</span>
          </div>
          <h3 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
            Common Problems &amp; Quick Fixes
          </h3>
          <p className="text-xs sm:text-sm text-text-muted font-sans">
            Encountering an issue? Here are quick solutions to common setup questions.
          </p>
        </div>

        <div className="max-w-4xl mx-auto space-y-3 font-sans">
          {troubleshootingItems.map((item) => {
            const isOpen = openFaq === item.id;
            return (
              <div 
                key={item.id}
                className="rounded-xl bg-surface-100 border border-surface-border overflow-hidden transition-colors"
              >
                <button
                  type="button"
                  onClick={() => toggleFaq(item.id)}
                  className="w-full flex items-center justify-between p-4 sm:p-5 text-left hover:bg-surface-200/50 transition-colors gap-4 cursor-pointer"
                >
                  <div className="flex items-center gap-3">
                    <span className="w-6 h-6 rounded-full bg-surface-200 border border-surface-border flex items-center justify-center text-xs font-mono text-brand-light shrink-0">
                      {item.id}
                    </span>
                    <span className="text-sm sm:text-base font-semibold text-white">
                      {item.question}
                    </span>
                  </div>

                  <div className="flex items-center gap-2.5 shrink-0">
                    <span className="hidden sm:inline-block px-2 py-0.5 rounded text-[10px] font-mono font-medium text-text-muted bg-surface-200 border border-surface-border">
                      {item.badge}
                    </span>
                    {isOpen ? (
                      <ChevronUp className="w-4 h-4 text-brand-light" />
                    ) : (
                      <ChevronDown className="w-4 h-4 text-text-muted" />
                    )}
                  </div>
                </button>

                {isOpen && (
                  <div className="px-5 pb-5 pt-2 border-t border-surface-border/50 bg-surface-200/40">
                    {item.solution}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
