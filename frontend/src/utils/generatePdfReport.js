import jsPDF from 'jspdf';
import autoTable from 'jspdf-autotable';

/**
 * Formats a date or timestamp into a readable format.
 */
function formatDate(dateInput) {
  try {
    const d = dateInput ? new Date(dateInput) : new Date();
    return d.toLocaleString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: true,
    });
  } catch {
    return new Date().toISOString();
  }
}

/**
 * Returns color RGB values for a given risk level.
 */
function getRiskColor(level) {
  const norm = String(level || '').toUpperCase();
  if (norm === 'CRITICAL') return { rgb: [239, 68, 68], bg: [254, 242, 242], text: '#EF4444' };
  if (norm === 'HIGH') return { rgb: [249, 115, 22], bg: [255, 247, 237], text: '#F97316' };
  if (norm === 'MEDIUM') return { rgb: [234, 179, 8], bg: [254, 252, 232], text: '#EAB308' };
  if (norm === 'LOW') return { rgb: [16, 185, 129], bg: [236, 253, 245], text: '#10B981' };
  return { rgb: [100, 116, 139], bg: [241, 245, 249], text: '#64748B' }; // Incomplete / default
}

/**
 * Generates and downloads an executive PDF Security Audit Report.
 * @param {Object} report The candidate or scan report data.
 */
