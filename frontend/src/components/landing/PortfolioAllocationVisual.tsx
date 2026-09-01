import React, { useState } from 'react';
import {
  PieChart as PieIcon,
  ScatterChart as ScatterIcon,
  ShieldAlert,
} from 'lucide-react';

interface SectorSlice {
  name: string;
  pct: number;
  color: string;
  value: string;
  holdings: string[];
}

const SECTORS: SectorSlice[] = [
  { name: 'Technology & AI', pct: 42, color: '#6366f1', value: '$52,500', holdings: ['NVDA', 'MSFT', 'AAPL'] },
  { name: 'Healthcare & Biotech', pct: 18, color: '#06b6d4', value: '$22,500', holdings: ['LLY', 'UNH'] },
  { name: 'Financial Services', pct: 15, color: '#10b981', value: '$18,750', holdings: ['JPM', 'V'] },
  { name: 'Energy & Industrials', pct: 10, color: '#f59e0b', value: '$12,500', holdings: ['XOM', 'GE'] },
  { name: 'Cash & Short Treasuries', pct: 15, color: '#8b5cf6', value: '$18,750', holdings: ['BIL', 'USD'] },
];

interface ScatterAsset {
  symbol: string;
  name: string;
  volatilityPct: number; // x: 10% to 50%
  returnPct: number;     // y: 5% to 45%
  weightPct: number;
  color: string;
  isBenchmark?: boolean;
}

const SCATTER_ASSETS: ScatterAsset[] = [
  { symbol: 'NVDA', name: 'NVIDIA Corp', volatilityPct: 42, returnPct: 38, weightPct: 22, color: '#6366f1' },
  { symbol: 'MSFT', name: 'Microsoft Corp', volatilityPct: 22, returnPct: 24, weightPct: 15, color: '#818cf8' },
  { symbol: 'AAPL', name: 'Apple Inc', volatilityPct: 18, returnPct: 19, weightPct: 12, color: '#06b6d4' },
  { symbol: 'JPM', name: 'JPMorgan Chase', volatilityPct: 16, returnPct: 14, weightPct: 10, color: '#10b981' },
  { symbol: 'LLY', name: 'Eli Lilly', volatilityPct: 25, returnPct: 28, weightPct: 11, color: '#ec4899' },
  { symbol: 'SPY', name: 'S&P 500 Benchmark', volatilityPct: 15, returnPct: 12, weightPct: 0, color: '#94a3b8', isBenchmark: true },
];

