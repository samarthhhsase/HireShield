/**
 * HireShield Chrome Extension — Popup Client
 * 
 * Recruitment Risk Intelligence & Threat Analysis Client.
 * Connects directly to the HireShield FastAPI backend (/api/scanner/analyze-content).
 * Strictly preserves the backend state model, real risk scores, and threat levels.
 */

const API_BASE_URLS = [
  "https://hireshield-production.up.railway.app",
  "http://127.0.0.1:8001",
  "http://localhost:8001",
  "http://127.0.0.1:8000",
  "http://localhost:8000",
];

const WEB_APP_URL =
  "https://frontend-theta-nine-39.vercel.app/risk-analysis";

// Current active state cache
let currentTab = null;
let currentJobData = null;
let lastAnalysisResult = null;
let activeBackendUrl = API_BASE_URLS[0];
let lastActiveScannerView = "ready";

// DOM Elements
const views = {
  ready: document.getElementById("readyView"),
  scanning: document.getElementById("scanningView"),
  results: document.getElementById("resultsView"),
  error: document.getElementById("errorView"),
  extension: document.getElementById("extensionView"),
};

const elements = {
  statusPill: document.getElementById("backendStatusPill"),
  statusText: document.getElementById("backendStatusText"),

  // Navigation Tabs
  tabScannerBtn: document.getElementById("tabScannerBtn"),
  tabExtensionBtn: document.getElementById("tabExtensionBtn"),
  backToScannerBtn: document.getElementById("backToScannerBtn"),
  openExtensionsPageBtn: document.getElementById("openExtensionsPageBtn"),

  // Ready View
  readyJobTitle: document.getElementById("readyJobTitle"),
  readyJobUrl: document.getElementById("readyJobUrl"),
  readyTargetType: document.getElementById("readyTargetType"),
  startScanBtn: document.getElementById("startScanBtn"),

  // Scanning View
  scanStageHeadline: document.getElementById("scanStageHeadline"),
  stageExtract: document.getElementById("stageExtract"),
  stageUrl: document.getElementById("stageUrl"),
  stageNlp: document.getElementById("stageNlp"),
  stageBehavioral: document.getElementById("stageBehavioral"),
  stageRisk: document.getElementById("stageRisk"),

  // Results View
  resultSourceBadge: document.getElementById("resultSourceBadge"),
  resultStatusBadge: document.getElementById("resultStatusBadge"),
  resultJobTitle: document.getElementById("resultJobTitle"),
  resultCompany: document.getElementById("resultCompany"),
  resultUrl: document.getElementById("resultUrl"),
  scoreBanner: document.getElementById("scoreBanner"),
  resultScoreValue: document.getElementById("resultScoreValue"),
  resultScoreDenom: document.getElementById("resultScoreDenom"),
  resultRiskLevelBadge: document.getElementById("resultRiskLevelBadge"),
  resultScoreSubtext: document.getElementById("resultScoreSubtext"),

  // Layers
  valBehavioral: document.getElementById("valBehavioral"),
  barBehavioral: document.getElementById("barBehavioral"),
  valLinguistic: document.getElementById("valLinguistic"),
  barLinguistic: document.getElementById("barLinguistic"),
  valStructural: document.getElementById("valStructural"),
  barStructural: document.getElementById("barStructural"),
  valTechnical: document.getElementById("valTechnical"),
  barTechnical: document.getElementById("barTechnical"),

  // Signals & Explanation & Why Drawer
  signalsCountBadge: document.getElementById("signalsCountBadge"),
  signalsListContainer: document.getElementById("signalsListContainer"),
  redFlagsCard: document.getElementById("redFlagsCard"),
  redFlagsCountBadge: document.getElementById("redFlagsCountBadge"),
  redFlagsListContainer: document.getElementById("redFlagsListContainer"),
  trustSignalsCard: document.getElementById("trustSignalsCard"),
  trustSignalsCountBadge: document.getElementById("trustSignalsCountBadge"),
  trustSignalsListContainer: document.getElementById("trustSignalsListContainer"),

  // Verification Audit
  verificationAuditCard: document.getElementById("verificationAuditCard"),
  auditVerdictBadge: document.getElementById("auditVerdictBadge"),
  auditHeadline: document.getElementById("auditHeadline"),
  auditVerdictExplanation: document.getElementById("auditVerdictExplanation"),
  auditChecksListContainer: document.getElementById("auditChecksListContainer"),
  auditMethodology: document.getElementById("auditMethodology"),

  whyDrawerCard: document.getElementById("whyDrawerCard"),
  whyDrawerToggle: document.getElementById("whyDrawerToggle"),
  whyDrawerContent: document.getElementById("whyDrawerContent"),
  whyDrawerArrow: document.getElementById("whyDrawerArrow"),
  explanationText: document.getElementById("explanationText"),
  recommendationsList: document.getElementById("recommendationsList"),

  // Buttons
  viewFullAnalysisBtn: document.getElementById("viewFullAnalysisBtn"),
  scanAgainBtn: document.getElementById("scanAgainBtn"),

  // Error View
  errorTitle: document.getElementById("errorTitle"),
  errorMessage: document.getElementById("errorMessage"),
  errorDetails: document.getElementById("errorDetails"),
  errorRetryBtn: document.getElementById("errorRetryBtn"),
};

/**
 * Switch view panels with fade animation.
 */
function switchView(targetView) {
  if (targetView !== "extension") {
    lastActiveScannerView = targetView;
    if (elements.tabScannerBtn) elements.tabScannerBtn.classList.add("active");
    if (elements.tabExtensionBtn) elements.tabExtensionBtn.classList.remove("active");
  } else {
    if (elements.tabScannerBtn) elements.tabScannerBtn.classList.remove("active");
    if (elements.tabExtensionBtn) elements.tabExtensionBtn.classList.add("active");
  }

  Object.values(views).forEach((v) => {
    if (v) v.classList.remove("active");
  });
  if (views[targetView]) {
    views[targetView].classList.add("active");
  }
}

