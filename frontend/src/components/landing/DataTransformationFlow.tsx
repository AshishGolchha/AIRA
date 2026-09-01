import React, { useState } from 'react';
import {
  Cpu,
  CheckCircle2,
  Sparkles,
} from 'lucide-react';

interface SignalInput {
  id: string;
  type: string;
  source: string;
  rawSnippet: string;
  transformedOutput: string;
}

const SIGNALS: SignalInput[] = [
  {
    id: 'sec',
    type: 'Unstructured Filing',
    source: 'SEC EDGAR 10-Q (48 pages)',
    rawSnippet: '"Data Center segment compute revenue rose to $26,272 million compared with $10,323 million in the prior year..."',
    transformedOutput: 'Verified Metric: $26.3B (+154% YoY). Defensible Blackwell pricing power grounded in filing.',
  },
  {
    id: 'news',
    type: 'Market News Flow',
    source: 'Executive Sentiment & RSS',
    rawSnippet: '"Major cloud hyperscalers reaffirm commitment to AI infrastructure capex expansion despite ROI scrutiny..."',
    transformedOutput: 'Macro Context: Reaffirmed FY25 demand, but elevates hyperscaler concentration exposure.',
  },
  {
    id: 'portfolio',
    type: 'Position Weighting',
    source: 'User Portfolio Holdings',
    rawSnippet: '"Holding: 200 shares @ $95.00 FIFO cost basis. Represents 22.4% of total equity allocation."',
    transformedOutput: 'Deterministic Context: High portfolio concentration (>20%). Suggests conservative rebalance alert.',
  },
  {
    id: 'telemetry',
    type: 'Price Delta Feed',
    source: '15-Second Market Ticks',
    rawSnippet: '"Tick: $128.50 (+3.4%). 24h delta: +5.2%. 52W Range: $45.20 - $140.70."',
    transformedOutput: 'Deterministic Telemetry: Triggered price move rule (>5.0%). Dispatched signed webhook.',
  },
];

