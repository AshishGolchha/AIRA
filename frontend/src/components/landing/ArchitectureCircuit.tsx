import React, { useState } from 'react';
import {
  Cpu,
  Shield,
  Zap,
  CheckCircle2,
  PieChart,
  Bell,
  Search,
  Sparkles,
  ArrowRight,
} from 'lucide-react';

interface ModuleDetail {
  id: string;
  tier: 'ai' | 'deterministic' | 'convergence';
  title: string;
  tag: string;
  description: string;
  guarantee: string;
  rules: string[];
}

const MODULES: Record<string, ModuleDetail> = {
  'ai-synthesis': {
    id: 'ai-synthesis',
    tier: 'ai',
    title: 'Multi-Agent Qualitative Reasoning',
    tag: 'CrewAI + Gemini 2.0',
    description: 'Autonomous agents examine SEC disclosures, executive commentary, moat durability, and supply chain dependencies.',
    guarantee: 'All claims grounded directly in cited evidentiary text blocks.',
    rules: [
      'Specialized agent roles: Fundamental, Valuation, and Macro Risk analysts',
      'Continuous debate rounds to eliminate single-prompt biases',
      'Vector semantic memory (pgvector) ensures historical continuity',
    ],
  },
  'ai-evidence': {
    id: 'ai-evidence',
    tier: 'ai',
    title: 'Evidence Verification & Extraction',
    tag: 'Corpus Parsing',
    description: 'Extracts exact quantitative figures and quote citations from 10-K, 10-Q, and earnings transcripts.',
    guarantee: 'Every thesis insight maps to a verifiable source filing.',
    rules: [
      'Direct semantic chunking of financial reports',
      'Fact-checking agent validates citations prior to report generation',
      'Provenance metadata stamped onto every intelligence record',
    ],
  },
  'det-math': {
    id: 'det-math',
    tier: 'deterministic',
    title: 'Mathematical Portfolio Valuation',
    tag: 'Python & SQLAlchemy',
    description: 'Calculates portfolio market value, FIFO cost-basis accounting, unrealized profit & loss %, and asset concentration weights.',
    guarantee: 'Zero LLM participation in mathematical calculations.',
    rules: [
      'Executed deterministically via standard financial arithmetic',
      'Instant sub-10ms snapshot calculation on dashboard requests',
      'Multi-tenant database isolation enforced at the query level',
    ],
  },
  'det-alerts': {
    id: 'det-alerts',
    tier: 'deterministic',
    title: 'Threshold Monitoring & Retry Engine',
    tag: 'Idempotent Dispatcher',
    description: 'Evaluates real-time price deltas, 52-week extremes, and portfolio drawdowns against strict numeric thresholds.',
    guarantee: 'Guaranteed delivery with exponential retry backoff and SSRF protection.',
    rules: [
      'Sliding-window rule verification without stochastic AI drift',
      'Multi-channel dispatch (In-App, Email, HMAC-signed Webhooks)',
      'Exponential backoff with automated retry recovery',
    ],
  },
  'convergence': {
    id: 'convergence',
    tier: 'convergence',
    title: 'Grounded Investment Intelligence Layer',
    tag: 'Unified Output',
    description: 'Combines verified qualitative agent consensus with exact mathematical portfolio weights for trustworthy decision support.',
    guarantee: 'Institutional-grade reliability: qualitative insight + numeric precision.',
    rules: [
      'Personalized to investor risk tolerance (Conservative, Moderate, Aggressive)',
      'Asset weighting directly flags portfolio concentration risk',
      'Immutable audit history saved for verifiable long-term review',
    ],
  },
};