/**
 * Check backend health on startup.
 */
async function checkBackendHealth() {
  for (const baseUrl of API_BASE_URLS) {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 1500);
      const res = await fetch(`${baseUrl}/api/health`, { credentials: "omit", signal: controller.signal });
      clearTimeout(timeoutId);
      if (res.ok) {
        activeBackendUrl = baseUrl;
        elements.statusPill.classList.remove("offline");
        elements.statusText.textContent = "● LIVE";
        elements.statusPill.title = `FastAPI Engine: ${baseUrl}`;
        return true;
      }
    } catch (e) {
      // Try next
    }
  }

  // Fallback ping to root
  for (const baseUrl of API_BASE_URLS) {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 1500);
      const res = await fetch(`${baseUrl}/`, { credentials: "omit", signal: controller.signal });
      clearTimeout(timeoutId);
      if (res.ok) {
        activeBackendUrl = baseUrl;
        elements.statusPill.classList.remove("offline");
        elements.statusText.textContent = "● LIVE";
        return true;
      }
    } catch (e) {
      // Continue
    }
  }

  elements.statusPill.classList.add("offline");
  elements.statusText.textContent = "● OFFLINE";
  elements.statusPill.title = "FastAPI backend unreachable on port 8001";
  return false;
}

/**
 * Evaluates whether a browser tab can be scripted and analyzed.
 * Detects internal browser URLs, error pages, extension pages, and unreachable frames.
 */
function analyzeTabEligibility(tab) {
  if (!tab || !tab.id) {
    return {
      eligible: false,
      reason: "NO_TAB",
      badge: "NO TAB",
      title: "No Active Tab Detected",
      desc: "Please focus a web browser tab with an active webpage.",
    };
  }

  const url = (tab.url || "").trim();
  const title = (tab.title || "").trim();
  const lowerUrl = url.toLowerCase();
  const lowerTitle = title.toLowerCase();

  // 1. Detect Chrome internal error pages (e.g. net::ERR_CONNECTION_REFUSED, DNS error, offline)
  if (
    lowerUrl.startsWith("chrome-error://") ||
    lowerTitle.includes("this site can’t be reached") ||
    lowerTitle.includes("this site can't be reached") ||
    lowerTitle.includes("refused to connect") ||
    lowerTitle.includes("err_connection_") ||
    lowerTitle.includes("err_name_not_resolved") ||
    lowerTitle.includes("dns_probe_") ||
    lowerTitle.includes("problem loading page") ||
    lowerTitle.includes("server not found")
  ) {
    return {
      eligible: false,
      reason: "ERROR_PAGE",
      badge: "PAGE ERROR",
      title: "Target Page Unreachable",
      desc: "The active tab failed to load or is displaying a browser error page. Please make sure the website is running and loaded in your browser.",
    };
  }

  // 2. Detect internal browser and extension management schemes
  if (
    lowerUrl.startsWith("chrome://") ||
    lowerUrl.startsWith("chrome-extension://") ||
    lowerUrl.startsWith("edge://") ||
    lowerUrl.startsWith("about:") ||
    lowerUrl.startsWith("view-source:") ||
    lowerUrl.startsWith("devtools://") ||
    lowerUrl.startsWith("data:") ||
    lowerUrl.includes("chrome.google.com/webstore") ||
    lowerUrl.includes("chromewebstore.google.com")
  ) {
    return {
      eligible: false,
      reason: "RESTRICTED",
      badge: "RESTRICTED",
      title: "Internal Browser Page",
      desc: "Chrome security restricts extensions from inspecting browser settings, internal pages, and the Web Store.",
    };
  }

  // 3. Supported schemes (http, https, file)
  if (!lowerUrl.startsWith("http://") && !lowerUrl.startsWith("https://") && !lowerUrl.startsWith("file://")) {
    return {
      eligible: false,
      reason: "UNSUPPORTED_SCHEME",
      badge: "UNSUPPORTED",
      title: "Unsupported Page Type",
      desc: "Please navigate to a valid web page (http:// or https://) to scan.",
    };
  }

  return {
    eligible: true,
    url: url,
    title: title || "Recruitment Posting",
    badge: "WEB PAGE",
  };
}

/**
 * Initialize current active tab information.
 */
async function initActiveTab() {
  try {
    const tabs = await chrome.tabs.query({ active: true, currentWindow: true });
    if (!tabs || tabs.length === 0) {
      elements.readyJobTitle.textContent = "No active tab detected";
      elements.readyJobUrl.textContent = "Please focus a web page.";
      elements.readyTargetType.textContent = "NO TAB";
      elements.startScanBtn.disabled = true;
      return;
    }

    currentTab = tabs[0];
    const check = analyzeTabEligibility(currentTab);

    elements.readyTargetType.textContent = check.badge;

    if (!check.eligible) {
      elements.readyJobTitle.textContent = check.title;
      elements.readyJobUrl.textContent = check.desc;
      elements.startScanBtn.disabled = true;
      elements.startScanBtn.title = check.desc;
    } else {
      elements.readyJobTitle.textContent = check.title;
      elements.readyJobUrl.textContent = check.url;
      elements.readyJobUrl.title = check.url;
      elements.startScanBtn.disabled = false;
      elements.startScanBtn.title = "Analyze this job posting with HireShield";
    }
  } catch (err) {
    console.warn("Error querying active tab:", err);
    elements.readyJobTitle.textContent = "Target Discovery Failed";
    elements.readyJobUrl.textContent = err.message;
    elements.startScanBtn.disabled = true;
  }
}

/**
 * Extract job posting content from active tab with 3-phase resilience:
 * 1. Message to existing content script (fast path)
 * 2. Programmatic injection of content.js + extraction message
 * 3. Direct inline DOM script execution fallback
 */
