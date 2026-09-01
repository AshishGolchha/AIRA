import React, { useState } from 'react';
import {
  TrendingUp,
  Activity,
  Sparkles,
  Search,
  Bell,
} from 'lucide-react';

interface ChartPoint {
  date: string;
  price: number;
  label?: string;
  signalType?: 'ingestion' | 'consensus' | 'alert';
  signalDetail?: string;
}

interface TickerData {
  symbol: string;
  companyName: string;
  currentPrice: string;
  change: string;
  isPositive: boolean;
  peRatio: string;
  evEbitda: string;
  fcfYield: string;
  range52w: { low: number; high: number; current: number };
  points: ChartPoint[];
}

const MARKET_DATA: Record<string, TickerData> = {
  NVDA: {
    symbol: 'NVDA',
    companyName: 'NVIDIA Corp',
    currentPrice: '$128.50',
    change: '+142.8% (1Y)',
    isPositive: true,
    peRatio: '64.2x',
    evEbitda: '51.8x',
    fcfYield: '2.8%',
    range52w: { low: 45.2, high: 140.7, current: 128.5 },
    points: [
      { date: 'Oct 25', price: 48.0 },
      { date: 'Nov 25', price: 54.5 },
      {
        date: 'Dec 25',
        price: 68.0,
        label: 'SEC 10-Q Ingested',
        signalType: 'ingestion',
        signalDetail: 'Data Center compute revenue surged +154% YoY ($26.3B).',
      },
      { date: 'Jan 26', price: 79.2 },
      { date: 'Feb 26', price: 92.4 },
      {
        date: 'Mar 26',
        price: 110.0,
        label: 'Agent Consensus',
        signalType: 'consensus',
        signalDetail: 'Blackwell architecture moat switching costs confirmed.',
      },
      { date: 'Apr 26', price: 104.5 },
      {
        date: 'May 26',
        price: 118.2,
        label: 'Price Move Alert',
        signalType: 'alert',
        signalDetail: 'Deterministic >5.0% swing trigger dispatched via Webhook.',
      },
      { date: 'Jun 26', price: 128.5 },
    ],
  },
  AAPL: {
    symbol: 'AAPL',
    companyName: 'Apple Inc',
    currentPrice: '$224.20',
    change: '+24.5% (1Y)',
    isPositive: true,
    peRatio: '33.1x',
    evEbitda: '24.6x',
    fcfYield: '3.4%',
    range52w: { low: 164.0, high: 237.2, current: 224.2 },
    points: [
      { date: 'Oct 25', price: 172.0 },
      { date: 'Nov 25', price: 180.5 },
      {
        date: 'Dec 25',
        price: 195.0,
        label: 'Services Margin Spike',
        signalType: 'ingestion',
        signalDetail: 'Services segment gross margin expanded to 74.0%.',
      },
      { date: 'Jan 26', price: 188.0 },
      { date: 'Feb 26', price: 202.0 },
      {
        date: 'Mar 26',
        price: 215.0,
        label: 'Active Base Milestone',
        signalType: 'consensus',
        signalDetail: 'Active installed base surpassed 2.2B devices globally.',
      },
      { date: 'Apr 26', price: 208.5 },
      {
        date: 'May 26',
        price: 219.0,
        label: 'Dividend Telemetry',
        signalType: 'alert',
        signalDetail: 'Quarterly capital return telemetry verified.',
      },
      { date: 'Jun 26', price: 224.2 },
    ],
  },
  MSFT: {
    symbol: 'MSFT',
    companyName: 'Microsoft Corp',
    currentPrice: '$448.90',
    change: '+31.2% (1Y)',
    isPositive: true,
    peRatio: '36.8x',
    evEbitda: '25.9x',
    fcfYield: '2.5%',
    range52w: { low: 340.0, high: 468.3, current: 448.9 },
    points: [
      { date: 'Oct 25', price: 348.0 },
      { date: 'Nov 25', price: 365.0 },
      {
        date: 'Dec 25',
        price: 388.0,
        label: 'Azure Cloud Acceleration',
        signalType: 'ingestion',
        signalDetail: 'Intelligent Cloud segment grew +21% YoY ($28.5B).',
      },
      { date: 'Jan 26', price: 402.0 },
      { date: 'Feb 26', price: 420.0 },
      {
        date: 'Mar 26',
        price: 435.0,
        label: 'Copilot Enterprise Moat',
        signalType: 'consensus',
        signalDetail: 'M365 seat expansion defensibility confirmed by 3 agents.',
      },
      { date: 'Apr 26', price: 425.0 },
      {
        date: 'May 26',
        price: 442.0,
        label: 'Concentration Threshold',
        signalType: 'alert',
        signalDetail: 'Portfolio weighting checked against risk threshold (20%).',
      },
      { date: 'Jun 26', price: 448.9 },
    ],
  },
};