export const DataTransformationFlow: React.FC = () => {
  const [activeSignalId, setActiveSignalId] = useState<string>('sec');
  const activeSignal = SIGNALS.find((s) => s.id === activeSignalId) || SIGNALS[0];

  return (
    <div className="w-full max-w-5xl mx-auto rounded-3xl bg-surface-50/95 dark:bg-surface-200/90 border border-border-strong p-6 sm:p-8 backdrop-blur-xl font-sans text-left relative overflow-hidden shadow-xl dark:shadow-2xl transition-colors duration-200">
      {/* Circuit background */}
      <div className="absolute inset-0 bg-grid-pattern opacity-40 dark:opacity-25 pointer-events-none" />

      {/* Header */}
      <div className="text-center max-w-3xl mx-auto mb-8 relative z-10">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-brand-500/10 border border-brand-500/30 text-brand-700 dark:text-brand-300 text-xs font-semibold uppercase tracking-wider mb-2">
          <Sparkles className="w-3.5 h-3.5 text-brand-600 dark:text-brand-cyan" />
          <span>Continuous Intelligence Pipeline</span>
        </div>
        <h3 className="text-2xl sm:text-3xl font-extrabold text-slate-900 dark:text-white tracking-tight mb-2">
          From Chaotic Market Noise to Grounded Intelligence
        </h3>
        <p className="text-slate-600 dark:text-slate-300 text-xs sm:text-sm">
          Watch how messy financial documents and price feeds transform into verified, actionable investment decisions.
        </p>
      </div>

      {/* 3-Stage Pipeline Convergence */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-5 items-stretch relative z-10 mb-6">
        {/* ========================================================================= */}
        {/* STAGE 1: RAW SIGNALS (Left 4 cols) */}
        {/* ========================================================================= */}
        <div className="lg:col-span-4 p-4 rounded-2xl bg-surface-100 dark:bg-surface-100/80 border border-border-subtle flex flex-col justify-between space-y-3">
          <div>
            <div className="flex items-center justify-between pb-2 mb-3 border-b border-border-subtle">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-700 dark:text-slate-300">
                1. Raw Signals
              </span>
              <span className="text-[10px] font-mono text-slate-500 dark:text-slate-400">UNSTRUCTURED</span>
            </div>

            <div className="space-y-2">
              {SIGNALS.map((sig) => {
                const isSelected = sig.id === activeSignalId;
                return (
                  <button
                    key={sig.id}
                    onClick={() => setActiveSignalId(sig.id)}
                    className={`w-full text-left p-2.5 rounded-xl border transition-all text-xs ${
                      isSelected
                        ? 'bg-brand-500/15 dark:bg-brand-500/20 border-brand-500 text-slate-900 dark:text-white shadow-sm dark:shadow-glow-brand'
                        : 'bg-surface-50 dark:bg-surface-200/50 border-border-subtle text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200'
                    }`}
                  >
                    <div className="font-semibold text-slate-900 dark:text-white truncate">{sig.type}</div>
                    <div className="text-[10px] text-slate-500 dark:text-slate-400 font-mono truncate">{sig.source}</div>
                  </button>
                );
              })}
            </div>
          </div>

          <div className="p-2.5 rounded-xl bg-surface-50 dark:bg-surface-300/80 border border-border-subtle text-[11px] font-mono text-slate-600 dark:text-slate-400 italic">
            {activeSignal.rawSnippet}
          </div>
        </div>

        {/* ========================================================================= */}
        {/* STAGE 2: AIRA PROCESSING CORE (Center 4 cols) */}
        {/* ========================================================================= */}
        <div className="lg:col-span-4 p-5 rounded-2xl bg-gradient-to-b from-surface-100 to-surface-200 dark:from-surface-100 dark:to-surface-300 border border-brand-500/40 shadow-sm dark:shadow-glow-brand flex flex-col justify-between space-y-4">
          <div>
            <div className="flex items-center justify-between pb-2 mb-3 border-b border-border-subtle">
              <div className="flex items-center gap-1.5 text-xs font-bold uppercase tracking-wider text-slate-900 dark:text-white">
                <Cpu className="w-3.5 h-3.5 text-brand-600 dark:text-brand-cyan" />
                <span>2. Processing Core</span>
              </div>
              <span className="text-[10px] font-mono text-brand-700 dark:text-brand-cyan bg-brand-500/10 dark:bg-brand-cyan/10 px-2 py-0.5 rounded border border-brand-500/20 dark:border-brand-cyan/20">
                AUTONOMOUS
              </span>
            </div>

            <div className="space-y-2 text-xs">
              <div className="p-2 rounded-xl bg-surface-50 dark:bg-surface-200/70 border border-border-subtle flex items-center justify-between">
                <span className="text-slate-700 dark:text-slate-300">Semantic Parsing</span>
                <span className="font-mono text-[10px] text-brand-600 dark:text-brand-cyan">pgvector</span>
              </div>
              <div className="p-2 rounded-xl bg-surface-50 dark:bg-surface-200/70 border border-border-subtle flex items-center justify-between">
                <span className="text-slate-700 dark:text-slate-300">Multi-Agent Debate</span>
                <span className="font-mono text-[10px] text-brand-700 dark:text-brand-300">CrewAI</span>
              </div>
              <div className="p-2 rounded-xl bg-surface-50 dark:bg-surface-200/70 border border-border-subtle flex items-center justify-between">
                <span className="text-slate-700 dark:text-slate-300">Deterministic Math</span>
                <span className="font-mono text-[10px] text-emerald-600 dark:text-brand-emerald">SQL Certainty</span>
              </div>
            </div>
          </div>

          <div className="p-2.5 rounded-xl bg-brand-500/10 border border-brand-500/30 text-center text-[11px] font-mono text-brand-700 dark:text-brand-cyan font-bold">
            Zero Hallucination Pipeline
          </div>
        </div>

        {/* ========================================================================= */}
        {/* STAGE 3: ACTIONABLE INTELLIGENCE (Right 4 cols) */}
        {/* ========================================================================= */}
        <div className="lg:col-span-4 p-4 rounded-2xl bg-surface-100 dark:bg-surface-100/80 border border-emerald-500/40 dark:border-brand-emerald/40 flex flex-col justify-between space-y-3">
          <div>
            <div className="flex items-center justify-between pb-2 mb-3 border-b border-border-subtle">
              <span className="text-xs font-bold uppercase tracking-wider text-emerald-700 dark:text-brand-emerald">
                3. Actionable Output
              </span>
              <span className="text-[10px] font-mono text-emerald-700 dark:text-brand-emerald bg-emerald-500/10 dark:bg-brand-emerald/10 px-2 py-0.5 rounded border border-emerald-500/20 dark:border-emerald-500/20">
                GROUNDED
              </span>
            </div>

            <div className="p-3 rounded-xl bg-surface-50 dark:bg-surface-200/90 border border-border-subtle text-xs text-slate-900 dark:text-white leading-relaxed">
              <CheckCircle2 className="w-4 h-4 text-emerald-600 dark:text-brand-emerald inline mr-1.5 shrink-0" />
              {activeSignal.transformedOutput}
            </div>
          </div>

          <div className="p-2.5 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-[11px] font-mono text-emerald-700 dark:text-brand-emerald flex items-center justify-between">
            <span>Synthesis Latency</span>
            <strong>&lt;450ms</strong>
          </div>
        </div>
      </div>
    </div>
  );
};
