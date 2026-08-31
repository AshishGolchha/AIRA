import React, { useState } from 'react';
import {
  Cpu,
  Sparkles,
  TrendingUp,
  AlertTriangle,
  Scale,
  Shield,
  FileCheck,
} from 'lucide-react';

interface DebateRound {
  speaker: string;
  role: string;
  badgeColor: string;
  avatarIcon: React.ElementType;
  perspective: 'thesis' | 'challenge' | 'risk' | 'consensus';
  statement: string;
  citation: string;
}

const DEBATE_SCENARIO: DebateRound[] = [
  {
    speaker: 'Agent 1: Moat & Fundamentals',
    role: 'Senior Equity Analyst',
    badgeColor: 'text-brand-cyan bg-brand-cyan/10 border-brand-cyan/20',
    avatarIcon: TrendingUp,
    perspective: 'thesis',
    statement: 'Data center compute revenue expanded +154% YoY driven by enterprise accelerator demand. Gross margins of 75.1% demonstrate sustained pricing power and high software moat switching costs (CUDA ecosystem).',
    citation: 'Source: SEC 10-Q Filing, Data Center Revenue Segment Table (p. 18)',
  },
  {
    speaker: 'Agent 2: Valuation & Cash Flow',
    role: 'Valuation Specialist',
    badgeColor: 'text-brand-300 bg-brand-500/10 border-brand-500/20',
    avatarIcon: Scale,
    perspective: 'challenge',
    statement: 'While growth is unmatched, trading at 51.8x EV/EBITDA leaves zero margin for execution error. If customer capex growth decelerates from 60% to 25% in FY26, multiple compression could offset earnings growth.',
    citation: 'Source: Financial Statement Ratio Decomposition & Historical Multiple Spread',
  },
  {
    speaker: 'Agent 3: Downside Risk Officer',
    role: 'Macro Risk Officer',
    badgeColor: 'text-amber-400 bg-amber-400/10 border-amber-400/20',
    avatarIcon: AlertTriangle,
    perspective: 'risk',
    statement: 'Customer concentration remains the primary downside vector: top 4 cloud hyperscalers generate ~40% of total company revenue. In-house custom silicon (ASIC) development poses an asymmetric medium-term risk.',
    citation: 'Source: Customer Disclosures & Industry Supply Chain Lead Times',
  },
  {
    speaker: 'Consensus Synthesis Node',
    role: 'Autonomous Intelligence Core',
    badgeColor: 'text-brand-emerald bg-brand-emerald/10 border-brand-emerald/20',
    avatarIcon: Sparkles,
    perspective: 'consensus',
    statement: 'Consensus: Structural growth thesis remains intact for FY25 with high conviction, but concentration risk warrants strict portfolio allocation caps (<20% portfolio weight) and automated 5.0% price move alert telemetry.',
    citation: 'Grounding: Synthesized across 3 agent perspectives and matched to user portfolio context.',
  },
];

export const MultiAgentDebateVisual: React.FC = () => {
  const [activeRoundIdx, setActiveRoundIdx] = useState<number>(3); // default to consensus

  return (
    <div className="w-full max-w-5xl mx-auto rounded-3xl bg-surface-200/90 border border-border-strong p-6 sm:p-8 backdrop-blur-xl font-sans text-left">
      <div className="flex flex-wrap items-center justify-between gap-4 pb-6 mb-6 border-b border-border-subtle">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-brand-500/10 border border-brand-500/30 text-brand-300 text-xs font-semibold uppercase tracking-wider mb-2">
            <Cpu className="w-3.5 h-3.5 text-brand-cyan" />
            <span>Autonomous Multi-Agent Deliberation</span>
          </div>
          <h3 className="text-xl sm:text-2xl font-bold text-white tracking-tight">
            How AIRA Agents Debate & Reach High-Conviction Consensus
          </h3>
        </div>

        {/* Round Switchers */}
        <div className="flex items-center gap-1.5 p-1 rounded-xl bg-surface-100/80 border border-border-subtle text-xs font-mono">
          {DEBATE_SCENARIO.map((_, idx) => {
            const isActive = idx === activeRoundIdx;
            return (
              <button
                key={idx}
                onClick={() => setActiveRoundIdx(idx)}
                className={`px-3 py-1.5 rounded-lg transition-all ${
                  isActive
                    ? 'bg-brand-500 text-white font-bold shadow-glow-brand'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                Agent {idx + 1}
              </button>
            );
          })}
        </div>
      </div>

      {/* Main Debate Dialogue Visual */}
      <div className="space-y-4 mb-6">
        {DEBATE_SCENARIO.map((round, idx) => {
          const isSelected = idx === activeRoundIdx;
          const Icon = round.avatarIcon;
          return (
            <div
              key={idx}
              onClick={() => setActiveRoundIdx(idx)}
              className={`p-4 sm:p-5 rounded-2xl border transition-all cursor-pointer ${
                isSelected
                  ? 'bg-surface-100/90 border-brand-500/50 shadow-glow-card'
                  : 'bg-surface-200/40 border-border-subtle opacity-70 hover:opacity-100 hover:bg-surface-100/50'
              }`}
            >
              <div className="flex flex-wrap items-center justify-between gap-2 mb-2">
                <div className="flex items-center gap-2.5">
                  <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${round.badgeColor}`}>
                    <Icon className="w-4 h-4" />
                  </div>
                  <div>
                    <span className="text-xs font-bold text-white block">{round.speaker}</span>
                    <span className="text-[10px] text-slate-400 font-mono">{round.role}</span>
                  </div>
                </div>
                <span className={`text-[10px] font-mono uppercase px-2 py-0.5 rounded border ${round.badgeColor}`}>
                  {round.perspective}
                </span>
              </div>

              <p className="text-xs sm:text-sm text-slate-200 leading-relaxed mb-3">
                "{round.statement}"
              </p>

              <div className="flex items-center gap-2 text-[11px] font-mono text-slate-400 bg-surface-300/60 p-2 rounded-lg border border-border-subtle">
                <FileCheck className="w-3.5 h-3.5 text-brand-cyan shrink-0" />
                <span>{round.citation}</span>
              </div>
            </div>
          );
        })}
      </div>

      {/* Bottom Summary Bar */}
      <div className="p-4 rounded-2xl bg-brand-500/10 border border-brand-500/20 flex flex-wrap items-center justify-between gap-3 text-xs text-brand-300">
        <div className="flex items-center gap-2">
          <Shield className="w-4 h-4 text-brand-cyan" />
          <span className="font-semibold text-white">Multi-Agent Safeguard:</span>
          <span>No single LLM prompt produces unverified conclusions.</span>
        </div>
        <span className="font-mono text-[11px] text-brand-cyan">Evidence-Grounded Consensus</span>
      </div>
    </div>
  );
};
