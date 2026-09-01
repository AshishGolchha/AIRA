import React from 'react';
import {
  Search,
  CheckCircle2,
} from 'lucide-react';

export const EvidenceGroundingFlow: React.FC = () => {
  return (
    <div className="w-full max-w-5xl mx-auto rounded-3xl bg-surface-200/90 border border-border-strong p-6 sm:p-8 backdrop-blur-xl font-sans text-left relative overflow-hidden shadow-2xl">
      {/* Background Subtle Grid */}
      <div className="absolute inset-0 bg-grid-pattern opacity-20 pointer-events-none" />

      {/* Section Header */}
      <div className="flex flex-wrap items-center justify-between gap-4 pb-5 mb-6 border-b border-border-subtle relative z-10">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-brand-500/10 border border-brand-500/30 text-brand-300 text-xs font-semibold uppercase tracking-wider mb-2">
            <Search className="w-3.5 h-3.5 text-brand-cyan" />
            <span>Verifiable Evidence Grounding</span>
          </div>
          <h3 className="text-xl sm:text-2xl font-bold text-white tracking-tight">
            Every Thesis Claim Maps to a Verifiable Source Filing
          </h3>
        </div>

        <span className="text-xs font-mono text-brand-cyan bg-brand-cyan/10 px-2.5 py-1 rounded-lg border border-brand-cyan/20">
          SEC 10-Q &bull; EDGAR Grounded
        </span>
      </div>

      {/* Step-by-Step Flow Conduits */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-3.5 relative z-10 mb-6">
        {/* Step 1 */}
        <div className="p-4 rounded-2xl bg-surface-100/90 border border-border-subtle flex flex-col justify-between space-y-3">
          <div>
            <span className="text-[10px] font-mono font-bold text-brand-cyan uppercase block mb-1">
              Step 01 &bull; Extract
            </span>
            <h4 className="text-xs font-bold text-white mb-2">SEC 10-Q Excerpt</h4>
            <p className="text-[11px] text-slate-300 font-mono bg-surface-200/80 p-2.5 rounded-xl border border-border-subtle leading-relaxed">
              "Data Center compute segment revenue surged to $26.3B (+154% YoY)..."
            </p>
          </div>
          <span className="text-[10px] font-mono text-slate-400">Page 18, Segment Table</span>
        </div>

        {/* Step 2 */}
        <div className="p-4 rounded-2xl bg-surface-100/90 border border-border-subtle flex flex-col justify-between space-y-3">
          <div>
            <span className="text-[10px] font-mono font-bold text-brand-300 uppercase block mb-1">
              Step 02 &bull; Parse
            </span>
            <h4 className="text-xs font-bold text-white mb-2">Metrics Extracted</h4>
            <div className="space-y-1.5 font-mono text-[11px]">
              <div className="p-1.5 rounded-lg bg-surface-200/80 border border-border-subtle flex justify-between">
                <span className="text-slate-400">DC Revenue:</span>
                <strong className="text-white">$26.3B</strong>
              </div>
              <div className="p-1.5 rounded-lg bg-surface-200/80 border border-border-subtle flex justify-between">
                <span className="text-slate-400">Gross Margin:</span>
                <strong className="text-brand-emerald">75.1%</strong>
              </div>
            </div>
          </div>
          <span className="text-[10px] font-mono text-slate-400">Deterministic Numbers</span>
        </div>

        {/* Step 3 */}
        <div className="p-4 rounded-2xl bg-surface-100/90 border border-border-subtle flex flex-col justify-between space-y-3">
          <div>
            <span className="text-[10px] font-mono font-bold text-brand-emerald uppercase block mb-1">
              Step 03 &bull; Validate
            </span>
            <h4 className="text-xs font-bold text-white mb-2">Agent Cross-Check</h4>
            <div className="text-[11px] text-slate-300 leading-relaxed bg-surface-200/80 p-2.5 rounded-xl border border-border-subtle">
              Fundamental & Valuation agents verify multiple defensibility against historical baseline.
            </div>
          </div>
          <span className="text-[10px] font-mono text-brand-emerald flex items-center gap-1">
            <CheckCircle2 className="w-3 h-3" />
            3 Agents Agreed
          </span>
        </div>

        {/* Step 4 */}
        <div className="p-4 rounded-2xl bg-gradient-to-b from-surface-100 to-surface-300 border border-brand-500/40 shadow-glow-brand flex flex-col justify-between space-y-3">
          <div>
            <span className="text-[10px] font-mono font-bold text-brand-cyan uppercase block mb-1">
              Step 04 &bull; Synthesize
            </span>
            <h4 className="text-xs font-bold text-white mb-2">Grounded Thesis</h4>
            <div className="text-[11px] text-slate-200 leading-relaxed">
              High-conviction structural thesis grounded with 18.5% portfolio weight context.
            </div>
          </div>
          <span className="text-[10px] font-mono text-brand-cyan font-bold">
            Verifiable Decision
          </span>
        </div>
      </div>
    </div>
  );
};
