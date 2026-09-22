import React from 'react';
import { ShieldCheck, AlertTriangle, ShieldAlert, AlertOctagon, HelpCircle, ShieldQuestion } from 'lucide-react';

export default function RadialScoreGauge({ 
  score = null, 
  level = 'LOW', 
  contentAnalyzed = true,
  size = 200, 
  strokeWidth = 14 
}) {
  const isIncomplete = !contentAnalyzed || score === null || level === 'INCOMPLETE';

  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;

  if (isIncomplete) {
    // Incomplete / Unanalyzed Content State
    const color = '#F59E0B'; // Amber alert tone
    const glowColor = 'rgba(245, 158, 11, 0.25)';
    const bgTrackColor = 'rgba(245, 158, 11, 0.12)';

    return (
      <div className="flex flex-col items-center justify-center relative select-none">
        <div style={{ width: size, height: size }} className="relative flex items-center justify-center">
          <svg width={size} height={size} className="rotate-[-90deg] overflow-visible">
            {/* Background Track */}
            <circle
              cx={size / 2}
              cy={size / 2}
              r={radius}
              fill="none"
              stroke={bgTrackColor}
              strokeWidth={strokeWidth}
            />

            {/* Incomplete Dashed Arc (Indicates partial Layer A assessment) */}
            <circle
              cx={size / 2}
              cy={size / 2}
              r={radius}
              fill="none"
              stroke={color}
              strokeWidth={strokeWidth}
              strokeDasharray="6 8"
              strokeDashoffset="0"
              strokeLinecap="round"
              className="opacity-70 animate-pulse"
              style={{ filter: `drop-shadow(0 0 8px ${glowColor})` }}
            />
          </svg>

          {/* Center Content for Incomplete Scan */}
          <div className="absolute inset-0 flex flex-col items-center justify-center text-center p-3">
            <div className="text-[10px] font-mono tracking-widest text-text-muted uppercase mb-0.5">
              RISK SCORE
            </div>
            <div className="text-3xl sm:text-4xl font-extrabold tracking-tight text-white flex items-baseline">
              <span className="text-risk-medium">N/A</span>
            </div>
            <div className="text-[10px] font-mono text-text-muted mt-0.5">
              CONTENT NOT ANALYZED
            </div>

            <div 
              className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[10px] font-mono font-bold tracking-wider mt-2 border bg-risk-medium/10 border-risk-medium/40 text-risk-medium"
            >
              <HelpCircle className="w-3 h-3" />
              <span>INCOMPLETE</span>
            </div>
          </div>
        </div>
        <p className="text-[11px] font-mono text-text-muted text-center mt-2 max-w-[200px] leading-tight">
          Insufficient page content for complete risk analysis.
        </p>
      </div>
    );
  }

  // Completed Content Analysis State
  const normalizedScore = Math.min(100, Math.max(0, Math.round(score ?? 0)));
  const strokeDashoffset = circumference - (normalizedScore / 100) * circumference;

  let color = '#10B981'; // LOW
  let glowColor = 'rgba(16, 185, 129, 0.35)';
  let bgTrackColor = 'rgba(16, 185, 129, 0.12)';
  let Icon = ShieldCheck;

  if (level === 'CRITICAL' || normalizedScore >= 75) {
    color = '#EF4444';
    glowColor = 'rgba(239, 68, 68, 0.4)';
    bgTrackColor = 'rgba(239, 68, 68, 0.12)';
    Icon = AlertOctagon;
  } else if (level === 'HIGH' || normalizedScore >= 50) {
    color = '#F97316';
    glowColor = 'rgba(249, 115, 22, 0.4)';
    bgTrackColor = 'rgba(249, 115, 22, 0.12)';
    Icon = ShieldAlert;
  } else if (level === 'MEDIUM' || normalizedScore >= 25) {
    color = '#F59E0B';
    glowColor = 'rgba(245, 158, 11, 0.4)';
    bgTrackColor = 'rgba(245, 158, 11, 0.12)';
    Icon = AlertTriangle;
  }

  return (
    <div className="flex flex-col items-center justify-center relative select-none">
      <div style={{ width: size, height: size }} className="relative flex items-center justify-center">
        <svg width={size} height={size} className="rotate-[-90deg] overflow-visible">
          {/* Background Track */}
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="none"
            stroke={bgTrackColor}
            strokeWidth={strokeWidth}
          />

          {/* Progress Arc */}
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="none"
            stroke={color}
            strokeWidth={strokeWidth}
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            strokeLinecap="round"
            className="transition-all duration-1000 ease-out"
            style={{ filter: `drop-shadow(0 0 10px ${glowColor})` }}
          />
        </svg>

        {/* Center Content */}
        <div className="absolute inset-0 flex flex-col items-center justify-center text-center p-4">
          <div className="text-[11px] font-mono tracking-widest text-text-muted uppercase mb-1">
            RISK SCORE
          </div>
          <div className="text-4xl sm:text-5xl font-extrabold tracking-tight text-white flex items-baseline">
            <span>{normalizedScore}</span>
            <span className="text-xs font-mono text-text-muted ml-1">/100</span>
          </div>

          <div 
            className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-[11px] font-mono font-bold tracking-wider mt-2 border"
            style={{
              backgroundColor: `${color}15`,
              borderColor: `${color}40`,
              color: color,
            }}
          >
            <Icon className="w-3 h-3" />
            <span>{level}</span>
          </div>
        </div>
      </div>
    </div>
  );
}