export const ArchitectureCircuit: React.FC = () => {
  const [selectedModuleId, setSelectedModuleId] = useState<string>('convergence');
  const active = MODULES[selectedModuleId] || MODULES.convergence;

  return (
    <div className="w-full max-w-6xl mx-auto rounded-3xl bg-surface-50/95 dark:bg-surface-200/90 border border-border-strong p-6 sm:p-8 lg:p-10 backdrop-blur-xl relative overflow-hidden font-sans text-left shadow-xl dark:shadow-2xl transition-colors duration-200">
      {/* Background circuit lines */}
      <div className="absolute inset-0 bg-grid-pattern opacity-40 dark:opacity-30 pointer-events-none" />

      {/* Header Statement */}
      <div className="text-center max-w-3xl mx-auto mb-10 relative z-10">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-brand-500/10 border border-brand-500/30 text-brand-700 dark:text-brand-300 text-xs font-semibold uppercase tracking-wider mb-3">
          <Shield className="w-3.5 h-3.5 text-brand-600 dark:text-brand-cyan" />
          <span>The AIRA Architectural Differentiator</span>
        </div>
        <h3 className="text-2xl sm:text-4xl font-extrabold text-slate-900 dark:text-white tracking-tight mb-3">
          Why AIRA Is Not "ChatGPT for Stocks"
        </h3>
        <p className="text-slate-600 dark:text-slate-300 text-sm sm:text-base leading-relaxed">
          AIRA separates qualitative AI reasoning from deterministic mathematical calculations to eliminate hallucination and deliver institutional-grade certainty.
        </p>
      </div>

      {/* Visual 3-Way Circuit Convergence Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 relative z-10 mb-8 items-stretch">
        {/* ========================================================= */}
        {/* TIER 1 (Left 4 cols): AUTONOMOUS AI REASONING TIER */}
        {/* ========================================================= */}
        <div className="lg:col-span-4 flex flex-col justify-between p-5 rounded-2xl bg-surface-100 dark:bg-surface-100/70 border border-brand-500/30 space-y-4">
          <div>
            <div className="flex items-center justify-between pb-3 mb-3 border-b border-border-subtle">
              <div className="flex items-center gap-2">
                <div className="w-7 h-7 rounded-lg bg-brand-500/20 flex items-center justify-center text-brand-600 dark:text-brand-cyan">
                  <Cpu className="w-4 h-4" />
                </div>
                <span className="text-xs font-bold uppercase tracking-wider text-slate-900 dark:text-white">
                  Autonomous AI Tier
                </span>
              </div>
              <span className="text-[10px] font-mono text-brand-700 dark:text-brand-cyan bg-brand-500/10 dark:bg-brand-cyan/10 px-2 py-0.5 rounded border border-brand-500/20 dark:border-brand-cyan/20">
                QUALITATIVE
              </span>
            </div>

            <p className="text-xs text-slate-600 dark:text-slate-400 mb-4 leading-relaxed">
              Applied strictly to narrative synthesis, competitive moat evaluations, and evidence-grounded thesis discovery.
            </p>

            <div className="space-y-2.5">
              <button
                onClick={() => setSelectedModuleId('ai-synthesis')}
                className={`w-full text-left p-3 rounded-xl border transition-all text-xs ${
                  selectedModuleId === 'ai-synthesis'
                    ? 'bg-brand-500/15 dark:bg-brand-500/20 border-brand-500 text-slate-900 dark:text-white shadow-sm dark:shadow-glow-brand'
                    : 'bg-surface-50 dark:bg-surface-200/50 border-border-subtle text-slate-700 dark:text-slate-300 hover:bg-surface-200/60'
                }`}
              >
                <div className="flex items-center justify-between font-semibold mb-1">
                  <span>Multi-Agent Reasoning</span>
                  <Sparkles className="w-3 h-3 text-brand-600 dark:text-brand-cyan" />
                </div>
                <span className="text-[11px] text-slate-500 dark:text-slate-400 block">CrewAI consensus across 3 analytical roles.</span>
              </button>

              <button
                onClick={() => setSelectedModuleId('ai-evidence')}
                className={`w-full text-left p-3 rounded-xl border transition-all text-xs ${
                  selectedModuleId === 'ai-evidence'
                    ? 'bg-brand-500/15 dark:bg-brand-500/20 border-brand-500 text-slate-900 dark:text-white shadow-sm dark:shadow-glow-brand'
                    : 'bg-surface-50 dark:bg-surface-200/50 border-border-subtle text-slate-700 dark:text-slate-300 hover:bg-surface-200/60'
                }`}
              >
                <div className="flex items-center justify-between font-semibold mb-1">
                  <span>Evidence Verification</span>
                  <Search className="w-3 h-3 text-brand-600 dark:text-brand-cyan" />
                </div>
                <span className="text-[11px] text-slate-500 dark:text-slate-400 block">Citations extracted from SEC 10-K & 10-Q filings.</span>
              </button>
            </div>
          </div>

          <div className="pt-3 border-t border-border-subtle text-[11px] font-mono text-brand-700 dark:text-brand-cyan flex items-center gap-1.5 font-medium">
            <CheckCircle2 className="w-3.5 h-3.5 text-brand-600 dark:text-brand-cyan shrink-0" />
            <span>Hallucination Guards Enforced</span>
          </div>
        </div>

        {/* ========================================================= */}
        {/* TIER 2 (Right 4 cols): DETERMINISTIC SYSTEM TIER */}
        {/* ========================================================= */}
        <div className="lg:col-span-4 flex flex-col justify-between p-5 rounded-2xl bg-surface-100 dark:bg-surface-100/70 border border-emerald-500/30 dark:border-brand-emerald/30 space-y-4">
          <div>
            <div className="flex items-center justify-between pb-3 mb-3 border-b border-border-subtle">
              <div className="flex items-center gap-2">
                <div className="w-7 h-7 rounded-lg bg-emerald-500/20 dark:bg-brand-emerald/20 flex items-center justify-center text-emerald-600 dark:text-brand-emerald">
                  <Shield className="w-4 h-4" />
                </div>
                <span className="text-xs font-bold uppercase tracking-wider text-slate-900 dark:text-white">
                  Deterministic Tier
                </span>
              </div>
              <span className="text-[10px] font-mono text-emerald-700 dark:text-brand-emerald bg-emerald-500/10 dark:bg-brand-emerald/10 px-2 py-0.5 rounded border border-emerald-500/20 dark:border-emerald-500/20">
                NUMERIC MATH
              </span>
            </div>

            <p className="text-xs text-slate-600 dark:text-slate-400 mb-4 leading-relaxed">
              Applied to all mathematical calculations, alert thresholds, authorization guards, and webhook retry mechanics.
            </p>

            <div className="space-y-2.5">
              <button
                onClick={() => setSelectedModuleId('det-math')}
                className={`w-full text-left p-3 rounded-xl border transition-all text-xs ${
                  selectedModuleId === 'det-math'
                    ? 'bg-emerald-500/15 dark:bg-brand-emerald/20 border-emerald-500 dark:border-brand-emerald text-slate-900 dark:text-white shadow-sm dark:shadow-glow-emerald'
                    : 'bg-surface-50 dark:bg-surface-200/50 border-border-subtle text-slate-700 dark:text-slate-300 hover:bg-surface-200/60'
                }`}
              >
                <div className="flex items-center justify-between font-semibold mb-1">
                  <span>Portfolio Valuation Math</span>
                  <PieChart className="w-3 h-3 text-emerald-600 dark:text-brand-emerald" />
                </div>
                <span className="text-[11px] text-slate-500 dark:text-slate-400 block">Exact FIFO cost basis and asset weighting.</span>
              </button>

              <button
                onClick={() => setSelectedModuleId('det-alerts')}
                className={`w-full text-left p-3 rounded-xl border transition-all text-xs ${
                  selectedModuleId === 'det-alerts'
                    ? 'bg-emerald-500/15 dark:bg-brand-emerald/20 border-emerald-500 dark:border-brand-emerald text-slate-900 dark:text-white shadow-sm dark:shadow-glow-emerald'
                    : 'bg-surface-50 dark:bg-surface-200/50 border-border-subtle text-slate-700 dark:text-slate-300 hover:bg-surface-200/60'
                }`}
              >
                <div className="flex items-center justify-between font-semibold mb-1">
                  <span>Threshold Rules & Retries</span>
                  <Bell className="w-3 h-3 text-emerald-600 dark:text-brand-emerald" />
                </div>
                <span className="text-[11px] text-slate-500 dark:text-slate-400 block">Signed webhooks & price swing triggers.</span>
              </button>
            </div>
          </div>

          <div className="pt-3 border-t border-border-subtle text-[11px] font-mono text-emerald-700 dark:text-brand-emerald flex items-center gap-1.5 font-medium">
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 dark:text-brand-emerald shrink-0" />
            <span>Zero AI Arithmetic Allowed</span>
          </div>
        </div>

        {/* ========================================================= */}
        {/* TIER 3 (Center/Bottom 4 cols): GROUNDED CONVERGENCE */}
        {/* ========================================================= */}
        <div className="lg:col-span-4 flex flex-col justify-between p-5 rounded-2xl bg-gradient-to-b from-surface-100 to-surface-200 dark:from-surface-100 dark:to-surface-300 border border-brand-500/40 dark:border-brand-300/40 shadow-sm dark:shadow-glow-brand space-y-4">
          <div>
            <div className="flex items-center justify-between pb-3 mb-3 border-b border-border-subtle">
              <div className="flex items-center gap-2">
                <div className="w-7 h-7 rounded-lg bg-brand-600 text-white flex items-center justify-center">
                  <Zap className="w-4 h-4" />
                </div>
                <span className="text-xs font-bold uppercase tracking-wider text-slate-900 dark:text-white">
                  Grounded Intelligence
                </span>
              </div>
              <span className="text-[10px] font-mono text-brand-700 dark:text-brand-300 bg-brand-500/20 px-2 py-0.5 rounded border border-brand-500/30">
                OUTPUT
              </span>
            </div>

            <p className="text-xs text-slate-600 dark:text-slate-300 mb-4 leading-relaxed">
              The synthesized result unites qualitative multi-agent reasoning with deterministic math for decision certainty.
            </p>

            <button
              onClick={() => setSelectedModuleId('convergence')}
              className={`w-full text-left p-3.5 rounded-xl border transition-all text-xs ${
                selectedModuleId === 'convergence'
                  ? 'bg-brand-500/15 dark:bg-brand-500/25 border-brand-500 dark:border-brand-300 text-slate-900 dark:text-white shadow-sm dark:shadow-glow-brand'
                  : 'bg-surface-50 dark:bg-surface-200/60 border-border-subtle text-slate-700 dark:text-slate-300 hover:bg-surface-200'
              }`}
            >
              <div className="flex items-center justify-between font-bold text-slate-900 dark:text-white mb-1.5">
                <span>Unified Investment Thesis</span>
                <ArrowRight className="w-3.5 h-3.5 text-brand-600 dark:text-brand-cyan" />
              </div>
              <p className="text-[11px] text-slate-600 dark:text-slate-300 leading-tight">
                Context-aware research grounded in your exact portfolio holdings and risk parameters.
              </p>
            </button>
          </div>

          <div className="p-3 rounded-xl bg-surface-50 dark:bg-surface-400/80 border border-border-subtle text-[11px] font-mono text-slate-700 dark:text-slate-300 flex items-center justify-between">
            <span>Formula:</span>
            <strong className="text-slate-900 dark:text-white">AI Reason + Math Truth</strong>
          </div>
        </div>
      </div>

      {/* Selected Module Deep-Dive Inspector */}
      <div className="p-5 rounded-2xl bg-surface-100 dark:bg-surface-300/90 border border-border-subtle text-xs relative z-10">
        <div className="flex flex-wrap items-center justify-between gap-2 pb-3 mb-3 border-b border-border-subtle">
          <div className="flex items-center gap-2">
            <span className="text-xs font-bold text-slate-900 dark:text-white font-sans">{active.title}</span>
            <span className="text-[10px] font-mono text-brand-700 dark:text-brand-cyan bg-brand-500/10 dark:bg-brand-cyan/10 px-2 py-0.5 rounded">
              {active.tag}
            </span>
          </div>
          <span className="text-[11px] text-emerald-700 dark:text-brand-emerald font-semibold flex items-center gap-1">
            <CheckCircle2 className="w-3.5 h-3.5" />
            {active.guarantee}
          </span>
        </div>

        <p className="text-xs text-slate-700 dark:text-slate-300 mb-3 leading-relaxed font-sans">
          {active.description}
        </p>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-2 text-[11px] font-sans text-slate-700 dark:text-slate-300">
          {active.rules.map((rule, idx) => (
            <div key={idx} className="p-2 rounded-lg bg-surface-50 dark:bg-surface-200/60 border border-border-subtle flex items-start gap-2">
              <span className="w-1.5 h-1.5 rounded-full bg-brand-600 dark:bg-brand-cyan mt-1.5 shrink-0" />
              <span>{rule}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
