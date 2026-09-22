import React, { useState, useEffect, useRef } from 'react';

export default function ShieldHero({ score = 24, level = 'LOW RISK' }) {
  const [mousePos, setMousePos] = useState({ x: 0, y: 0 });
  const [activeNode, setActiveNode] = useState(0);
  const containerRef = useRef(null);

  // Nodes specified in the Master Prompt
  const nodes = [
    { label: 'IDENTITY', x: 70, y: 110, angle: -140 },
    { label: 'RESUME', x: 50, y: 250, angle: -170 },
    { label: 'NLP', x: 80, y: 390, angle: -200 },
    { label: 'TECHNICAL', x: 530, y: 110, angle: -40 },
    { label: 'VERIFICATION', x: 550, y: 250, angle: -10 },
    { label: 'BEHAVIOR', x: 520, y: 390, angle: 20 },
  ];

  // Cycling active node for data telemetry feel
  useEffect(() => {
    const timer = setInterval(() => {
      setActiveNode((prev) => (prev + 1) % nodes.length);
    }, 1800);
    return () => clearInterval(timer);
  }, [nodes.length]);

  // Subtle mouse movement / parallax
  const handleMouseMove = (e) => {
    if (!containerRef.current) return;
    const rect = containerRef.current.getBoundingClientRect();
    const x = ((e.clientX - rect.left) / rect.width - 0.5) * 16;
    const y = ((e.clientY - rect.top) / rect.height - 0.5) * 16;
    setMousePos({ x, y });
  };

  const handleMouseLeave = () => {
    setMousePos({ x: 0, y: 0 });
  };

  return (
    <div 
      ref={containerRef}
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
      className="relative w-full max-w-[620px] aspect-[6/5] flex items-center justify-center select-none"
      style={{
        transform: `perspective(1000px) rotateX(${-mousePos.y * 0.4}deg) rotateY(${mousePos.x * 0.4}deg)`,
        transition: 'transform 0.2s cubic-bezier(0.16, 1, 0.3, 1)',
      }}
    >
      {/* Background radial glow */}
      <div className="absolute inset-0 bg-gradient-radial from-brand-primary/15 via-transparent to-transparent pointer-events-none filter blur-2xl" />

      {/* Main SVG Visualization Canvas */}
      <svg 
        viewBox="0 0 600 500" 
        className="w-full h-full drop-shadow-[0_0_35px_rgba(22,119,232,0.2)] overflow-visible"
        aria-label="HireShield AI Risk Engine Interactive Shield"
      >
        <defs>
          {/* Blue Cyber Linear Gradient */}
          <linearGradient id="shieldBorderGrad" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#5DA2F0" stopOpacity="0.9" />
            <stop offset="50%" stopColor="#1677E8" stopOpacity="0.7" />
            <stop offset="100%" stopColor="#0F59C5" stopOpacity="0.4" />
          </linearGradient>

          {/* Inner Surface Gradient */}
          <linearGradient id="shieldSurfaceGrad" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor="#0B1625" stopOpacity="0.85" />
            <stop offset="60%" stopColor="#07111F" stopOpacity="0.92" />
            <stop offset="100%" stopColor="#05070B" stopOpacity="0.98" />
          </linearGradient>

          {/* Scanning Beam Gradient */}
          <linearGradient id="laserGrad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#1677E8" stopOpacity="0" />
            <stop offset="45%" stopColor="#1677E8" stopOpacity="0.15" />
            <stop offset="50%" stopColor="#5DA2F0" stopOpacity="0.85" />
            <stop offset="55%" stopColor="#1677E8" stopOpacity="0.15" />
            <stop offset="100%" stopColor="#1677E8" stopOpacity="0" />
          </linearGradient>

          {/* Mask for scanning beam inside shield */}
          <mask id="shieldClipMask">
            <path
              d="M300,50 L420,95 L420,270 C420,360 300,430 300,430 C300,430 180,360 180,270 L180,95 Z"
              fill="#FFFFFF"
            />
          </mask>
        </defs>

        {/* Outer Background Circuit Lines & Connecting Rays */}
        <g className="stroke-brand-primary/20 stroke-[1.5]" strokeDasharray="3 3">
          {nodes.map((node, i) => {
            const shieldAnchorX = i < 3 ? 180 : 420;
            const shieldAnchorY = i === 0 || i === 3 ? 130 : i === 1 || i === 4 ? 260 : 360;
            const isHot = activeNode === i;
            return (
              <g key={node.label}>
                <line
                  x1={node.x + (i < 3 ? 45 : -45)}
                  y1={node.y}
                  x2={shieldAnchorX}
                  y2={shieldAnchorY}
                  className={`transition-all duration-700 ${
                    isHot ? 'stroke-brand-light stroke-[2] opacity-90' : 'opacity-40'
                  }`}
                  strokeDasharray={isHot ? 'none' : '4 4'}
                />
                {isHot && (
                  <circle
                    cx={(node.x + shieldAnchorX) / 2}
                    cy={(node.y + shieldAnchorY) / 2}
                    r="3"
                    className="fill-brand-light animate-ping"
                  />
                )}
              </g>
            );
          })}
        </g>

        {/* Concentric subtle radar grid rings */}
        <circle cx="300" cy="250" r="160" fill="none" stroke="rgba(30,58,102,0.18)" strokeWidth="1" strokeDasharray="6 8" />
        <circle cx="300" cy="250" r="220" fill="none" stroke="rgba(30,58,102,0.12)" strokeWidth="1" />

        {/* THE SHIELD BASE SURFACE */}
        <path
          d="M300,50 L420,95 L420,270 C420,360 300,430 300,430 C300,430 180,360 180,270 L180,95 Z"
          fill="url(#shieldSurfaceGrad)"
          stroke="url(#shieldBorderGrad)"
          strokeWidth="2.5"
          className="transition-all duration-500 filter drop-shadow-[0_0_15px_rgba(22,119,232,0.3)]"
        />

        {/* Inner Tech Inset Border */}
        <path
          d="M300,68 L404,106 L404,260 C404,342 300,408 300,408 C300,408 196,342 196,260 L196,106 Z"
          fill="none"
          stroke="#1677E8"
          strokeOpacity="0.25"
          strokeWidth="1.2"
          strokeDasharray="16 4"
        />

        {/* Scanning Laser Beam (masked to shield interior) */}
        <g mask="url(#shieldClipMask)">
          <rect
            x="170"
            y="40"
            width="260"
            height="400"
            fill="url(#laserGrad)"
            className="animate-scanline pointer-events-none"
          />
        </g>

        {/* Corner Cyber Brackets */}
        <path d="M170,85 L170,75 L190,75" fill="none" stroke="#5DA2F0" strokeWidth="2" opacity="0.7" />
        <path d="M430,85 L430,75 L410,75" fill="none" stroke="#5DA2F0" strokeWidth="2" opacity="0.7" />
        <path d="M290,440 L300,450 L310,440" fill="none" stroke="#5DA2F0" strokeWidth="2" opacity="0.7" />

        {/* INSIDE THE SHIELD - CONTENT REQUIRED BY SPEC:
            HIRE SHIELD
            AI RISK ENGINE
            27 (or dynamic score)
            LOW RISK (or level) */}
        <g className="text-center select-none">
          {/* Status badge at top */}
          <text
            x="300"
            y="130"
            textAnchor="middle"
            className="fill-brand-light font-mono text-[10px] tracking-[0.25em] font-semibold"
          >
            HIRESHIELD INTELLIGENCE
          </text>

          {/* Subheading */}
          <text
            x="300"
            y="152"
            textAnchor="middle"
            className="fill-text-muted font-mono text-[9px] tracking-[0.2em]"
          >
            AI RISK ENGINE // ACTIVE
          </text>

          {/* Large Center Numerical Score */}
          <text
            x="300"
            y="245"
            textAnchor="middle"
            className="fill-white font-sans font-extrabold text-[64px] tracking-tight drop-shadow-[0_0_20px_rgba(22,119,232,0.5)]"
          >
            {score}
          </text>
          
          <text
            x="300"
            y="272"
            textAnchor="middle"
            className="fill-text-muted font-mono text-[11px] tracking-widest"
          >
            / 100
          </text>

          {/* Risk Level Badge */}
          <g transform="translate(230, 305)">
            <rect
              width="140"
              height="26"
              rx="13"
              fill={score >= 75 ? 'rgba(239,68,68,0.15)' : score >= 50 ? 'rgba(249,115,22,0.15)' : score >= 25 ? 'rgba(245,158,11,0.15)' : 'rgba(16,185,129,0.15)'}
              stroke={score >= 75 ? 'rgba(239,68,68,0.4)' : score >= 50 ? 'rgba(249,115,22,0.4)' : score >= 25 ? 'rgba(245,158,11,0.4)' : 'rgba(16,185,129,0.4)'}
              strokeWidth="1"
            />
            <circle
              cx="18"
              cy="13"
              r="3.5"
              fill={score >= 75 ? '#EF4444' : score >= 50 ? '#F97316' : score >= 25 ? '#F59E0B' : '#10B981'}
              className="animate-pulse"
            />
            <text
              x="75"
              y="17"
              textAnchor="middle"
              fill={score >= 75 ? '#EF4444' : score >= 50 ? '#F97316' : score >= 25 ? '#F59E0B' : '#10B981'}
              className="font-mono text-[10px] font-bold tracking-widest"
            >
              {level}
            </text>
          </g>

          {/* Bottom telemetry line */}
          <text
            x="300"
            y="370"
            textAnchor="middle"
            className="fill-text-muted/60 font-mono text-[8px] tracking-[0.15em]"
          >
            TELEMETRY: VERIFIED // CONFIDENCE 94%
          </text>
        </g>

        {/* 6 ORBITAL SIGNAL NODES:
            IDENTITY, RESUME, NLP, TECHNICAL, VERIFICATION, BEHAVIOR */}
        {nodes.map((node, i) => {
          const isActive = activeNode === i;
          return (
            <g 
              key={node.label}
              className="cursor-pointer transition-all duration-300 group"
              onClick={() => setActiveNode(i)}
            >
              {/* Node Card Container */}
              <rect
                x={node.x - 45}
                y={node.y - 18}
                width="90"
                height="36"
                rx="6"
                fill={isActive ? '#091522' : '#07111F'}
                stroke={isActive ? '#1677E8' : 'rgba(30,58,102,0.4)'}
                strokeWidth={isActive ? '1.5' : '1'}
                className="transition-all duration-300 drop-shadow-md group-hover:stroke-brand-light"
              />

              {/* Status Dot */}
              <circle
                cx={node.x - 30}
                cy={node.y}
                r="3"
                className={`transition-colors ${
                  isActive ? 'fill-brand-light animate-pulse' : 'fill-text-muted'
                }`}
              />

              {/* Node Text Label */}
              <text
                x={node.x + 8}
                y={node.y + 4}
                textAnchor="middle"
                className={`font-mono text-[9px] tracking-wider font-semibold transition-colors ${
                  isActive ? 'fill-white' : 'fill-text-muted group-hover:fill-text-secondary'
                }`}
              >
                {node.label}
              </text>
            </g>
          );
        })}
      </svg>
    </div>
  );
}