async function extractJobContentFromTab(tab) {
  // Update UI step
  setStepState(elements.stageExtract, "running");
  elements.scanStageHeadline.textContent = "Extracting page content from active tab...";

  // 0. Pre-flight check tab eligibility
  const check = analyzeTabEligibility(tab);
  if (!check.eligible) {
    const err = new Error(check.desc);
    err.code = check.reason;
    throw err;
  }

  // Phase 1: Try sending message to existing content script
  try {
    const response = await chrome.tabs.sendMessage(tab.id, { action: "EXTRACT_JOB_CONTENT" });
    if (response && response.success && response.data && response.data.content) {
      setStepState(elements.stageExtract, "done");
      return response.data;
    }
  } catch (msgErr) {
    // Content script is not listening yet (e.g. tab opened before extension was loaded/reloaded)
    // Silently fall through to Phase 2 without generating console warning logs
  }

  // Phase 2: Try programmatic injection of content.js
  try {
    await chrome.scripting.executeScript({
      target: { tabId: tab.id },
      files: ["content.js"],
    });

    const response = await chrome.tabs.sendMessage(tab.id, { action: "EXTRACT_JOB_CONTENT" });
    if (response && response.success && response.data && response.data.content) {
      setStepState(elements.stageExtract, "done");
      return response.data;
    }
  } catch (injectErr) {
    const injectMsg = (injectErr && injectErr.message) || "";

    if (injectMsg.includes("showing error page") || injectMsg.includes("Frame with ID 0")) {
      const err = new Error("The target web page is displaying a browser error page (e.g. connection refused, DNS error, or offline). Please verify the website is online and loaded in your browser.");
      err.code = "ERROR_PAGE";
      throw err;
    }

    if (injectMsg.includes("Cannot access") || injectMsg.includes("restricted") || injectMsg.includes("chrome://")) {
      const err = new Error("Chrome security policies prevent scanning internal browser pages. Please open a job posting on the web.");
      err.code = "RESTRICTED";
      throw err;
    }

    // Otherwise continue to Phase 3 direct execution fallback
  }

  // Phase 3: Direct inline DOM extraction fallback
  try {
    const results = await chrome.scripting.executeScript({
      target: { tabId: tab.id },
      func: () => {
        // Direct DOM extraction
        const url = window.location.href;
        const pageTitle = document.title || "";

        // Find visible job title
        const titleEl = document.querySelector(
          ".job-details-jobs-unified-top-card__job-title, .jobsearch-JobInfoHeader-title, .jd-header-title, [data-test='job-title'], main h1, article h1, h1"
        );
        const title = titleEl ? titleEl.innerText.trim() : pageTitle;

        // Find company
        const compEl = document.querySelector(
          ".job-details-jobs-unified-top-card__company-name, [data-testid='inlineHeader-companyName'], .jd-header-comp-name, [data-test='employer-name'], [itemprop='hiringOrganization'], .company"
        );
        const company = compEl ? compEl.innerText.trim() : "";

        // Find content container or extract body text
        const container = document.querySelector(
          "#job-details, .jobs-description__content, #jobDescriptionText, .job-desc, article, [role='main'], main, .job-description, .description"
        );

        let text = "";
        if (container && container.innerText && container.innerText.trim().length >= 40) {
          text = container.innerText.trim();
        } else {
          // Clone body and remove noisy chrome
          const clone = document.body.cloneNode(true);
          const removeSelectors = "script, style, noscript, svg, nav, footer, header, iframe, button, input, textarea";
          clone.querySelectorAll(removeSelectors).forEach((el) => el.remove());
          text = clone.innerText || clone.textContent || "";
        }

        // Clean whitespace
        text = text.replace(/\r\n/g, "\n").replace(/\t/g, " ").replace(/[ \f\v]+/g, " ");
        text = text.replace(/\n\s*\n\s*\n+/g, "\n\n").trim();

        if (text.length > 95000) {
          text = text.substring(0, 95000) + "\n\n[Content truncated for analysis]";
        }

        return {
          url: url,
          title: title || "Recruitment Posting",
          company: company || "",
          content: text,
          charCount: text.length,
        };
      },
    });

    if (results && results[0] && results[0].result) {
      setStepState(elements.stageExtract, "done");
      return results[0].result;
    }
  } catch (scriptErr) {
    const scriptMsg = (scriptErr && scriptErr.message) || "";
    if (scriptMsg.includes("showing error page") || scriptMsg.includes("Frame with ID 0")) {
      const err = new Error("The target web page is displaying a browser error page (e.g. connection refused, DNS error, or offline). Please verify the website is online and loaded in your browser.");
      err.code = "ERROR_PAGE";
      throw err;
    }
    if (scriptMsg.includes("Cannot access") || scriptMsg.includes("restricted")) {
      const err = new Error("Chrome security policies prevent scanning internal browser pages.");
      err.code = "RESTRICTED";
      throw err;
    }
    throw new Error(`Unable to extract page content: ${scriptMsg}`);
  }

  throw new Error("No readable job description found on the page.");
}

/**
 * Update pipeline step visual state.
 */
function setStepState(el, state) {
  if (!el) return;
  el.classList.remove("done", "running", "waiting");
  el.classList.add(state);
  const icon = el.querySelector(".step-check");
  if (icon) {
    if (state === "done") icon.textContent = "✓";
    else if (state === "running") icon.textContent = "→";
    else icon.textContent = "·";
  }
}

/**
 * Send extracted job content to the FastAPI backend.
 * Tries the modern Hybrid Risk Engine (/api/risk/analyze) first,
 * then gracefully falls back to /api/scanner/analyze-content if needed.
 */