export function generatePdfReport(report) {
  if (!report) {
    console.error('Cannot generate PDF: report data is missing');
    return;
  }

  const doc = new jsPDF({
    orientation: 'portrait',
    unit: 'mm',
    format: 'a4',
  });

  const pageWidth = doc.internal.pageSize.getWidth();
  const pageHeight = doc.internal.pageSize.getHeight();
  const margin = 14;
  const contentWidth = pageWidth - margin * 2;

  const reportId = report.id || `HS-${new Date().getFullYear()}-${Math.floor(100000 + Math.random() * 900000)}`;
  const candidateOrTitle = report.candidateName || report.job?.title || report.title || 'Target Job Dossier';
  const company = report.job?.company || report.company || 'Not Specified / Unverified';
  const targetUrl = report.final_url || report.url || 'Not Provided';
  const riskScore = report.risk_score !== null && report.risk_score !== undefined ? report.risk_score : 'N/A';
  const riskLevel = (report.risk_level || (report.content_analyzed ? 'LOW' : 'INCOMPLETE')).toUpperCase();
  const verdict = report.verdict ? report.verdict.replace(/_/g, ' ') : (report.risk_score > 60 ? 'HIGH RISK' : 'LOW RISK');
  const riskColors = getRiskColor(riskLevel);

  let cursorY = 0;

  // -------------------------------------------------------------
  // 1. TOP HEADER BANNER (HireShield Cyber Dark Style)
  // -------------------------------------------------------------
  doc.setFillColor(15, 23, 42); // slate-900
  doc.rect(0, 0, pageWidth, 38, 'F');

  // Accent Line
  doc.setFillColor(riskColors.rgb[0], riskColors.rgb[1], riskColors.rgb[2]);
  doc.rect(0, 37, pageWidth, 1.5, 'F');

  // Logo / Shield icon symbol
  doc.setFillColor(riskColors.rgb[0], riskColors.rgb[1], riskColors.rgb[2]);
  doc.roundedRect(margin, 8, 8, 8, 1.5, 1.5, 'F');
  doc.setTextColor(255, 255, 255);
  doc.setFont('helvetica', 'bold');
  doc.setFontSize(8);
  doc.text('HS', margin + 1.8, 13.5);

  // Title & Subtitle
  doc.setFont('helvetica', 'bold');
  doc.setFontSize(14);
  doc.setTextColor(255, 255, 255);
  doc.text('HIRESHIELD INTELLIGENCE PLATFORM', margin + 12, 12);

  doc.setFont('helvetica', 'normal');
  doc.setFontSize(8);
  doc.setTextColor(148, 163, 184); // slate-400
  doc.text('RECRUITMENT THREAT ASSESSMENT & SECURITY AUDIT DOSSIER', margin + 12, 17);

  // Header Right Metadata (Report ID & Date)
  doc.setFont('courier', 'bold');
  doc.setFontSize(8.5);
  doc.setTextColor(255, 255, 255);
  doc.text(`ID: ${reportId}`, pageWidth - margin, 12, { align: 'right' });

  doc.setFont('helvetica', 'normal');
  doc.setFontSize(7.5);
  doc.setTextColor(148, 163, 184);
  doc.text(`Date: ${formatDate(report.scannedAt)}`, pageWidth - margin, 17, { align: 'right' });

  cursorY = 44;

  // -------------------------------------------------------------
  // 2. EXECUTIVE RISK SUMMARY CARD
  // -------------------------------------------------------------
  // Card Background
  doc.setFillColor(248, 250, 252); // slate-50
  doc.setDrawColor(226, 232, 240); // slate-200
  doc.roundedRect(margin, cursorY, contentWidth, 34, 2, 2, 'FD');

  // Left column: Risk Score Badge
  doc.setFillColor(riskColors.bg[0], riskColors.bg[1], riskColors.bg[2]);
  doc.setDrawColor(riskColors.rgb[0], riskColors.rgb[1], riskColors.rgb[2]);
  doc.roundedRect(margin + 4, cursorY + 4, 38, 26, 2, 2, 'FD');

  doc.setFont('helvetica', 'bold');
  doc.setFontSize(18);
  doc.setTextColor(riskColors.rgb[0], riskColors.rgb[1], riskColors.rgb[2]);
  doc.text(String(riskScore), margin + 23, cursorY + 16, { align: 'center' });

  doc.setFont('helvetica', 'bold');
  doc.setFontSize(7);
  doc.text('/ 100 RISK SCORE', margin + 23, cursorY + 21, { align: 'center' });

  doc.setFontSize(7.5);
  doc.text(riskLevel, margin + 23, cursorY + 26, { align: 'center' });

  // Center column: Key Verdict & Status
  const midX = margin + 48;
  doc.setFont('helvetica', 'bold');
  doc.setFontSize(8);
  doc.setTextColor(100, 116, 139);
  doc.text('SECURITY VERDICT:', midX, cursorY + 9);

  doc.setFont('helvetica', 'bold');
  doc.setFontSize(12);
  doc.setTextColor(riskColors.rgb[0], riskColors.rgb[1], riskColors.rgb[2]);
  doc.text(verdict, midX, cursorY + 16);

  doc.setFont('helvetica', 'normal');
  doc.setFontSize(8);
  doc.setTextColor(71, 85, 105);
  const auditMode = report.content_analyzed
    ? 'Full Multi-Layer Heuristic & Infrastructure Assessment'
    : 'Layer A Infrastructure Only (WAF / Access Limited)';
  doc.text(`Audit Scope: ${auditMode}`, midX, cursorY + 22);

  const flagCount = report.red_flags ? report.red_flags.length : 0;
  doc.text(`Threat Flags Detected: ${flagCount} active alert${flagCount === 1 ? '' : 's'}`, midX, cursorY + 27);

  // Right column: Scam Probability & Status
  const rightX = pageWidth - margin - 4;
  doc.setFont('helvetica', 'normal');
  doc.setFontSize(8);
  doc.setTextColor(100, 116, 139);
  doc.text('Scam Probability:', rightX, cursorY + 9, { align: 'right' });

  const prob = report.fake_job_probability !== null && report.fake_job_probability !== undefined
    ? `${report.fake_job_probability}%`
    : (riskScore !== 'N/A' ? `${riskScore}%` : 'N/A');
  doc.setFont('helvetica', 'bold');
  doc.setFontSize(13);
  doc.setTextColor(riskColors.rgb[0], riskColors.rgb[1], riskColors.rgb[2]);
  doc.text(prob, rightX, cursorY + 16, { align: 'right' });

  doc.setFont('helvetica', 'normal');
  doc.setFontSize(7.5);
  doc.setTextColor(100, 116, 139);
  doc.text(`HTTP: ${report.http_status || 200} // ${report.fetch_status || 'COMPLETE'}`, rightX, cursorY + 24, { align: 'right' });

  cursorY += 40;

  // -------------------------------------------------------------
  // 3. TARGET SPECIFICATIONS TABLE
  // -------------------------------------------------------------
  autoTable(doc, {
    startY: cursorY,
    head: [['TARGET DOSSIER SPECIFICATION', 'EXTRACTED ATTRIBUTES']],
    body: [
      ['Target Position / Title', candidateOrTitle],
      ['Company / Employer', company],
      ['Scanned Target URL', targetUrl],
      [
        'Content Source',
        report.content_intelligence?.source === 'browser_fallback'
          ? 'Browser Fallback (User Provided Body Text)'
          : report.content_analyzed
          ? 'Automated HTTPX Engine Extraction'
          : 'Server Access Restricted (WAF Protected)',
      ],
      [
        'Extracted Text Summary',
        report.job?.text_preview
          ? (report.job.text_preview.length > 180 ? `${report.job.text_preview.slice(0, 180)}...` : report.job.text_preview)
          : 'No visible job body preview available.',
      ],
    ],
    margin: { left: margin, right: margin },
    styles: {
      fontSize: 8,
      cellPadding: 2.2,
      lineColor: [226, 232, 240],
      lineWidth: 0.2,
    },
    headStyles: {
      fillColor: [30, 41, 59], // slate-800
      textColor: [255, 255, 255],
      fontStyle: 'bold',
      fontSize: 8,
    },
    columnStyles: {
      0: { fontStyle: 'bold', cellWidth: 50, textColor: [51, 65, 85] },
      1: { textColor: [30, 41, 59] },
    },
    theme: 'grid',
  });

  cursorY = doc.lastAutoTable.finalY + 6;

  // -------------------------------------------------------------
  // 4. LAYER A: INFRASTRUCTURE & TECHNICAL VALIDATION
  // -------------------------------------------------------------
  const tech = report.technical_checks || {};
  const urlIntel = report.url_intelligence || {};

  const isSslValid = tech.ssl_valid === true || urlIntel.ssl_valid === true;
  const isHttps = tech.is_https === true || urlIntel.is_https === true || targetUrl.startsWith('https://');
  const isDnsValid = tech.dns_exists !== false && urlIntel.dns_exists !== false;
  const domainAge = tech.domain_age_days !== null && tech.domain_age_days !== undefined
    ? `${tech.domain_age_days} days (${Math.floor(tech.domain_age_days / 365)} yrs)`
    : 'Not Available / Protected WHOIS';

  autoTable(doc, {
    startY: cursorY,
    head: [['LAYER A: INFRASTRUCTURE CHECK', 'STATUS', 'DETAILS & TELEMETRY']],
    body: [
      [
        'Target Hostname',
        urlIntel.domain || 'Resolved',
        `Evaluated hostname for typo-squatting and suspicious patterns.`,
      ],
      [
        'SSL / TLS Certificate',
        isSslValid ? 'SECURE / VALID' : (tech.ssl_valid === false ? 'INSECURE / INVALID' : 'UNVERIFIED'),
        isSslValid ? 'Trusted certificate authority and active HTTPS handshake verified.' : 'Certificate is invalid, expired, or untrusted.',
      ],
      [
        'Domain Registration Age',
        tech.domain_age_days && tech.domain_age_days < 90 ? 'RECENT (<90d)' : 'ESTABLISHED',
        domainAge,
      ],
      [
        'DNS Resolution',
        isDnsValid ? 'ACTIVE (RESOLVED)' : 'NO DNS RECORD',
        tech.ip ? `Server IP Address: ${tech.ip}` : 'DNS A-Record verified.',
      ],
      [
        'Protocol & Redirect Chain',
        isHttps ? 'HTTPS ENFORCED' : 'UNENCRYPTED HTTP',
        `Redirect hops: ${tech.redirect_count || 0}`,
      ],
    ],
    margin: { left: margin, right: margin },
    styles: {
      fontSize: 7.5,
      cellPadding: 2,
      lineColor: [226, 232, 240],
      lineWidth: 0.2,
    },
    headStyles: {
      fillColor: [30, 41, 59],
      textColor: [255, 255, 255],
      fontStyle: 'bold',
      fontSize: 8,
    },
    columnStyles: {
      0: { fontStyle: 'bold', cellWidth: 50, textColor: [51, 65, 85] },
      1: {
        fontStyle: 'bold',
        cellWidth: 42,
        textColor: [15, 23, 42],
      },
      2: { textColor: [71, 85, 105] },
    },
    theme: 'grid',
    didParseCell: function (data) {
      if (data.section === 'body' && data.column.index === 1) {
        const text = String(data.cell.raw);
        if (text.includes('SECURE') || text.includes('ESTABLISHED') || text.includes('RESOLVED') || text.includes('HTTPS')) {
          data.cell.styles.textColor = [16, 185, 129];
        } else if (text.includes('INSECURE') || text.includes('INVALID') || text.includes('RECENT') || text.includes('UNENCRYPTED')) {
          data.cell.styles.textColor = [239, 68, 68];
        }
      }
    },
  });

  cursorY = doc.lastAutoTable.finalY + 6;

  // Check if we need to advance to page 2 if remaining space is too tight
  if (cursorY > pageHeight - 65) {
    doc.addPage();
    cursorY = 20;
  }

  // -------------------------------------------------------------
  // 5. LAYER B: HEURISTIC RISK BREAKDOWN
  // -------------------------------------------------------------
  const scores = report.scores || {};
  const behavioral = scores.behavioral !== undefined ? `${scores.behavioral}/100` : 'N/A';
  const linguistic = scores.linguistic !== undefined ? `${scores.linguistic}/100` : 'N/A';
  const structural = scores.structural !== undefined ? `${scores.structural}/100` : 'N/A';
  const technical = scores.technical !== undefined ? `${scores.technical}/100` : 'N/A';

  autoTable(doc, {
    startY: cursorY,
    head: [['LAYER B: RISK DIMENSION', 'SCORE', 'WEIGHT', 'EVALUATION FOCUS']],
    body: [
      ['Behavioral Heuristics', behavioral, '40%', 'Advance fees, payment requests, sensitive credential harvesting.'],
      ['Linguistic Analysis', linguistic, '25%', 'Artificial urgency, excessive income guarantees, pressure language.'],
      ['Structural Channels', structural, '20%', 'Informal communication (Telegram, WhatsApp), non-corporate domains.'],
      ['Technical Infrastructure', technical, '15%', 'Domain age, SSL health, DNS validity, redirect chaining.'],
    ],
    margin: { left: margin, right: margin },
    styles: {
      fontSize: 7.5,
      cellPadding: 2,
      lineColor: [226, 232, 240],
      lineWidth: 0.2,
    },
    headStyles: {
      fillColor: [30, 41, 59],
      textColor: [255, 255, 255],
      fontStyle: 'bold',
      fontSize: 8,
    },
    columnStyles: {
      0: { fontStyle: 'bold', cellWidth: 50, textColor: [51, 65, 85] },
      1: { fontStyle: 'bold', cellWidth: 26, halign: 'center' },
      2: { cellWidth: 20, halign: 'center', textColor: [100, 116, 139] },
      3: { textColor: [71, 85, 105] },
    },
    theme: 'grid',
  });

  cursorY = doc.lastAutoTable.finalY + 6;

  if (cursorY > pageHeight - 65) {
    doc.addPage();
    cursorY = 20;
  }

  // -------------------------------------------------------------
  // 6. DETECTED RED FLAGS / THREAT INDICATORS
  // -------------------------------------------------------------
  const redFlags = report.red_flags || [];
  const redFlagRows = redFlags.length > 0
    ? redFlags.map((flag, idx) => {
        if (typeof flag === 'string') {
          return [`FLAG #${idx + 1}`, 'HIGH', flag];
        }
        return [
          (flag.type || `FLAG #${idx + 1}`).toUpperCase(),
          (flag.severity || 'HIGH').toUpperCase(),
          flag.message || flag.description || 'Suspicious recruitment pattern detected.',
        ];
      })
    : [['NONE', 'CLEAN', 'No behavioral or structural red flags detected in target posting.']];

  autoTable(doc, {
    startY: cursorY,
    head: [['SECURITY THREAT INDICATORS (RED FLAGS)', 'SEVERITY', 'OBSERVED BEHAVIOR / EVIDENCE']],
    body: redFlagRows,
    margin: { left: margin, right: margin },
    styles: {
      fontSize: 7.5,
      cellPadding: 2,
      lineColor: [226, 232, 240],
      lineWidth: 0.2,
    },
    headStyles: {
      fillColor: redFlags.length > 0 ? [185, 28, 28] : [30, 41, 59], // red-700 if flags, slate if clean
      textColor: [255, 255, 255],
      fontStyle: 'bold',
      fontSize: 8,
    },
    columnStyles: {
      0: { fontStyle: 'bold', cellWidth: 45, textColor: [51, 65, 85] },
      1: { fontStyle: 'bold', cellWidth: 26, halign: 'center' },
      2: { textColor: [71, 85, 105] },
    },
    theme: 'grid',
    didParseCell: function (data) {
      if (data.section === 'body' && data.column.index === 1) {
        const sev = String(data.cell.raw).toUpperCase();
        if (sev === 'CRITICAL') data.cell.styles.textColor = [220, 38, 38];
        else if (sev === 'HIGH') data.cell.styles.textColor = [234, 88, 12];
        else if (sev === 'MEDIUM') data.cell.styles.textColor = [202, 138, 4];
        else if (sev === 'CLEAN' || sev === 'LOW') data.cell.styles.textColor = [16, 185, 129];
      }
    },
  });

  cursorY = doc.lastAutoTable.finalY + 6;

  if (cursorY > pageHeight - 50) {
    doc.addPage();
    cursorY = 20;
  }

  // -------------------------------------------------------------
  // 7. RECOMMENDATIONS & CANDIDATE DILIGENCE ADVISORY
  // -------------------------------------------------------------
  const recommendations = (report.recommendations && report.recommendations.length > 0)
    ? report.recommendations
    : [
        'Verify recruiter identity on official enterprise careers page or corporate email domain.',
        'Never transfer funds, purchase training packages, or pay processing fees for employment.',
        'Protect personal identifiable information (PII) including bank details, SSN, or national ID cards prior to official verification.',
        'Be cautious of interviews conducted exclusively over informal chat platforms like Telegram or WhatsApp.',
      ];

  const recRows = recommendations.map((rec, i) => [`0${i + 1}`, rec]);

  autoTable(doc, {
    startY: cursorY,
    head: [['#', 'CANDIDATE DILIGENCE & SAFETY ADVISORY']],
    body: recRows,
    margin: { left: margin, right: margin },
    styles: {
      fontSize: 7.5,
      cellPadding: 2,
      lineColor: [226, 232, 240],
      lineWidth: 0.2,
    },
    headStyles: {
      fillColor: [30, 41, 59],
      textColor: [255, 255, 255],
      fontStyle: 'bold',
      fontSize: 8,
    },
    columnStyles: {
      0: { fontStyle: 'bold', cellWidth: 10, halign: 'center', textColor: [100, 116, 139] },
      1: { textColor: [51, 65, 85] },
    },
    theme: 'grid',
  });

  // -------------------------------------------------------------
  // 8. PAGE FOOTERS ON ALL PAGES
  // -------------------------------------------------------------
  const totalPages = doc.internal.getNumberOfPages();
  for (let i = 1; i <= totalPages; i++) {
    doc.setPage(i);

    // Subtle divider line
    doc.setDrawColor(226, 232, 240);
    doc.line(margin, pageHeight - 12, pageWidth - margin, pageHeight - 12);

    doc.setFont('helvetica', 'normal');
    doc.setFontSize(7);
    doc.setTextColor(148, 163, 184); // slate-400
    doc.text(
      'HIRESHIELD RISK INTELLIGENCE • CONFIDENTIAL CANDIDATE AUDIT REPORT • PROPRIETARY HEURISTIC ENGINE',
      margin,
      pageHeight - 7
    );

    doc.setFont('courier', 'bold');
    doc.text(`PAGE ${i} OF ${totalPages}`, pageWidth - margin, pageHeight - 7, { align: 'right' });
  }

  // -------------------------------------------------------------
  // 9. TRIGGER DOWNLOAD
  // -------------------------------------------------------------
  const sanitizedId = String(reportId).replace(/[^a-zA-Z0-9-_]/g, '_');
  const filename = `hireshield-audit-report-${sanitizedId}.pdf`;
  doc.save(filename);
}
