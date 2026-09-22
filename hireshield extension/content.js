/**
 * HireShield Content Script
 * 
 * Extracts visible recruitment and job posting content from the active tab.
 * Uses domain-specific selectors for top job platforms (LinkedIn, Indeed, Naukri, Glassdoor, etc.)
 * with resilient semantic HTML fallbacks.
 */

(function () {
  // Prevent duplicate execution if injected multiple times
  if (window.__hireShieldContentScriptLoaded) {
    return;
  }
  window.__hireShieldContentScriptLoaded = true;

  /**
   * Extract job metadata and visible description text from the current webpage.
   */
  function extractJobData() {
    const url = window.location.href;
    const hostname = window.location.hostname.toLowerCase();

    let title = "";
    let company = "";
    let content = "";

    // 1. Platform-specific title extraction
    const titleSelectors = [
      // LinkedIn
      ".job-details-jobs-unified-top-card__job-title",
      ".jobs-unified-top-card__job-title",
      ".topcard__title",
      "h1.t-24",
      // Indeed
      ".jobsearch-JobInfoHeader-title",
      "h1[data-testid='jobsearch-JobInfoHeader-title']",
      "h1.jobsearch-JobInfoHeader-title",
      // Naukri
      ".jd-header-title",
      "header.styles_header__j_9f9 h1",
      "h1.styles_title__... ",
      // Glassdoor
      "[data-test='job-title']",
      ".job-title",
      // Workday
      "[data-automation-id='jobPostingHeader']",
      // Lever / Greenhouse
      ".posting-headline h2",
      ".app-title",
      "#header h1",
      // Generic semantic tags
      "main h1",
      "article h1",
      "[role='main'] h1",
      "h1",
    ];

    for (const selector of titleSelectors) {
      try {
        const el = document.querySelector(selector);
        if (el && el.innerText && el.innerText.trim().length > 0) {
          title = el.innerText.trim();
          break;
        }
      } catch (e) {
        // Continue to next selector
      }
    }

    if (!title) {
      // Fallback: document title cleaned of platform branding
      const pageTitle = document.title || "";
      title = pageTitle
        .replace(/\s*[-|–—]\s*(LinkedIn|Indeed|Naukri|Glassdoor|ZipRecruiter|Monster|Foundit|Jobs|Careers).*$/i, "")
        .trim();
    }

    // 2. Platform-specific company extraction
    const companySelectors = [
      // LinkedIn
      ".job-details-jobs-unified-top-card__company-name",
      ".jobs-unified-top-card__company-name",
      ".topcard__org-name-link",
      ".jobs-top-card__company-url",
      // Indeed
      "[data-testid='inlineHeader-companyName']",
      ".companyName",
      // Naukri
      ".jd-header-comp-name",
      "a.styles_header-link__... ",
      // Glassdoor
      "[data-test='employer-name']",
      // Workday
      "[data-automation-id='companyName']",
      // Lever / Greenhouse
      ".posting-headline .org",
      ".company-name",
      // Generic schema / microdata
      "[itemprop='hiringOrganization']",
      ".company",
      ".employer",
    ];

    for (const selector of companySelectors) {
      try {
        const el = document.querySelector(selector);
        if (el && el.innerText && el.innerText.trim().length > 0) {
          company = el.innerText.trim();
          break;
        }
      } catch (e) {
        // Continue to next selector
      }
    }

    if (!company) {
      // Check OpenGraph site_name or parse domain
      const ogSite = document.querySelector("meta[property='og:site_name']");
      if (ogSite && ogSite.content) {
        company = ogSite.content.trim();
      } else {
        // Derive clean brand name from domain
        company = hostname.replace(/^www\./, "").split(".")[0];
        company = company.charAt(0).toUpperCase() + company.slice(1);
      }
    }

    // 3. Platform-specific and semantic content extraction
    const contentSelectors = [
      // LinkedIn
      "#job-details",
      ".jobs-description__content",
      ".jobs-box__html-content",
      // Indeed
      "#jobDescriptionText",
      ".jobsearch-jobDescriptionText",
      // Naukri
      ".job-desc",
      "section.job-desc",
      ".styles_job_desc__... ",
      // Glassdoor
      "#JobDescriptionContainer",
      ".desc",
      // Workday
      "[data-automation-id='jobPostingDescription']",
      // Lever / Greenhouse
      ".section-wrapper.page-full-width",
      ".posting-requirements",
      "#content",
      // Generic semantic containers
      "article",
      "[role='main']",
      "main",
      ".job-description",
      "#job-description",
      ".job-details",
      ".description",
    ];

    for (const selector of contentSelectors) {
      try {
        const el = document.querySelector(selector);
        if (el && el.innerText && el.innerText.trim().length >= 40) {
          content = el.innerText.trim();
          break;
        }
      } catch (e) {
        // Continue to next selector
      }
    }

    // If no dedicated container matched or content is too short, extract clean body text
    if (!content || content.length < 50) {
      content = extractCleanBodyText();
    }

    // Normalize whitespace and clamp within FastAPI limit (100,000 chars)
    content = content.replace(/\r\n/g, "\n").replace(/\t/g, " ").replace(/[ \f\v]+/g, " ");
    content = content.replace(/\n\s*\n\s*\n+/g, "\n\n").trim();

    if (content.length > 95000) {
      content = content.substring(0, 95000) + "\n\n[Content truncated for analysis]";
    }

    // 4. Extract Salary Information
    let salary = "";
    const salarySelectors = [
      ".job-details-jobs-unified-top-card__job-insight",
      ".jobs-unified-top-card__job-insight",
      ".metadata.salary-snippet-container",
      "div[data-testid='attribute_snippets_section']",
      "#salaryInfoAndJobType",
      "[data-test='detailSalary']",
      ".salary-estimate",
      ".jd-header-salary",
      "[itemprop='baseSalary']",
      "[itemprop='estimatedSalary']",
    ];

    for (const selector of salarySelectors) {
      try {
        const el = document.querySelector(selector);
        if (el && el.innerText && /[\$₹€£]|\b(?:usd|inr|lpa|eur|gbp)\b/i.test(el.innerText)) {
          salary = el.innerText.trim();
          break;
        }
      } catch (e) {
        // Continue
      }
    }

    if (!salary) {
      // Regex check in extracted content
      const salaryMatch = content.match(/(?:salary|compensation|pay|ctc|stipend)\s*[:\-]?\s*([$₹€£][\d,]+(?:\s*-\s*[$₹€£]?[\d,]+)?(?:\s*(?:per\s*(?:year|month|hr|hour|day|annum)|lpa|\/yr|\/hr|\/mo))?)/i);
      if (salaryMatch) {
        salary = salaryMatch[0].trim();
      }
    }

    // 5. Extract Recruiter / Contact Email
    let recruiterEmail = "";
    const mailtoEl = document.querySelector("a[href^='mailto:']");
    if (mailtoEl) {
      const href = mailtoEl.getAttribute("href") || "";
      const emailPart = href.replace(/^mailto:/i, "").split("?")[0].trim();
      if (emailPart) recruiterEmail = emailPart;
    }

    if (!recruiterEmail) {
      const emailMatch = content.match(/\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b/);
      if (emailMatch) {
        recruiterEmail = emailMatch[0].trim();
      }
    }

    // 6. Detect Platform Source
    let source = "direct";
    if (hostname.includes("linkedin")) source = "linkedin";
    else if (hostname.includes("indeed")) source = "indeed";
    else if (hostname.includes("naukri")) source = "naukri";
    else if (hostname.includes("glassdoor")) source = "glassdoor";
    else if (hostname.includes("wellfound")) source = "wellfound";
    else if (hostname.includes("greenhouse")) source = "greenhouse";
    else if (hostname.includes("lever")) source = "lever";

    return {
      url: url,
      title: title || "Recruitment Posting",
      company: company || "Undisclosed Company",
      content: content,
      salary: salary,
      recruiter_email: recruiterEmail,
      source: source,
      charCount: content.length,
      timestamp: new Date().toISOString(),
    };
  }

  /**
   * Fallback extractor: reads visible body text while stripping navigation, footers, and scripts.
   */
  function extractCleanBodyText() {
    const clone = document.body.cloneNode(true);

    // Remove noise elements
    const unwanted = clone.querySelectorAll(
      "script, style, noscript, svg, nav, footer, header, iframe, button, input, select, textarea, [aria-hidden='true']"
    );
    unwanted.forEach((el) => el.remove());

    return clone.innerText || clone.textContent || "";
  }

  // Listen for messages from popup
  chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request && request.action === "PING") {
      sendResponse({ success: true, status: "PONG" });
      return true;
    }
    if (request && request.action === "EXTRACT_JOB_CONTENT") {
      try {
        const data = extractJobData();
        sendResponse({ success: true, data: data });
      } catch (err) {
        sendResponse({ success: false, error: err.message });
      }
      return true;
    }
    return false;
  });

  // Expose on window for direct chrome.scripting.executeScript fallback
  window.__hireShieldExtractJobData = extractJobData;
})();