async function sendToBackend(payload) {
  setStepState(elements.stageUrl, "done");
  setStepState(elements.stageNlp, "running");
  elements.scanStageHeadline.textContent = "Evaluating multi-vector risk engine & domain intelligence...";

  // 1. Primary path: POST /api/risk/analyze
  try {
    const riskEndpoint = `${activeBackendUrl}/api/risk/analyze`;
    const riskRes = await fetch(riskEndpoint, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Accept": "application/json",
      },
      body: JSON.stringify({
        url: payload.url || "",
        job_text: payload.content || "",
        company_name: payload.company || "",
        recruiter_email: payload.recruiter_email || "",
        salary: payload.salary || "",
        source: payload.source || "direct",
      }),
    });

    if (riskRes.ok) {
      const riskData = await riskRes.json();
      setStepState(elements.stageNlp, "done");
      setStepState(elements.stageBehavioral, "done");
      setStepState(elements.stageRisk, "done");
      return { ...riskData, is_hybrid_risk_engine: true };
    }
  } catch (riskErr) {
    console.warn("Primary /api/risk/analyze failed, falling back to legacy scanner:", riskErr);
  }

  // 2. Fallback path: POST /api/scanner/analyze-content
  const targetEndpoint = `${activeBackendUrl}/api/scanner/analyze-content`;
  const response = await fetch(targetEndpoint, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Accept": "application/json",
    },
    body: JSON.stringify({
      url: payload.url || "",
      title: payload.title || "",
      company: payload.company || "",
      content: payload.content || "",
    }),
  });

  setStepState(elements.stageNlp, "done");
  setStepState(elements.stageBehavioral, "running");

  if (!response.ok) {
    let errorDetail = "";
    try {
      const errJson = await response.json();
      errorDetail = errJson.detail || JSON.stringify(errJson);
    } catch (e) {
      errorDetail = `Server responded with status ${response.status} (${response.statusText})`;
    }

    const err = new Error(errorDetail);
    err.status = response.status;
    throw err;
  }

  setStepState(elements.stageBehavioral, "done");
  setStepState(elements.stageRisk, "running");
  elements.scanStageHeadline.textContent = "Computing multi-layer risk score...";

  const data = await response.json();
  setStepState(elements.stageRisk, "done");
  return data;
}

/**
 * Render Hybrid Risk Engine results (RED FLAGS, TRUST SIGNALS, WHY? Drawer).
 */
function renderHybridRiskEngine(data) {
  lastAnalysisResult = data;

  // 1. Target Metadata
  elements.resultJobTitle.textContent = currentJobData?.title || "Recruitment Posting";
  elements.resultCompany.textContent = currentJobData?.company || "Undisclosed Company";
  elements.resultUrl.textContent = currentJobData?.url || "N/A";
  elements.resultUrl.title = currentJobData?.url || "";

  elements.resultSourceBadge.textContent = (currentJobData?.source || "BROWSER CLIENT").toUpperCase();
  const isOverride = data.override && data.override.override;
  elements.resultStatusBadge.textContent = isOverride ? "CRITICAL_OVERRIDE" : "ASSESSMENT_COMPLETE";
  elements.resultStatusBadge.classList.remove("incomplete");

  // 2. Risk Score & Level
  const score = data.risk_score;
  const level = (data.risk_level || "LOW").toUpperCase();

  elements.scoreBanner.className = "score-banner";
  elements.resultRiskLevelBadge.className = "risk-level-badge";

  elements.resultScoreValue.textContent = score;
  elements.resultScoreDenom.textContent = "/ 100";
  elements.resultRiskLevelBadge.textContent = level;

  if (level === "CRITICAL") {
    elements.resultRiskLevelBadge.classList.add("level-critical");
    elements.scoreBanner.style.borderColor = "var(--color-critical)";
  } else if (level === "HIGH") {
    elements.resultRiskLevelBadge.classList.add("level-high");
    elements.scoreBanner.style.borderColor = "var(--color-orange)";
  } else if (level === "MODERATE" || level === "MEDIUM") {
    elements.resultRiskLevelBadge.classList.add("level-medium");
    elements.scoreBanner.style.borderColor = "var(--color-yellow)";
  } else {
    elements.resultRiskLevelBadge.classList.add("level-low");
    elements.scoreBanner.style.borderColor = "var(--color-green)";
  }

  const confPercent = Math.round((data.confidence || 0.8) * 100);
  elements.resultScoreSubtext.textContent = `Confidence: ${confPercent}% • ${data.signals?.length || 0} indicators detected`;

  // 3. Analysis Layers Breakdown
  const analysis = data.analysis || {};
  renderLayer("valBehavioral", "barBehavioral", analysis.nlp?.score || 0, true);
  renderLayer("valLinguistic", "barLinguistic", analysis.impersonation?.score || 0, true);
  renderLayer("valStructural", "barStructural", analysis.company?.score || 0, true);
  renderLayer("valTechnical", "barTechnical", analysis.domain?.score || 0, true);

  // 4. RED FLAGS Section
  const signals = data.signals || [];
  if (elements.redFlagsListContainer) {
    elements.redFlagsListContainer.innerHTML = "";
    if (signals.length > 0) {
      if (elements.redFlagsCountBadge) elements.redFlagsCountBadge.textContent = `${signals.length} DETECTED`;
      signals.forEach((sig) => {
        const card = document.createElement("div");
        const sev = (sig.severity || "high").toLowerCase();
        card.className = `signal-card ${sev}`;

        const topRow = document.createElement("div");
        topRow.className = "signal-top-row";

        const name = document.createElement("div");
        name.className = "signal-name";
        name.innerHTML = `<span style="margin-right: 4px;">${sev === "critical" ? "🛑" : "⚠️"}</span> ${escapeHtml(sig.title || "Risk Flag")}`;

        const tag = document.createElement("span");
        tag.className = "signal-severity-tag";
        tag.textContent = `${sev.toUpperCase()} (+${sig.score || 0})`;
        tag.style.background = sev === "critical" ? "rgba(220, 38, 38, 0.2)" : "rgba(249, 115, 22, 0.2)";
        tag.style.color = sev === "critical" ? "#fca5a5" : "#fdba74";

        topRow.appendChild(name);
        topRow.appendChild(tag);
        card.appendChild(topRow);

        if (sig.description) {
          const desc = document.createElement("div");
          desc.className = "signal-evidence";
          desc.textContent = sig.description;
          card.appendChild(desc);
        }

        if (sig.evidence) {
          const ev = document.createElement("div");
          ev.className = "signal-impact";
          ev.textContent = `Evidence: "${sig.evidence}"`;
          card.appendChild(ev);
        }

        elements.redFlagsListContainer.appendChild(card);
      });
    } else {
      if (elements.redFlagsCountBadge) elements.redFlagsCountBadge.textContent = "0 DETECTED";
      const cleanCard = document.createElement("div");
      cleanCard.className = "signal-card clean";
      cleanCard.innerHTML = `<div class="signal-top-row"><div class="signal-name" style="color: var(--color-green);">✓ No active recruitment fraud flags identified</div></div>`;
      elements.redFlagsListContainer.appendChild(cleanCard);
    }
  }

  // 5. TRUST SIGNALS Section
  const trustSignals = data.positive_signals || [];
  if (elements.trustSignalsListContainer) {
    elements.trustSignalsListContainer.innerHTML = "";
    if (trustSignals.length > 0) {
      if (elements.trustSignalsCountBadge) elements.trustSignalsCountBadge.textContent = `${trustSignals.length} VERIFIED`;
      trustSignals.forEach((ts) => {
        const item = document.createElement("div");
        item.className = "trust-item";
        item.innerHTML = `<span class="trust-icon">🟢</span><span class="trust-text">${escapeHtml(ts)}</span>`;
        elements.trustSignalsListContainer.appendChild(item);
      });
    } else {
      if (elements.trustSignalsCountBadge) elements.trustSignalsCountBadge.textContent = "0 RECORDED";
      const item = document.createElement("div");
      item.className = "trust-item";
      item.innerHTML = `<span class="trust-icon" style="color: #64748b;">○</span><span class="trust-text">No verified trust badges registered for this domain</span>`;
      elements.trustSignalsListContainer.appendChild(item);
    }
  }

  // 6. WHY? Expandable Drawer & Recommendations
  if (elements.explanationText) {
    elements.explanationText.textContent = data.summary || "Full hybrid multi-vector intelligence assessment complete.";
  }

  if (elements.recommendationsList) {
    elements.recommendationsList.innerHTML = "";
    const recs = data.recommendations || [];
    recs.forEach((rec) => {
      const li = document.createElement("li");
      li.textContent = rec;
      elements.recommendationsList.appendChild(li);
    });
  }

  // 7. VERIFICATION AUDIT (Why Real / Fake, What Checked & How Verified)
  renderVerificationAudit(data.verification_audit);

  switchView("results");
}

