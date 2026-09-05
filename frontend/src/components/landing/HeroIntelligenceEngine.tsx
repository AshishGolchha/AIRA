import React, { useState } from 'react';
import {
  Cpu,
  Search,
  CheckCircle2,
  PieChart,
  ShieldAlert,
  Activity,
  FileText,
  Sparkles,
  RefreshCw,
  Zap,
} from 'lucide-react';

interface TickerScenario {
  ticker: string;
  name: string;
  price: string;
  change: string;
  changePositive: boolean;
  pe: string;
  evEbitda: string;
  marketCap: string;
  activeSignals: string[];
  agents: {
    role: string;
    focus: string;
    sentiment: 'bullish' | 'neutral' | 'cautious';
    quote: string;
  }[];
  synthesis: {
    verdict: string;
    conviction: string;
    keyCatalyst: string;
    riskFactor: string;
    portfolioContext: string;
    deterministicRule: string;
  };
}

const SCENARIOS: Record<string, TickerScenario> = {
  NVDA: {
    ticker: 'NVDA',
    name: 'NVIDIA Corporation',
    price: '₹128.50',
    change: '+3.4%',
    changePositive: true,
    pe: '64.2x',
    evEbitda: '51.8x',
    marketCap: '$3.16T',
    activeSignals: [
      'SEC 10-Q: Data Center revenue reached $26.3B (+154% YoY)',
      'Gross margin expanded to 75.1% on Blackwell ramp',
      'Hyperscaler capex guidance raised across top 4 customers',
    ],
    agents: [
      {
        role: 'Fundamental Analyst',
        focus: 'Pricing Power & Moat',
        sentiment: 'bullish',
        quote: 'CUDA software ecosystem and NVLink interconnect maintain multi-year switching cost defensibility.',
      },
      {
        role: 'Valuation Specialist',
        focus: 'Multiples & Cash Flow',
        sentiment: 'neutral',
        quote: 'Trading at 51.8x EV/EBITDA; near-term pricing assumes sustained >70% gross margins through FY26.',
      },
      {
        role: 'Macro Risk Officer',
        focus: 'Supply Chain & Concentration',
        sentiment: 'cautious',
        quote: 'Top 4 cloud hyperscalers generate ~40% of revenue; vulnerable to capex digestion cycles.',
      },
    ],
    synthesis: {
      verdict: 'High-Conviction Structural Growth with Concentration Risk',
      conviction: '88% Grounded',
      keyCatalyst: 'Blackwell ultra-scale data center cluster deliveries in Q3/Q4.',
      riskFactor: 'Hyperscaler capex moderation and sovereign export restriction friction.',
      portfolioContext: 'Current holding weight: 18.5% of total portfolio. Within moderate tolerance threshold.',
      deterministicRule: 'Price Alert: Trigger if 24h delta exceeds ±5.0% (₹122.08 / ₹134.92).',
    },
  },
  AAPL: {
    ticker: 'AAPL',
    name: 'Apple Inc.',
    price: '₹224.20',
    change: '+0.8%',
    changePositive: true,
    pe: '33.1x',
    evEbitda: '24.6x',
    marketCap: '$3.42T',
    activeSignals: [
      'Services segment revenue hit all-time record $24.2B with 74% gross margin',
      'Installed base surpassed 2.2 billion active devices globally',
      'Greater China revenue stabilized with localized AI features',
    ],
    agents: [
      {
        role: 'Fundamental Analyst',
        focus: 'Ecosystem & Services',
        sentiment: 'bullish',
        quote: 'Services mix shift drives recurring revenue quality and multi-year gross margin expansion.',
      },
      {
        role: 'Valuation Specialist',
        focus: 'Share Buybacks & Multiple',
        sentiment: 'neutral',
        quote: 'P/E multiple expanded from 25x to 33x. Aggressive $110B annual capital return provides floor.',
      },
      {
        role: 'Macro Risk Officer',
        focus: 'Regulatory & Hardware Cycle',
        sentiment: 'cautious',
        quote: 'DOJ antitrust inquiry into App Store revenue share creates potential 5-8% EBITDA margin headwind.',
      },
    ],
    synthesis: {
      verdict: 'Defensive Quality Compounder with Capital Return Moat',
      conviction: '84% Grounded',
      keyCatalyst: 'Apple Intelligence rollout driving multi-year iPhone upgrade supercycle.',
      riskFactor: 'App Store regulatory scrutiny in US and EU DMA enforcement.',
      portfolioContext: 'Current holding weight: 22.0% of total portfolio. Core anchor position.',
      deterministicRule: 'Drawdown Alert: Trigger if position dips below 200-day moving avg (₹208.50).',
    },
  },
  MSFT: {
    ticker: 'MSFT',
    name: 'Microsoft Corporation',
    price: '₹418.00',
    change: '-0.4%',
    changePositive: false,
    pe: '34.8x',
    evEbitda: '23.2x',
    marketCap: '$3.11T',
    activeSignals: [
      'Azure Cloud revenue growth +29% with 8 points attributed directly to AI services',
      'Copilot seat deployments expanded 60% QoQ in Fortune 500 accounts',
      'Capital expenditures reached $19B/quarter dedicated to AI data centers',
    ],
    agents: [
      {
        role: 'Fundamental Analyst',
        focus: 'Enterprise Cloud Dominance',
        sentiment: 'bullish',
        quote: 'Azure enterprise distribution and Office 365 installed base create unmatched AI distribution velocity.',
      },
      {
        role: 'Valuation Specialist',
        focus: 'Capex ROI & Multiples',
        sentiment: 'cautious',
        quote: 'Elevated quarterly capex ($19B) creates near-term free cash flow margin compression.',
      },
      {
        role: 'Macro Risk Officer',
        focus: 'Capacity Bottlenecks',
        sentiment: 'neutral',
        quote: 'GPU capacity constraints remain the primary limiter for Azure AI revenue upside in H1.',
      },
    ],
    synthesis: {
      verdict: 'Enterprise AI Leader Balancing Capex Intensity with Monetization',
      conviction: '86% Grounded',
      keyCatalyst: 'Commercial cloud acceleration and Copilot enterprise monetization ramp.',
      riskFactor: 'Capex depreciation pressure if enterprise AI inference ROI lags infrastructure spend.',
      portfolioContext: 'Current holding weight: 14.2% of total portfolio. High-quality thematic anchor.',
      deterministicRule: 'Price Alert: Trigger if 24h delta exceeds ±4.5% (₹399.19 / ₹436.81).',
    },
  },
};