export const PortfolioAllocationVisual: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'donut' | 'scatter' | 'drawdown'>('donut');
  const [hoveredSector, setHoveredSector] = useState<SectorSlice | null>(SECTORS[0]);
  const [hoveredAsset, setHoveredAsset] = useState<ScatterAsset | null>(SCATTER_ASSETS[0]);

  // Compute SVG Donut paths
  let cumulativeAngle = 0;
  const radius = 70;
  const cx = 100;
  const cy = 100;

  const donutSlices = SECTORS.map((s) => {
    const angle = (s.pct / 100) * 360;
    const startAngle = cumulativeAngle;
    const endAngle = cumulativeAngle + angle;
    cumulativeAngle += angle;

    const startRad = ((startAngle - 90) * Math.PI) / 180;
    const endRad = ((endAngle - 90) * Math.PI) / 180;

    const x1 = cx + radius * Math.cos(startRad);
    const y1 = cy + radius * Math.sin(startRad);
    const x2 = cx + radius * Math.cos(endRad);
    const y2 = cy + radius * Math.sin(endRad);

    const largeArc = angle > 180 ? 1 : 0;
    const d = `M ${x1} ${y1} A ${radius} ${radius} 0 ${largeArc} 1 ${x2} ${y2}`;

    return { ...s, d, startAngle, endAngle };
  });

  return (
    <div className="w-full max-w-5xl mx-auto rounded-3xl bg-surface-200/90 border border-border-strong p-6 sm:p-8 backdrop-blur-xl font-sans text-left relative overflow-hidden shadow-2xl">
      {/* Background Circuit Grid */}
      <div className="absolute inset-0 bg-grid-pattern opacity-25 pointer-events-none" />

      {/* Header with Mode Toggles */}
      <div className="flex flex-wrap items-center justify-between gap-4 pb-5 mb-6 border-b border-border-subtle relative z-10">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-brand-500/10 border border-brand-500/30 text-brand-300 text-xs font-semibold uppercase tracking-wider mb-2">
            <PieIcon className="w-3.5 h-3.5 text-brand-cyan" />
            <span>Whole-Portfolio Contextualization</span>
          </div>
          <h3 className="text-xl sm:text-2xl font-bold text-white tracking-tight">
            Research Is Grounded in Your Exact Portfolio Weights
          </h3>
        </div>

        {/* View Mode Switcher */}
        <div className="flex items-center gap-1.5 p-1 rounded-xl bg-surface-100/90 border border-border-subtle text-xs font-mono">
          <button
            onClick={() => setActiveTab('donut')}
            className={`px-3 py-1.5 rounded-lg transition-all flex items-center gap-1.5 ${
              activeTab === 'donut'
                ? 'bg-brand-500 text-white font-bold shadow-glow-brand'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            <PieIcon className="w-3.5 h-3.5" />
            <span>Asset Allocation</span>
          </button>

          <button
            onClick={() => setActiveTab('scatter')}
            className={`px-3 py-1.5 rounded-lg transition-all flex items-center gap-1.5 ${
              activeTab === 'scatter'
                ? 'bg-brand-500 text-white font-bold shadow-glow-brand'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            <ScatterIcon className="w-3.5 h-3.5" />
            <span>Risk vs Return</span>
          </button>

          <button
            onClick={() => setActiveTab('drawdown')}
            className={`px-3 py-1.5 rounded-lg transition-all flex items-center gap-1.5 ${
              activeTab === 'drawdown'
                ? 'bg-brand-500 text-white font-bold shadow-glow-brand'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            <ShieldAlert className="w-3.5 h-3.5" />
            <span>Telemetry Drawdown</span>
          </button>
        </div>
      </div>

      {/* Main Content Pane */}
      <div className="relative z-10">
        {/* ========================================================================= */}
        {/* TAB 1: SVG DONUT CHART & SECTOR EXPOSURE BARS */}
        {/* ========================================================================= */}
        {activeTab === 'donut' && (
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-center">
            {/* Donut Visual */}
            <div className="lg:col-span-5 flex flex-col items-center justify-center p-4">
              <div className="relative w-52 h-52">
                <svg viewBox="0 0 200 200" className="w-full h-full transform -rotate-90">
                  {donutSlices.map((slice, idx) => (
                    <path
                      key={idx}
                      d={slice.d}
                      fill="none"
                      stroke={slice.color}
                      strokeWidth={hoveredSector?.name === slice.name ? 22 : 18}
                      className="transition-all duration-300 cursor-pointer"
                      onMouseEnter={() => setHoveredSector(slice)}
                    />
                  ))}
                </svg>

                {/* Center Donut Hole Text */}
                <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none text-center">
                  <span className="text-[11px] font-mono uppercase text-slate-400">Total Portfolio</span>
                  <span className="text-xl font-bold text-white font-mono mt-0.5">$125,000</span>
                  <span className="text-[10px] text-brand-emerald font-mono font-semibold">+25.0% P&L</span>
                </div>
              </div>
              <span className="text-[11px] font-mono text-slate-400 mt-2">Hover sector to inspect holdings</span>
            </div>

            {/* Sector Exposure List */}
            <div className="lg:col-span-7 space-y-2.5">
              {SECTORS.map((s, idx) => {
                const isSelected = hoveredSector?.name === s.name;
                return (
                  <div
                    key={idx}
                    onMouseEnter={() => setHoveredSector(s)}
                    className={`p-3 rounded-2xl border transition-all cursor-pointer ${
                      isSelected
                        ? 'bg-surface-100/90 border-brand-500/50 shadow-glow-card'
                        : 'bg-surface-100/40 border-border-subtle hover:bg-surface-100/70'
                    }`}
                  >
                    <div className="flex items-center justify-between text-xs mb-1.5">
                      <div className="flex items-center gap-2">
                        <span className="w-3 h-3 rounded-full shrink-0" style={{ backgroundColor: s.color }} />
                        <span className="font-semibold text-white">{s.name}</span>
                      </div>
                      <div className="flex items-center gap-3 font-mono">
                        <span className="text-slate-400">{s.value}</span>
                        <strong className="text-white font-bold">{s.pct}%</strong>
                      </div>
                    </div>

                    {/* Progress Bar */}
                    <div className="w-full h-1.5 rounded-full bg-surface-300 overflow-hidden">
                      <div
                        className="h-full rounded-full transition-all duration-500"
                        style={{ width: `${s.pct}%`, backgroundColor: s.color }}
                      />
                    </div>

                    {/* Holdings chips */}
                    {isSelected && (
                      <div className="flex items-center gap-1.5 mt-2 pt-2 border-t border-border-subtle/60 text-[10px] font-mono text-slate-300">
                        <span className="text-slate-400">Allocated Assets:</span>
                        {s.holdings.map((h, i) => (
                          <span key={i} className="px-1.5 py-0.5 rounded bg-surface-200 border border-border-subtle text-brand-cyan">
                            ${h}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* ========================================================================= */}
        {/* TAB 2: RISK VS RETURN SCATTER MATRIX */}
        {/* ========================================================================= */}
        {activeTab === 'scatter' && (
          <div>
            <div className="p-4 rounded-2xl bg-surface-400/90 border border-border-subtle relative overflow-hidden">
              <div className="flex items-center justify-between text-xs font-mono text-slate-400 mb-2">
                <span>Y-Axis: Projected Annual Return (%)</span>
                <span>X-Axis: Annualized Volatility (%)</span>
              </div>

              {/* Scatter SVG Grid */}
              <svg viewBox="0 0 500 240" className="w-full h-56 select-none">
                {/* Benchmark SPY baseline area */}
                <line x1="50" y1="30" x2="450" y2="210" stroke="rgba(255,255,255,0.1)" strokeDasharray="3 3" />
                <text x="380" y="195" fill="#94a3b8" fontSize="9" fontFamily="monospace">
                  Capital Market Line
                </text>

                {/* Gridlines */}
                {[50, 110, 170].map((y, i) => (
                  <line key={i} x1="40" y1={y} x2="480" y2={y} stroke="rgba(255,255,255,0.05)" />
                ))}
                {[120, 220, 320, 420].map((x, i) => (
                  <line key={i} x1={x} y1="20" x2={x} y2="210" stroke="rgba(255,255,255,0.05)" />
                ))}

                {/* Scatter Dots */}
                {SCATTER_ASSETS.map((asset, idx) => {
                  // Map volatility (10-50) to X (60-460)
                  const cx = 60 + ((asset.volatilityPct - 10) / 40) * 400;
                  // Map return (5-45) to Y (200-30)
                  const cy = 200 - ((asset.returnPct - 5) / 40) * 170;
                  const isHovered = hoveredAsset?.symbol === asset.symbol;

                  return (
                    <g
                      key={idx}
                      className="cursor-pointer"
                      onMouseEnter={() => setHoveredAsset(asset)}
                      onClick={() => setHoveredAsset(asset)}
                    >
                      {/* Pulse ring for selected asset */}
                      {isHovered && (
                        <circle cx={cx} cy={cy} r="14" fill={asset.color} fillOpacity="0.25" />
                      )}
                      <circle
                        cx={cx}
                        cy={cy}
                        r={asset.isBenchmark ? 6 : 8}
                        fill={asset.color}
                        stroke="#0a0d13"
                        strokeWidth="2"
                      />
                      <text
                        x={cx + 10}
                        y={cy + 4}
                        fill="#ffffff"
                        fontSize="10"
                        fontWeight="bold"
                        fontFamily="monospace"
                      >
                        {asset.symbol}
                      </text>
                    </g>
                  );
                })}
              </svg>
            </div>

            {/* Asset Scatter Callout */}
            {hoveredAsset && (
              <div className="mt-4 p-3 rounded-xl bg-surface-100 border border-brand-500/30 flex items-center justify-between text-xs">
                <div className="flex items-center gap-2">
                  <span className="w-3 h-3 rounded-full" style={{ backgroundColor: hoveredAsset.color }} />
                  <strong className="text-white">{hoveredAsset.name} (${hoveredAsset.symbol})</strong>
                </div>
                <div className="flex items-center gap-4 font-mono text-[11px]">
                  <span>Volatility: <strong className="text-white">{hoveredAsset.volatilityPct}%</strong></span>
                  <span>Projected Return: <strong className="text-brand-emerald">{hoveredAsset.returnPct}%</strong></span>
                  <span>Portfolio Weight: <strong className="text-brand-cyan">{hoveredAsset.weightPct}%</strong></span>
                </div>
              </div>
            )}
          </div>
        )}

        {/* ========================================================================= */}
        {/* TAB 3: DRAWDOWN & DETERMINISTIC ALERT TELEMETRY */}
        {/* ========================================================================= */}
        {activeTab === 'drawdown' && (
          <div>
            <div className="p-4 rounded-2xl bg-surface-400/90 border border-border-subtle relative overflow-hidden">
              <div className="flex items-center justify-between text-xs font-mono text-slate-400 mb-2">
                <span>Continuous Equity Curve Telemetry</span>
                <span className="text-amber-400 font-semibold flex items-center gap-1">
                  <ShieldAlert className="w-3.5 h-3.5" />
                  Drawdown Threshold: 5.0%
                </span>
              </div>

              {/* Drawdown Curve SVG */}
              <svg viewBox="0 0 500 140" className="w-full h-40 select-none">
                <defs>
                  <linearGradient id="drawdownGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#10b981" stopOpacity="0.3" />
                    <stop offset="100%" stopColor="#10b981" stopOpacity="0.0" />
                  </linearGradient>
                </defs>

                {/* Gridlines */}
                <line x1="30" y1="30" x2="470" y2="30" stroke="rgba(255,255,255,0.05)" />
                <line x1="30" y1="80" x2="470" y2="80" stroke="rgba(255,255,255,0.05)" />
                <line x1="30" y1="120" x2="470" y2="120" stroke="rgba(255,255,255,0.05)" />

                {/* Normal Curve */}
                <path
                  d="M 40 50 L 100 42 L 160 35 L 220 28 L 260 78 L 300 82 L 350 48 L 410 32 L 460 25"
                  fill="none"
                  stroke="#10b981"
                  strokeWidth="2.5"
                />

                {/* Highlighted Drawdown Zone */}
                <rect x="235" y="20" width="80" height="90" fill="rgba(245, 158, 11, 0.12)" stroke="#f59e0b" strokeWidth="1" strokeDasharray="3 3" rx="4" />

                {/* Alert Event Marker */}
                <circle cx="260" cy="78" r="6" fill="#f59e0b" stroke="#ffffff" strokeWidth="2" />
                <text x="272" y="75" fill="#f59e0b" fontSize="10" fontWeight="bold" fontFamily="monospace">
                  -7.2% Drawdown
                </text>
              </svg>
            </div>

            <div className="mt-4 p-3.5 rounded-2xl bg-amber-500/10 border border-amber-500/30 flex items-center justify-between text-xs text-amber-200 font-sans">
              <div className="flex items-center gap-2">
                <ShieldAlert className="w-4 h-4 text-amber-400 shrink-0" />
                <span>Deterministic Alert Triggered: Signed HMAC Webhook dispatched in 42ms with 0 LLM hallucination.</span>
              </div>
              <span className="font-mono text-[11px] text-amber-300 font-bold">Rule ID #941</span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