export const MarketTerminalChart: React.FC = () => {
  const [selectedTicker, setSelectedTicker] = useState<string>('NVDA');
  const [hoveredIdx, setHoveredIdx] = useState<number | null>(5); // default to a milestone

  const activeData = MARKET_DATA[selectedTicker] || MARKET_DATA.NVDA;
  const points = activeData.points;

  // Chart coordinates mapping (SVG width: 800, height: 260)
  const minPrice = Math.min(...points.map((p) => p.price)) * 0.9;
  const maxPrice = Math.max(...points.map((p) => p.price)) * 1.05;

  const svgWidth = 800;
  const svgHeight = 240;
  const paddingX = 40;
  const paddingY = 25;

  const getX = (idx: number) => paddingX + (idx / (points.length - 1)) * (svgWidth - paddingX * 2);
  const getY = (price: number) =>
    svgHeight - paddingY - ((price - minPrice) / (maxPrice - minPrice)) * (svgHeight - paddingY * 2);

  // Generate SVG Path
  const pathD = points.reduce((acc, pt, idx) => {
    const x = getX(idx);
    const y = getY(pt.price);
    return idx === 0 ? `M ${x} ${y}` : `${acc} L ${x} ${y}`;
  }, '');

  const areaD = `${pathD} L ${getX(points.length - 1)} ${svgHeight - paddingY} L ${getX(0)} ${
    svgHeight - paddingY
  } Z`;

  const activePoint = hoveredIdx !== null ? points[hoveredIdx] : points[points.length - 1];

  return (
    <div className="w-full rounded-3xl bg-surface-50/95 dark:bg-surface-200/90 border border-border-strong p-5 sm:p-7 backdrop-blur-xl font-sans text-left shadow-xl dark:shadow-2xl relative overflow-hidden transition-colors duration-200">
      {/* Background Subtle Grid Pattern */}
      <div className="absolute inset-0 bg-grid-pattern opacity-40 dark:opacity-20 pointer-events-none" />

      {/* Terminal Header */}
      <div className="flex flex-wrap items-center justify-between gap-4 pb-4 mb-4 border-b border-border-subtle relative z-10">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-brand-500/10 dark:bg-brand-500/15 border border-brand-500/30 flex items-center justify-center text-brand-600 dark:text-brand-cyan">
            <Activity className="w-4 h-4" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-sm font-bold text-slate-900 dark:text-white tracking-tight">{activeData.companyName}</span>
              <span className="text-xs font-mono text-brand-700 dark:text-brand-cyan bg-brand-500/10 dark:bg-brand-cyan/10 px-2 py-0.5 rounded border border-brand-500/20 dark:border-brand-cyan/20">
                ${activeData.symbol}
              </span>
            </div>
            <div className="flex items-center gap-2 mt-0.5">
              <span className="text-base font-extrabold text-slate-900 dark:text-white font-mono">{activeData.currentPrice}</span>
              <span className="text-xs font-semibold text-emerald-600 dark:text-brand-emerald flex items-center gap-0.5 font-mono">
                <TrendingUp className="w-3 h-3" />
                {activeData.change}
              </span>
            </div>
          </div>
        </div>

        {/* Ticker Selector Switcher */}
        <div className="flex items-center gap-1.5 p-1 rounded-xl bg-surface-100 dark:bg-surface-100/90 border border-border-subtle text-xs font-mono">
          {Object.keys(MARKET_DATA).map((sym) => (
            <button
              key={sym}
              onClick={() => {
                setSelectedTicker(sym);
                setHoveredIdx(null);
              }}
              className={`px-3 py-1.5 rounded-lg font-bold transition-all ${
                selectedTicker === sym
                  ? 'bg-brand-600 text-white shadow-sm dark:shadow-glow-brand'
                  : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
              }`}
            >
              ${sym}
            </button>
          ))}
        </div>
      </div>

      {/* SVG Interactive Time-Series Chart */}
      <div className="relative z-10 w-full overflow-x-auto">
        <svg
          viewBox={`0 0 ${svgWidth} ${svgHeight}`}
          className="w-full h-48 sm:h-64 select-none"
          preserveAspectRatio="none"
        >
          <defs>
            {/* Area Gradient */}
            <linearGradient id={`chartGrad-${selectedTicker}`} x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#6366f1" stopOpacity="0.25" />
              <stop offset="100%" stopColor="#06b6d4" stopOpacity="0.0" />
            </linearGradient>
            {/* Line Gradient */}
            <linearGradient id={`lineGrad-${selectedTicker}`} x1="0" y1="0" x2="1" y2="0">
              <stop offset="0%" stopColor="#6366f1" />
              <stop offset="50%" stopColor="#818cf8" />
              <stop offset="100%" stopColor="#06b6d4" />
            </linearGradient>
          </defs>

          {/* Horizontal Gridlines */}
          {[0.2, 0.4, 0.6, 0.8].map((pct, i) => {
            const y = paddingY + pct * (svgHeight - paddingY * 2);
            return (
              <line
                key={i}
                x1={paddingX}
                y1={y}
                x2={svgWidth - paddingX}
                y2={y}
                stroke="currentColor"
                className="text-slate-200 dark:text-slate-800"
                strokeDasharray="4 4"
              />
            );
          })}

          {/* Area Fill */}
          <path d={areaD} fill={`url(#chartGrad-${selectedTicker})`} />

          {/* Main Price Trajectory Stroke */}
          <path
            d={pathD}
            fill="none"
            stroke={`url(#lineGrad-${selectedTicker})`}
            strokeWidth="3"
            strokeLinecap="round"
            strokeLinejoin="round"
          />

          {/* Milestone Interactive Points */}
          {points.map((pt, idx) => {
            const x = getX(idx);
            const y = getY(pt.price);
            const isMilestone = Boolean(pt.signalType);
            const isHovered = hoveredIdx === idx;

            return (
              <g
                key={idx}
                className="cursor-pointer"
                onMouseEnter={() => setHoveredIdx(idx)}
                onClick={() => setHoveredIdx(idx)}
              >
                {/* Vertical indicator guideline on hover */}
                {isHovered && (
                  <line
                    x1={x}
                    y1={paddingY}
                    x2={x}
                    y2={svgHeight - paddingY}
                    stroke="#06b6d4"
                    strokeWidth="1.5"
                    strokeDasharray="2 2"
                  />
                )}

                {/* Milestone Marker Outer Ring */}
                {isMilestone && (
                  <circle
                    cx={x}
                    cy={y}
                    r={isHovered ? 8 : 6}
                    fill="#ffffff"
                    stroke={
                      pt.signalType === 'ingestion'
                        ? '#06b6d4'
                        : pt.signalType === 'consensus'
                        ? '#6366f1'
                        : '#10b981'
                    }
                    strokeWidth="2.5"
                    className="transition-all duration-200"
                  />
                )}

                {/* Center dot */}
                <circle
                  cx={x}
                  cy={y}
                  r={isHovered ? 4 : isMilestone ? 3 : 2}
                  fill={isMilestone ? (pt.signalType === 'alert' ? '#10b981' : '#6366f1') : '#818cf8'}
                />
              </g>
            );
          })}
        </svg>
      </div>

      {/* Interactive Signal Callout Inspector */}
      {activePoint && (
        <div className="mt-4 p-3.5 sm:p-4 rounded-2xl bg-surface-100 dark:bg-surface-100/90 border border-brand-500/30 flex flex-wrap items-center justify-between gap-3 text-xs relative z-10 animate-in fade-in duration-200">
          <div className="flex items-center gap-3">
            <div
              className={`w-7 h-7 rounded-lg flex items-center justify-center shrink-0 ${
                activePoint.signalType === 'ingestion'
                  ? 'bg-brand-cyan/20 text-brand-600 dark:text-brand-cyan'
                  : activePoint.signalType === 'consensus'
                  ? 'bg-brand-500/20 text-brand-700 dark:text-brand-300'
                  : 'bg-emerald-500/20 text-emerald-700 dark:text-brand-emerald'
              }`}
            >
              {activePoint.signalType === 'ingestion' ? (
                <Search className="w-3.5 h-3.5" />
              ) : activePoint.signalType === 'consensus' ? (
                <Sparkles className="w-3.5 h-3.5" />
              ) : (
                <Bell className="w-3.5 h-3.5" />
              )}
            </div>
            <div>
              <div className="flex items-center gap-2 font-mono">
                <span className="text-slate-900 dark:text-white font-bold">{activePoint.date}: ${activePoint.price.toFixed(2)}</span>
                {activePoint.label && (
                  <span className="text-[10px] uppercase font-bold text-brand-700 dark:text-brand-cyan px-1.5 py-0.5 rounded bg-brand-500/10 dark:bg-brand-cyan/10 border border-brand-500/20 dark:border-brand-cyan/20">
                    {activePoint.label}
                  </span>
                )}
              </div>
              <p className="text-slate-600 dark:text-slate-300 text-xs mt-0.5 leading-relaxed">
                {activePoint.signalDetail || 'Baseline price trajectory tracked in continuous telemetry stream.'}
              </p>
            </div>
          </div>

          <div className="text-[11px] font-mono text-slate-500 dark:text-slate-400 bg-surface-200/80 px-2.5 py-1 rounded-lg border border-border-subtle shrink-0">
            Hover point to inspect signal
          </div>
        </div>
      )}

      {/* Fundamental Valuation Multiples Strip */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5 mt-4 pt-4 border-t border-border-subtle text-xs relative z-10">
        <div className="p-2.5 rounded-xl bg-surface-100/80 dark:bg-surface-100/60 border border-border-subtle">
          <span className="text-[10px] text-slate-500 dark:text-slate-400 font-mono uppercase block">Trailing P/E</span>
          <span className="text-sm font-bold text-slate-900 dark:text-white font-mono mt-0.5 block">{activeData.peRatio}</span>
        </div>
        <div className="p-2.5 rounded-xl bg-surface-100/80 dark:bg-surface-100/60 border border-border-subtle">
          <span className="text-[10px] text-slate-500 dark:text-slate-400 font-mono uppercase block">EV / EBITDA</span>
          <span className="text-sm font-bold text-slate-900 dark:text-white font-mono mt-0.5 block">{activeData.evEbitda}</span>
        </div>
        <div className="p-2.5 rounded-xl bg-surface-100/80 dark:bg-surface-100/60 border border-border-subtle">
          <span className="text-[10px] text-slate-500 dark:text-slate-400 font-mono uppercase block">Free Cash Flow Yield</span>
          <span className="text-sm font-bold text-emerald-600 dark:text-brand-emerald font-mono mt-0.5 block">{activeData.fcfYield}</span>
        </div>
        <div className="p-2.5 rounded-xl bg-surface-100/80 dark:bg-surface-100/60 border border-border-subtle">
          <span className="text-[10px] text-slate-500 dark:text-slate-400 font-mono uppercase block">52-Week Range</span>
          <div className="flex items-center gap-2 mt-1">
            <span className="text-[10px] text-slate-500 dark:text-slate-400 font-mono">${activeData.range52w.low}</span>
            <div className="flex-1 h-1.5 rounded-full bg-surface-200 dark:bg-surface-300 relative overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-brand-600 to-cyan-500 rounded-full"
                style={{
                  width: `${
                    ((activeData.range52w.current - activeData.range52w.low) /
                      (activeData.range52w.high - activeData.range52w.low)) *
                    100
                  }%`,
                }}
              />
            </div>
            <span className="text-[10px] text-slate-500 dark:text-slate-400 font-mono">${activeData.range52w.high}</span>
          </div>
        </div>
      </div>
    </div>
  );
};