/**
 * Escapes HTML characters to prevent XSS.
 */
function escapeHtml(str) {
  if (!str) return "";
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

/**
 * Render the Verification Audit card:
 * Explaining Why the job is REAL or FAKE, What we checked, and How it was verified.
 */
function renderVerificationAudit(audit) {
  if (!elements.verificationAuditCard) return;

  if (!audit) {
    elements.verificationAuditCard.style.display = "none";
    return;
  }

  elements.verificationAuditCard.style.display = "block";

  // Headline & Verdict
  if (elements.auditHeadline) {
    elements.auditHeadline.textContent = audit.headline || "Job Verification Breakdown";
  }

  const verdict = (audit.verdict || "UNVERIFIED").toUpperCase();
  if (elements.auditVerdictBadge) {
    elements.auditVerdictBadge.textContent = verdict.replace(/_/g, " ");
    elements.auditVerdictBadge.className = "section-badge-count";

    if (verdict.includes("REAL")) {
      elements.auditVerdictBadge.classList.add("green");
      elements.verificationAuditCard.style.borderLeftColor = "#10b981";
    } else if (verdict.includes("FAKE") || verdict.includes("SCAM")) {
      elements.auditVerdictBadge.classList.add("red");
      elements.verificationAuditCard.style.borderLeftColor = "#ef4444";
    } else {
      elements.auditVerdictBadge.classList.add("yellow");
      elements.verificationAuditCard.style.borderLeftColor = "#f59e0b";
    }
  }

  if (elements.auditVerdictExplanation) {
    elements.auditVerdictExplanation.textContent = audit.verdict_explanation || "";
  }

  // 6 Pillar Checks List
  if (elements.auditChecksListContainer) {
    elements.auditChecksListContainer.innerHTML = "";
    const checks = audit.checks_performed || [];

    const pillarIcons = {
      "domain": "🌐",
      "employer": "🏢",
      "recruiter": "✉️",
      "payment": "💳",
      "identity": "🔒",
      "salary": "📊"
    };

    checks.forEach((chk) => {
      const item = document.createElement("div");
      const statusLower = (chk.status || "caution").toLowerCase();
      item.className = `audit-check-item ${statusLower}`;

      // Pick pillar icon
      let icon = "🛡️";
      const pLower = (chk.pillar || "").toLowerCase();
      for (const [key, ic] of Object.entries(pillarIcons)) {
        if (pLower.includes(key)) {
          icon = ic;
          break;
        }
      }

      item.innerHTML = `
        <div class="audit-check-header">
          <span class="audit-pillar-name">${icon} ${escapeHtml(chk.pillar || "Security Pillar")}</span>
          <span class="audit-status-badge ${statusLower}">${escapeHtml(chk.status || "CAUTION")}</span>
        </div>
        <div class="audit-detail-block">
          <div class="audit-detail-row">
            <span class="audit-detail-label">Checked:</span>
            <span class="audit-detail-text">${escapeHtml(chk.what_we_checked || "")}</span>
          </div>
          <div class="audit-detail-row">
            <span class="audit-detail-label">Verified:</span>
            <span class="audit-detail-text">${escapeHtml(chk.how_verified || "")}</span>
          </div>
          <div class="audit-detail-finding">
            <strong>Result:</strong> ${escapeHtml(chk.finding || "")}
          </div>
        </div>
      `;
      elements.auditChecksListContainer.appendChild(item);
    });
  }

  if (elements.auditMethodology) {
    elements.auditMethodology.textContent = audit.verification_methodology || "Multi-vector cross-referencing across DNS, WHOIS, TLS, NLP heuristics, and enterprise ATS platform whitelists.";
  }
}

/**
 * Render complete recruitment risk assessment response in UI.
 */
function renderResults(data) {
  lastAnalysisResult = data;

  if (data && data.is_hybrid_risk_engine) {
    renderHybridRiskEngine(data);
    return;
  }

  // 1. Target Metadata
  const job = data.job || {};
  elements.resultJobTitle.textContent = job.title || currentJobData?.title || "Recruitment Posting";
  elements.resultCompany.textContent = job.company || currentJobData?.company || "Undisclosed Company";
  elements.resultUrl.textContent = data.url || currentJobData?.url || "N/A";
  elements.resultUrl.title = data.url || "";

  // Content Source & Assessment Status
  elements.resultSourceBadge.textContent = data.layers?.content?.source === "browser_fallback"
    ? "BROWSER FALLBACK"
    : (data.content_intelligence?.source || "BROWSER CLIENT").toUpperCase();

  const assessmentStatus = data.risk_assessment_status || "RISK_ASSESSMENT_COMPLETE";
  elements.resultStatusBadge.textContent = assessmentStatus;
  if (assessmentStatus === "INCOMPLETE") {
    elements.resultStatusBadge.classList.add("incomplete");
  } else {
    elements.resultStatusBadge.classList.remove("incomplete");
  }

  // 2. Risk Score & Level Handling (Strictly preserving backend semantics)
  const isContentAnalyzed = data.content_analyzed !== false;
  const isBlocked = data.fetch_status === "FETCH_BLOCKED";
  const rawScore = data.risk_score;
  const riskLevel = (data.risk_level || "INCOMPLETE").toUpperCase();

  // Reset level classes
  elements.scoreBanner.className = "score-banner";
  elements.resultRiskLevelBadge.className = "risk-level-badge";

  if (!isContentAnalyzed || isBlocked || rawScore === null || rawScore === undefined) {
    // INCOMPLETE / LIMITED ACCESS STATE
    elements.resultScoreValue.textContent = "N/A";
    elements.resultScoreDenom.textContent = "";
    elements.resultRiskLevelBadge.textContent = isBlocked ? "PAGE ACCESS LIMITED" : "INCOMPLETE";
    elements.resultRiskLevelBadge.classList.add("level-incomplete");
    elements.resultScoreSubtext.textContent = "Insufficient page content for full assessment • Layer B pending";
  } else {
    // COMPLETE RISK SCORE (0 to 100)
    elements.resultScoreValue.textContent = rawScore;
    elements.resultScoreDenom.textContent = "/ 100";
    elements.resultRiskLevelBadge.textContent = riskLevel;

    // Apply color theme according to risk level
    if (riskLevel === "CRITICAL") {
      elements.resultRiskLevelBadge.classList.add("level-critical");
      elements.scoreBanner.style.borderColor = "var(--color-critical)";
    } else if (riskLevel === "HIGH") {
      elements.resultRiskLevelBadge.classList.add("level-high");
      elements.scoreBanner.style.borderColor = "var(--color-orange)";
    } else if (riskLevel === "MEDIUM") {
      elements.resultRiskLevelBadge.classList.add("level-medium");
      elements.scoreBanner.style.borderColor = "var(--color-yellow)";
    } else {
      // LOW (0 - 24)
      elements.resultRiskLevelBadge.classList.add("level-low");
      elements.scoreBanner.style.borderColor = "var(--color-green)";
    }

    elements.resultScoreSubtext.textContent = "Composite recruitment risk from Layer A + B analysis";
  }

  // 3. Analysis Layers Breakdown
  const scores = data.scores || {};
  renderLayer("valBehavioral", "barBehavioral", scores.behavioral, isContentAnalyzed);
  renderLayer("valLinguistic", "barLinguistic", scores.linguistic, isContentAnalyzed);
  renderLayer("valStructural", "barStructural", scores.structural, isContentAnalyzed);
  renderLayer("valTechnical", "barTechnical", scores.technical, true); // Technical Layer A always available

  // 4. Risk Signals
  const redFlags = data.red_flags || [];
  elements.signalsListContainer.innerHTML = "";

  if (redFlags.length > 0) {
    elements.signalsCountBadge.textContent = `${redFlags.length} DETECTED`;
    elements.signalsCountBadge.style.color = "var(--color-critical)";

    redFlags.forEach((flag) => {
      const card = document.createElement("div");
      const severity = (flag.severity || "high").toLowerCase();
      card.className = `signal-card ${severity}`;

      const topRow = document.createElement("div");
      topRow.className = "signal-top-row";

      const name = document.createElement("div");
      name.className = "signal-name";
      name.innerHTML = `<span style="margin-right: 4px;">${severity === "critical" ? "🛑" : "⚠️"}</span> ${escapeHtml(flag.message || "Risk Signal Detected")}`;

      const tag = document.createElement("span");
      tag.className = "signal-severity-tag";
      tag.textContent = severity;
      tag.style.background = severity === "critical" ? "rgba(220, 38, 38, 0.2)" : "rgba(249, 115, 22, 0.2)";
      tag.style.color = severity === "critical" ? "#fca5a5" : "#fdba74";

      topRow.appendChild(name);
      topRow.appendChild(tag);
      card.appendChild(topRow);

      if (flag.evidence) {
        const evidence = document.createElement("div");
        evidence.className = "signal-evidence";
        evidence.textContent = flag.evidence;
        card.appendChild(evidence);
      }

      if (flag.impact) {
        const impact = document.createElement("div");
        impact.className = "signal-impact";
        impact.textContent = `Impact: ${flag.impact}`;
        card.appendChild(impact);
      }

      elements.signalsListContainer.appendChild(card);
    });
  } else {
    // Clean / No Signals Detected
    elements.signalsCountBadge.textContent = "0 DETECTED";
    elements.signalsCountBadge.style.color = "var(--color-green)";

    const cleanCard = document.createElement("div");
    cleanCard.className = "signal-card clean";
    cleanCard.innerHTML = `
      <div class="signal-top-row">
        <div class="signal-name" style="color: var(--color-green);">✓ No recruitment fraud indicators detected</div>
      </div>
      <div class="signal-evidence">Heuristic NLP detected no payment demands, credential solicitation, or artificial coercion.</div>
    `;
    elements.signalsListContainer.appendChild(cleanCard);

    // If HTTPS is verified, show positive signal
    const tech = data.technical_checks || {};
    if (tech.is_https) {
      const httpsCard = document.createElement("div");
      httpsCard.className = "signal-card clean";
      httpsCard.innerHTML = `
        <div class="signal-top-row">
          <div class="signal-name" style="color: var(--color-blue);">✓ HTTPS Transport Verified</div>
        </div>
        <div class="signal-evidence">Secure TLS encryption confirmed on target domain.</div>
      `;
      elements.signalsListContainer.appendChild(httpsCard);
    }
  }

  // 5. Explanation
  elements.explanationText.textContent = data.explanation || "Risk assessment completed successfully.";

  // 6. Verification Audit
  renderVerificationAudit(data.verification_audit);

  // Switch to Results View
  switchView("results");
}

/**
 * Render individual layer score and progress bar.
 */
function renderLayer(valId, barId, score, isAnalyzed) {
  const valEl = elements[valId];
  const barEl = elements[barId];
  if (!valEl || !barEl) return;

  if (!isAnalyzed || score === null || score === undefined) {
    valEl.textContent = "UNAVAILABLE";
    valEl.style.color = "var(--text-muted)";
    barEl.style.width = "0%";
    return;
  }

  if (typeof score === "number") {
    valEl.textContent = `${score}%`;
    barEl.style.width = `${Math.min(100, Math.max(0, score))}%`;
    if (score >= 50) {
      valEl.style.color = "var(--color-orange)";
      barEl.classList.add("high");
    } else {
      valEl.style.color = "var(--color-blue)";
      barEl.classList.remove("high");
    }
  } else {
    valEl.textContent = "ANALYZED";
    valEl.style.color = "var(--color-green)";
    barEl.style.width = "100%";
  }
}

/**
 * Render structured error message in error view.
 */
function showError(err) {
  switchView("error");

  const status = err.status;
  const code = err.code;
  const msg = err.message || "";

  if (code === "ERROR_PAGE" || msg.includes("showing error page") || msg.includes("Frame with ID 0")) {
    elements.errorTitle.textContent = "PAGE UNREACHABLE";
    elements.errorMessage.textContent = "The active browser tab is displaying an error or failed to load (e.g. connection refused, DNS error, or offline).";
    elements.errorDetails.textContent = `Target: ${currentTab?.url || "Unknown URL"}\n\nTroubleshooting:\n1. Verify the target website or local dev server is running.\n2. Reload the page in Chrome.\n3. Click Retry Analysis.`;
  } else if (code === "RESTRICTED" || msg.includes("restricted") || msg.includes("Cannot access")) {
    elements.errorTitle.textContent = "RESTRICTED PAGE";
    elements.errorMessage.textContent = "Chrome security restricts extensions from inspecting browser system pages and the Web Store.";
    elements.errorDetails.textContent = `Target: ${currentTab?.url || "Restricted URL"}\n\nPlease navigate to a public job board or job posting (e.g. LinkedIn, Indeed, Naukri) and scan.`;
  } else if (!status || msg.includes("Failed to fetch") || msg.includes("NetworkError") || msg.includes("net::ERR_CONNECTION_REFUSED")) {
    elements.errorTitle.textContent = "BACKEND OFFLINE";
    elements.errorMessage.textContent = "HireShield could not connect to the analysis server. Make sure the FastAPI backend is running.";
    elements.errorDetails.textContent = `Target: ${activeBackendUrl}/api/scanner/analyze-content\nRun command: uvicorn app.main:app --port 8001`;
  } else if (status === 422) {
    elements.errorTitle.textContent = "INSUFFICIENT PAGE CONTENT";
    elements.errorMessage.textContent = msg || "Submitted content is too brief or invalid. Please ensure a complete visible job description is open on screen.";
    elements.errorDetails.textContent = `HTTP 422 Unprocessable Content: ${msg}`;
  } else if (status === 403) {
    elements.errorTitle.textContent = "ACCESS RESTRICTED";
    elements.errorMessage.textContent = "Access to the requested endpoint was denied by backend security policies.";
    elements.errorDetails.textContent = `HTTP 403 Forbidden: ${msg}`;
  } else {
    elements.errorTitle.textContent = `ANALYSIS ERROR (${status || "CLIENT"})`;
    elements.errorMessage.textContent = msg || "An unexpected error occurred while analyzing the job posting.";
    elements.errorDetails.textContent = err.stack || err.toString();
  }
}

/**
 * Execute full scan pipeline.
 */
async function runAnalysis() {
  try {
    switchView("scanning");

    // Reset steps
    setStepState(elements.stageExtract, "waiting");
    setStepState(elements.stageUrl, "waiting");
    setStepState(elements.stageNlp, "waiting");
    setStepState(elements.stageBehavioral, "waiting");
    setStepState(elements.stageRisk, "waiting");

    // 1. Query fresh active browser tab
    const tabs = await chrome.tabs.query({ active: true, currentWindow: true });
    if (!tabs || tabs.length === 0) {
      const err = new Error("No active browser tab found. Please focus a web browser window.");
      err.code = "NO_TAB";
      throw err;
    }
    currentTab = tabs[0];

    // 2. Pre-check tab eligibility
    const check = analyzeTabEligibility(currentTab);
    if (!check.eligible) {
      const err = new Error(check.desc);
      err.code = check.reason;
      throw err;
    }

    // 3. Extract DOM content
    currentJobData = await extractJobContentFromTab(currentTab);

    // Validate minimum content size before sending
    if (!currentJobData.content || currentJobData.content.trim().length < 15) {
      const err = new Error("The visible job description text is too brief (< 15 characters) to evaluate. Please navigate directly to the job details page.");
      err.status = 422;
      throw err;
    }

    // 4. Send to FastAPI backend
    const result = await sendToBackend(currentJobData);

    // Save active analysis result with full metadata and persistent ID
    lastAnalysisResult = {
      ...result,
      url: currentJobData?.url || currentTab?.url || "",
      title: currentJobData?.title || "",
      company: currentJobData?.company || "",
    };

    // 5. Render response
    renderResults(result);

  } catch (err) {
    console.warn("Scan pipeline notice:", err.message);
    showError(err);
  }
}

/**
 * Open the web application's full risk analysis page and copy target website URL to clipboard.
 * Preserves the exact scan ID so the web platform displays the identical risk score.
 */
async function openFullAnalysis() {
  const scanId = lastAnalysisResult?.id || lastAnalysisResult?.candidate_id;
  let targetUrl = lastAnalysisResult?.url || currentJobData?.url || currentTab?.url || "";

  if (!targetUrl) {
    try {
      const tabs = await chrome.tabs.query({ active: true, currentWindow: true });
      if (tabs && tabs[0]) {
        targetUrl = tabs[0].url || "";
      }
    } catch (e) {
      console.warn("Could not query active tab:", e);
    }
  }

  // Copy target website link to user's clipboard
  if (targetUrl) {
    try {
      await navigator.clipboard.writeText(targetUrl);
      console.log("Copied target job URL to clipboard:", targetUrl);
    } catch (err) {
      // Fallback copy mechanism
      try {
        const tempInput = document.createElement("textarea");
        tempInput.value = targetUrl;
        tempInput.style.position = "fixed";
        tempInput.style.opacity = "0";
        document.body.appendChild(tempInput);
        tempInput.select();
        document.execCommand("copy");
        document.body.removeChild(tempInput);
      } catch (fallbackErr) {
        console.warn("Clipboard copy fallback error:", fallbackErr);
      }
    }

    // Temporary button visual feedback
    if (elements.viewFullAnalysisBtn) {
      const originalContent = elements.viewFullAnalysisBtn.innerHTML;
      elements.viewFullAnalysisBtn.innerHTML = `<span>✓ LINK COPIED &bull; OPENING...</span>`;
      setTimeout(() => {
        if (elements.viewFullAnalysisBtn) {
          elements.viewFullAnalysisBtn.innerHTML = originalContent;
        }
      }, 2000);
    }
  }

  let fullUrl;
  if (scanId) {
    // Navigate directly to the evaluated dossier ID so the score is 100% identical
    fullUrl = `${WEB_APP_URL}/${scanId}?url=${encodeURIComponent(targetUrl)}`;
  } else if (targetUrl) {
    fullUrl = `${WEB_APP_URL}?url=${encodeURIComponent(targetUrl)}`;
  } else {
    fullUrl = WEB_APP_URL;
  }
  chrome.tabs.create({ url: fullUrl });
}

/**
 * Escape HTML to prevent injection in dynamic elements.
 */
function escapeHtml(str) {
  if (!str) return "";
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

// ==========================================================================
// Event Listeners
// ==========================================================================
document.addEventListener("DOMContentLoaded", async () => {
  // Start health check and tab discovery in parallel
  checkBackendHealth();
  await initActiveTab();

  // Button actions
  if (elements.startScanBtn) {
    elements.startScanBtn.addEventListener("click", runAnalysis);
  }

  if (elements.scanAgainBtn) {
    elements.scanAgainBtn.addEventListener("click", runAnalysis);
  }

  if (elements.errorRetryBtn) {
    elements.errorRetryBtn.addEventListener("click", runAnalysis);
  }

  if (elements.viewFullAnalysisBtn) {
    elements.viewFullAnalysisBtn.addEventListener("click", openFullAnalysis);
  }

  // Why Drawer accordion toggle
  if (elements.whyDrawerToggle) {
    elements.whyDrawerToggle.addEventListener("click", () => {
      if (elements.whyDrawerContent) {
        const isHidden = elements.whyDrawerContent.style.display === "none" || !elements.whyDrawerContent.style.display;
        elements.whyDrawerContent.style.display = isHidden ? "block" : "none";
        if (elements.whyDrawerArrow) {
          elements.whyDrawerArrow.classList.toggle("open", isHidden);
        }
      }
    });
  }

  // Extension tab and Add to Browser actions
  if (elements.tabScannerBtn) {
    elements.tabScannerBtn.addEventListener("click", () => {
      switchView(lastActiveScannerView || "ready");
    });
  }

  if (elements.tabExtensionBtn) {
    elements.tabExtensionBtn.addEventListener("click", () => {
      switchView("extension");
    });
  }

  if (elements.backToScannerBtn) {
    elements.backToScannerBtn.addEventListener("click", () => {
      switchView(lastActiveScannerView || "ready");
    });
  }

  if (elements.openExtensionsPageBtn) {
    elements.openExtensionsPageBtn.addEventListener("click", () => {
      chrome.tabs.create({ url: "chrome://extensions" });
    });
  }
});