export const HeroIntelligenceEngine: React.FC = () => {
  const [selectedTicker, setSelectedTicker] = useState<string>('NVDA');
  const [activeAgentIdx, setActiveAgentIdx] = useState<number>(0);
  const [isSynthesizing, setIsSynthesizing] = useState<boolean>(false);

  const current = SCENARIOS[selectedTicker] || SCENARIOS.NVDA;

  const handleTickerChange = (ticker: string) => {
    if (ticker === selectedTicker) return;
    setIsSynthesizing(true);
    setSelectedTicker(ticker);
    setActiveAgentIdx(0);
    setTimeout(() => {
      setIsSynthesizing(false);
    }, 400);
  };

  return (
    <div className="rounded-3xl border border-border-strong bg-surface-50/95 dark:bg-surface-300/90 backdrop-blur-2xl shadow-xl dark:shadow-glow-brand overflow-hidden text-left relative transition-all duration-300">
      {/* Simulation Banner & Ticker Scenario Switcher */}
      <div className="px-4 sm:px-6 py-3.5 bg-surface-100/80 dark:bg-surface-400/80 border-b border-border-subtle flex flex-wrap items-center justify-between gap-3">
        {/* Ticker Selector Buttons */}
        <div className="flex items-center gap-2">
          <span className="text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400 mr-1 hidden sm:inline">
            Active Research Target:
          </span>
          {Object.keys(SCENARIOS).map((ticker) => {
            const isActive = ticker === selectedTicker;
            return (
              <button
                key={ticker}
                onClick={() => handleTickerChange(ticker)}
                className={`px-3 py-1 rounded-lg text-xs font-mono font-bold transition-all duration-200 focus:outline-none focus-visible:ring-2 focus-visible:ring-brand-400 ${
                  isActive
                    ? 'bg-brand-600 text-white shadow-sm dark:shadow-glow-brand'
                    : 'bg-surface-200 dark:bg-surface-100/60 text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200 hover:bg-surface-200'
                }`}
              >
                ${ticker}
              </button>
            );
          })}
        </div>

        {/* Live Engine Status Indicators */}
        <div className="flex items-center gap-3 text-[11px] font-mono text-slate-500 dark:text-slate-400">
          <div className="hidden sm:flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-surface-50 dark:bg-surface-100/80 border border-border-subtle">
            <Cpu className="w-3 h-3 text-brand-600 dark:text-brand-cyan" />
            <span>3 Agents Reasoning</span>
          </div>
          <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-surface-50 dark:bg-surface-100/80 border border-border-subtle">
            <Activity className="w-3 h-3 text-emerald-600 dark:text-brand-emerald" />
            <span className="text-slate-700 dark:text-slate-300">Deterministic Rules: <strong className="text-emerald-600 dark:text-brand-emerald font-normal">Active</strong></span>
          </div>
        </div>
      </div>

      {/* Target Asset Header Overview */}
      <div className="px-4 sm:px-6 py-4 bg-surface-100/40 dark:bg-surface-200/50 border-b border-border-subtle flex flex-wrap items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2.5">
            <h2 className="text-xl sm:text-2xl font-black text-slate-900 dark:text-white tracking-tight font-sans">
              {current.name} <span className="text-brand-600 dark:text-brand-cyan font-mono font-bold text-base">({current.ticker})</span>
            </h2>
            <span className={`px-2 py-0.5 rounded text-xs font-mono font-bold ${
              current.changePositive ? 'bg-emerald-500/10 text-emerald-700 dark:text-brand-emerald border border-emerald-500/20' : 'bg-rose-500/10 text-rose-700 dark:text-rose-400 border border-rose-500/20'
            }`}>
              {current.price} ({current.change})
            </span>
          </div>
        </div>

        {/* Quick Fundamental Badges */}
        <div className="flex items-center gap-3 font-mono text-xs">
          <div className="px-2.5 py-1 rounded-lg bg-surface-50 dark:bg-surface-100/70 border border-border-subtle">
            <span className="text-slate-500 text-[10px] block uppercase">Trailing P/E</span>
            <span className="text-slate-900 dark:text-white font-bold">{current.pe}</span>
          </div>
          <div className="px-2.5 py-1 rounded-lg bg-surface-50 dark:bg-surface-100/70 border border-border-subtle">
            <span className="text-slate-500 text-[10px] block uppercase">EV / EBITDA</span>
            <span className="text-slate-900 dark:text-white font-bold">{current.evEbitda}</span>
          </div>
          <div className="hidden sm:block px-2.5 py-1 rounded-lg bg-surface-50 dark:bg-surface-100/70 border border-border-subtle">
            <span className="text-slate-500 text-[10px] block uppercase">Market Cap</span>
            <span className="text-slate-900 dark:text-white font-bold">{current.marketCap}</span>
          </div>
        </div>
      </div>

      {/* 3-Column Connected Engine Visual */}
      <div className={`p-4 sm:p-6 grid grid-cols-1 lg:grid-cols-12 gap-5 transition-opacity duration-300 ${isSynthesizing ? 'opacity-50' : 'opacity-100'}`}>
        {/* ========================================================= */}
        {/* COLUMN 1 (Left, 4 cols): INGESTION & EVIDENCE STREAM */}
        {/* ========================================================= */}
        <div className="lg:col-span-4 flex flex-col justify-between space-y-4">
          <div>
            <div className="flex items-center justify-between pb-2 mb-3 border-b border-border-subtle">
              <div className="flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wider text-slate-700 dark:text-slate-300">
                <Search className="w-3.5 h-3.5 text-brand-600 dark:text-brand-cyan" />
                <span>1. Verified Ingestion Stream</span>
              </div>
              <span className="text-[10px] font-mono text-slate-500 dark:text-slate-400">10-Q & Telemetry</span>
            </div>

            <div className="space-y-2.5">
              {current.activeSignals.map((signal, idx) => (
                <div
                  key={idx}
                  className="p-2.5 rounded-xl bg-surface-100/80 dark:bg-surface-100/60 border border-border-subtle hover:border-brand-500/30 transition-all text-xs text-slate-700 dark:text-slate-300 leading-relaxed flex items-start gap-2"
                >
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 dark:text-brand-emerald shrink-0 mt-0.5" />
                  <span>{signal}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Connected Conduit Indicator */}
          <div className="p-3 rounded-xl bg-brand-500/10 border border-brand-500/20 flex items-center justify-between text-xs text-brand-700 dark:text-brand-300">
            <div className="flex items-center gap-2">
              <RefreshCw className="w-3.5 h-3.5 text-brand-600 dark:text-brand-cyan animate-spin" style={{ animationDuration: '8s' }} />
              <span className="font-medium">Continuous Ingestion Active</span>
            </div>
            <span className="font-mono text-[10px] text-brand-600 dark:text-brand-cyan">ZERO HALLUCINATION</span>
          </div>
        </div>

        {/* ========================================================= */}
        {/* COLUMN 2 (Center, 4 cols): MULTI-AGENT REASONING CORE */}
        {/* ========================================================= */}
        <div className="lg:col-span-4 flex flex-col justify-between space-y-4 border-y lg:border-y-0 lg:border-x border-border-subtle py-4 lg:py-0 lg:px-4">
          <div>
            <div className="flex items-center justify-between pb-2 mb-3 border-b border-border-subtle">
              <div className="flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wider text-slate-700 dark:text-slate-300">
                <Cpu className="w-3.5 h-3.5 text-brand-600 dark:text-brand-500" />
                <span>2. Multi-Agent Reasoning Core</span>
              </div>
              <span className="text-[10px] font-mono text-brand-600 dark:text-brand-cyan">CrewAI + Gemini</span>
            </div>

            {/* Agent Selectors */}
            <div className="space-y-2 mb-3">
              {current.agents.map((agent, idx) => {
                const isActive = idx === activeAgentIdx;
                return (
                  <button
                    key={idx}
                    onClick={() => setActiveAgentIdx(idx)}
                    className={`w-full text-left p-2.5 rounded-xl border transition-all duration-200 flex items-center justify-between ${
                      isActive
                        ? 'bg-brand-500/10 dark:bg-brand-500/15 border-brand-500/50 text-slate-900 dark:text-white shadow-sm dark:shadow-glow-brand'
                        : 'bg-surface-100/60 dark:bg-surface-100/40 border-border-subtle text-slate-600 dark:text-slate-400 hover:bg-surface-100 hover:text-slate-900 dark:hover:text-slate-200'
                    }`}
                  >
                    <div className="flex items-center gap-2">
                      <div className={`w-2 h-2 rounded-full ${
                        agent.sentiment === 'bullish' ? 'bg-emerald-500 dark:bg-brand-emerald' : agent.sentiment === 'cautious' ? 'bg-amber-500 dark:bg-amber-400' : 'bg-brand-600 dark:bg-brand-cyan'
                      }`} />
                      <span className="text-xs font-semibold font-sans">{agent.role}</span>
                    </div>
                    <span className="text-[10px] font-mono uppercase text-slate-500 dark:text-slate-400">{agent.focus}</span>
                  </button>
                );
              })}
            </div>

            {/* Active Agent Dialogue Box */}
            <div className="p-3 rounded-xl bg-surface-100 dark:bg-surface-300/80 border border-border-subtle text-xs text-slate-700 dark:text-slate-300 leading-relaxed font-sans relative">
              <div className="text-[10px] font-mono font-semibold uppercase text-brand-600 dark:text-brand-cyan mb-1 flex items-center gap-1">
                <Sparkles className="w-3 h-3" />
                <span>{current.agents[activeAgentIdx].role} Findings:</span>
              </div>
              <p className="italic text-slate-800 dark:text-slate-200">
                "{current.agents[activeAgentIdx].quote}"
              </p>
            </div>
          </div>

          <div className="text-[10px] text-center font-mono text-slate-500 dark:text-slate-400 flex items-center justify-center gap-2">
            <span className="w-1.5 h-1.5 rounded-full bg-brand-600 dark:bg-brand-cyan" />
            <span>Agent Consensus Convergence: <strong>94.2%</strong></span>
          </div>
        </div>

        {/* ========================================================= */}
        {/* COLUMN 3 (Right, 4 cols): GROUNDED SYNTHESIS & TELEMETRY */}
        {/* ========================================================= */}
        <div className="lg:col-span-4 flex flex-col justify-between space-y-4">
          <div>
            <div className="flex items-center justify-between pb-2 mb-3 border-b border-border-subtle">
              <div className="flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wider text-slate-700 dark:text-slate-300">
                <Zap className="w-3.5 h-3.5 text-emerald-600 dark:text-brand-emerald" />
                <span>3. Grounded Synthesis</span>
              </div>
              <span className="text-[10px] font-mono text-emerald-700 dark:text-brand-emerald font-semibold">{current.synthesis.conviction}</span>
            </div>

            {/* Structured Synthesis Summary */}
            <div className="p-3 rounded-xl bg-surface-100/90 dark:bg-surface-100/70 border border-border-subtle space-y-2 mb-3">
              <div className="text-xs font-bold text-slate-900 dark:text-white font-sans">
                {current.synthesis.verdict}
              </div>
              <div className="text-[11px] text-slate-700 dark:text-slate-300 font-sans leading-tight">
                <span className="text-brand-600 dark:text-brand-cyan font-semibold">Catalyst: </span>
                {current.synthesis.keyCatalyst}
              </div>
              <div className="text-[11px] text-slate-700 dark:text-slate-300 font-sans leading-tight">
                <span className="text-amber-700 dark:text-amber-300 font-semibold">Risk: </span>
                {current.synthesis.riskFactor}
              </div>
            </div>

            {/* Portfolio Grounding & Deterministic Alert Rule */}
            <div className="space-y-2">
              <div className="p-2.5 rounded-xl bg-surface-100/60 dark:bg-surface-100/40 border border-border-subtle flex items-start gap-2 text-xs text-slate-700 dark:text-slate-300">
                <PieChart className="w-3.5 h-3.5 text-brand-600 dark:text-brand-cyan shrink-0 mt-0.5" />
                <span className="text-[11px]">{current.synthesis.portfolioContext}</span>
              </div>
              <div className="p-2.5 rounded-xl bg-surface-100/60 dark:bg-surface-100/40 border border-border-subtle flex items-start gap-2 text-xs text-slate-700 dark:text-slate-300">
                <ShieldAlert className="w-3.5 h-3.5 text-emerald-600 dark:text-brand-emerald shrink-0 mt-0.5" />
                <span className="text-[11px] font-mono text-slate-700 dark:text-slate-300">{current.synthesis.deterministicRule}</span>
              </div>
            </div>
          </div>

          <div className="pt-2 flex items-center justify-between text-[10px] font-mono text-slate-500 dark:text-slate-400">
            <span>Vector Indexed (#8429)</span>
            <span className="text-emerald-700 dark:text-brand-emerald font-semibold">Ready for Decision</span>
          </div>
        </div>
      </div>

      {/* Console Bottom Bar */}
      <div className="px-4 sm:px-6 py-2.5 bg-surface-100/90 dark:bg-surface-400/90 border-t border-border-subtle flex flex-wrap items-center justify-between text-[11px] text-slate-500 dark:text-slate-400 font-mono">
        <div className="flex items-center gap-2">
          <FileText className="w-3 h-3 text-brand-600 dark:text-brand-cyan" />
          <span>AIRA Autonomous Research Engine • Evidence Verified</span>
        </div>
        <span className="text-slate-500 dark:text-slate-400">Illustrative Live Simulator Preview</span>
      </div>
    </div>
  );
};
