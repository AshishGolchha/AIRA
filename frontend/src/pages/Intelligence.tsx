import React, { useEffect, useState } from 'react';
import {
  Sparkles,
  ShieldAlert,
  TrendingUp,
  Bookmark,
  Compass,
  Database,
  Trash2,
  Clock,
  Loader2,
} from 'lucide-react';
import { api } from '../lib/api';
import {
  PortfolioIntelligenceRecord,
  PortfolioIntelligenceSummaryItem,
} from '../types';
import { useToast } from '../context/ToastContext';
import { GlassCard } from '../components/ui/GlassCard';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { Badge } from '../components/ui/Badge';
import { PageHeader } from '../components/ui/PageHeader';
import { EmptyState } from '../components/ui/EmptyState';
import { Skeleton } from '../components/ui/Skeleton';
import { formatDate } from '../lib/utils';

export const Intelligence: React.FC = () => {
  const [activeReport, setActiveReport] = useState<PortfolioIntelligenceRecord | null>(null);
  const [history, setHistory] = useState<PortfolioIntelligenceSummaryItem[]>([]);
  const [isLoadingHistory, setIsLoadingHistory] = useState(true);
  const [isLoadingReport, setIsLoadingReport] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [query, setQuery] = useState('');

  const { showToast } = useToast();

  const fetchHistory = async () => {
    setIsLoadingHistory(true);
    try {
      const res = await api.intelligence.getHistory();
      setHistory(res.history);
      if (res.history.length > 0 && !activeReport) {
        // Load the latest report details
        loadReport(res.history[0].id);
      }
    } catch (err: any) {
      showToast(err.message || 'Failed to load intelligence history.', 'error');
    } finally {
      setIsLoadingHistory(false);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, []);

  const loadReport = async (id: number) => {
    setIsLoadingReport(true);
    try {
      const res = await api.intelligence.getReport(id);
      setActiveReport(res.report);
    } catch (err: any) {
      showToast(err.message || 'Failed to load report.', 'error');
    } finally {
      setIsLoadingReport(false);
    }
  };

  const handleGenerate = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsGenerating(true);
    try {
      const res = await api.intelligence.generate({
        query: query.trim() || undefined,
      });
      setActiveReport(res.intelligence);
      showToast('Portfolio intelligence synthesized successfully.', 'success');
      setQuery('');
      // Refresh history
      const histRes = await api.intelligence.getHistory();
      setHistory(histRes.history);
    } catch (err: any) {
      showToast(err.message || 'Failed to generate intelligence.', 'error');
    } finally {
      setIsGenerating(false);
    }
  };

  const handleDelete = async (id: number) => {
    try {
      await api.intelligence.deleteReport(id);
      showToast('Intelligence report deleted.', 'info');
      if (activeReport?.id === id) {
        setActiveReport(null);
      }
      fetchHistory();
    } catch (err: any) {
      showToast(err.message || 'Failed to delete report.', 'error');
    }
  };

  return (
    <div className="space-y-8 animate-in fade-in duration-300">
      <PageHeader
        title="Portfolio & Watchlist Intelligence"
        subtitle="Autonomous synthesis combining deterministic portfolio weights, watchlist telemetry, and AI market reasoning."
      />

      {/* Generation Bar */}
      <GlassCard glow="brand" className="p-5">
        <form onSubmit={handleGenerate} className="space-y-3">
          <div className="flex flex-col sm:flex-row items-center gap-3">
            <div className="flex-1 w-full">
              <Input
                placeholder="Optional focal query (e.g. 'Assess semiconductor concentration and interest rate risk')"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                disabled={isGenerating}
              />
            </div>
            <Button
              type="submit"
              variant="glow"
              isLoading={isGenerating}
              disabled={isGenerating}
              className="w-full sm:w-auto shrink-0"
              leftIcon={<Sparkles className="w-4 h-4" />}
            >
              {isGenerating ? 'Synthesizing...' : 'Generate New Synthesis'}
            </Button>
          </div>
          {isGenerating && (
            <div className="flex items-center gap-2 text-xs text-brand-300 animate-pulse pt-1">
              <Loader2 className="w-3.5 h-3.5 animate-spin" />
              <span>
                AIRA Multi-Agent Engine is grounding deterministic weights, fetching live security quotes, and evaluating risk vectors...
              </span>
            </div>
          )}
        </form>
      </GlassCard>

      {/* Main Grid: History Sidebar & Report View */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left 4 Cols: Historical Reports */}
        <div className="lg:col-span-4 space-y-3">
          <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400 px-1 flex items-center justify-between">
            <span>Historical Reports ({history.length})</span>
            <Clock className="w-3.5 h-3.5 text-slate-400 dark:text-slate-500" />
          </h3>

          {isLoadingHistory ? (
            <div className="space-y-2">
              <Skeleton className="h-20 rounded-xl" />
              <Skeleton className="h-20 rounded-xl" />
              <Skeleton className="h-20 rounded-xl" />
            </div>
          ) : history.length === 0 ? (
            <div className="p-6 rounded-2xl border border-dashed border-border-strong text-center text-xs text-slate-500 bg-surface-100 dark:bg-surface-200/30">
              No saved intelligence reports. Generate a synthesis above to begin.
            </div>
          ) : (
            <div className="space-y-2 max-h-[650px] overflow-y-auto pr-1">
              {history.map((item) => {
                const isSelected = activeReport?.id === item.id;
                return (
                  <div
                    key={item.id}
                    onClick={() => loadReport(item.id)}
                    className={`p-3.5 rounded-xl border transition-all cursor-pointer group flex items-start justify-between gap-3 ${
                      isSelected
                        ? 'bg-brand-500/10 dark:bg-brand-600/10 border-brand-500 text-slate-900 dark:text-white shadow-sm'
                        : 'bg-surface-50 dark:bg-surface-200/60 border-border-subtle hover:border-border-strong hover:bg-surface-100 dark:hover:bg-surface-100/60 text-slate-700 dark:text-slate-300'
                    }`}
                  >
                    <div className="flex-1 min-w-0 space-y-1">
                      <div className="flex items-center gap-2">
                        <span className="font-semibold text-xs text-slate-900 dark:text-white">
                          {item.query ? `"${item.query}"` : 'Portfolio Synthesis'}
                        </span>
                      </div>
                      <p className="text-[11px] text-slate-500 dark:text-slate-400 line-clamp-2 leading-relaxed">
                        {item.summary}
                      </p>
                      <div className="flex items-center gap-2 text-[10px] text-slate-500 font-mono pt-1">
                        <span>{formatDate(item.created_at)}</span>
                        {item.symbols_analyzed.length > 0 && (
                          <span>• {item.symbols_analyzed.slice(0, 3).join(', ')}</span>
                        )}
                      </div>
                    </div>

                    <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleDelete(item.id);
                        }}
                        className="p-1 rounded-md text-slate-400 hover:text-rose-600 dark:hover:text-rose-400 hover:bg-rose-500/10"
                        title="Delete Report"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* Right 8 Cols: Active Report Detail */}
        <div className="lg:col-span-8">
          {isLoadingReport ? (
            <GlassCard className="space-y-4">
              <Skeleton className="h-8 w-3/4" />
              <Skeleton className="h-24 w-full" />
              <Skeleton className="h-40 w-full" />
            </GlassCard>
          ) : !activeReport ? (
            <EmptyState
              icon={Sparkles}
              title="No Report Selected"
              description="Select a historical report from the left or generate a new AI synthesis using the form above."
              actionLabel="Generate Synthesis"
              onAction={() => handleGenerate({ preventDefault: () => {} } as any)}
              actionIcon={<Sparkles className="w-4 h-4" />}
            />
          ) : (
            <div className="space-y-6">
              {/* Executive Summary */}
              <GlassCard glow="brand" className="p-6">
                <div className="flex items-center justify-between gap-4 mb-4 pb-3 border-b border-border-subtle">
                  <div>
                    <div className="flex items-center gap-2">
                      <Sparkles className="w-4 h-4 text-brand-600 dark:text-brand-400" />
                      <h2 className="text-base font-bold text-slate-900 dark:text-white tracking-tight">
                        {activeReport.query ? `Report: ${activeReport.query}` : 'Executive Investment Synthesis'}
                      </h2>
                    </div>
                    <span className="text-[11px] text-slate-500 dark:text-slate-400 font-mono mt-0.5 block">
                      Generated {formatDate(activeReport.created_at)}
                    </span>
                  </div>
                  <Badge variant="brand">Persisted Record #{activeReport.id}</Badge>
                </div>

                <div className="space-y-4">
                  <div>
                    <h4 className="text-xs uppercase tracking-wider font-semibold text-slate-500 dark:text-slate-400 mb-1.5">
                      Executive Summary
                    </h4>
                    <p className="text-sm text-slate-800 dark:text-slate-200 leading-relaxed bg-surface-50 dark:bg-surface-300/40 p-4 rounded-xl border border-border-subtle">
                      {activeReport.summary}
                    </p>
                  </div>

                  <div>
                    <h4 className="text-xs uppercase tracking-wider font-semibold text-slate-500 dark:text-slate-400 mb-1.5">
                      Portfolio Architecture & Allocation
                    </h4>
                    <p className="text-xs text-slate-700 dark:text-slate-300 leading-relaxed bg-surface-50 dark:bg-surface-300/20 p-3.5 rounded-xl border border-border-subtle">
                      {activeReport.portfolio_overview}
                    </p>
                  </div>
                </div>
              </GlassCard>

              {/* Risks & Opportunities Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Risks */}
                <GlassCard className="border-rose-500/20 p-5">
                  <div className="flex items-center gap-2 mb-3 text-rose-600 dark:text-rose-400">
                    <ShieldAlert className="w-4 h-4" />
                    <h3 className="text-sm font-semibold">Identified Risk Vectors</h3>
                  </div>
                  <ul className="space-y-2 text-xs text-slate-700 dark:text-slate-300">
                    {activeReport.portfolio_risks.map((risk, idx) => (
                      <li key={idx} className="flex items-start gap-2 bg-rose-500/5 p-2.5 rounded-lg border border-rose-500/10">
                        <span className="text-rose-600 dark:text-rose-400 font-bold shrink-0">•</span>
                        <span className="leading-relaxed">{risk}</span>
                      </li>
                    ))}
                  </ul>
                </GlassCard>

                {/* Opportunities */}
                <GlassCard className="border-emerald-500/20 p-5">
                  <div className="flex items-center gap-2 mb-3 text-emerald-600 dark:text-emerald-400">
                    <TrendingUp className="w-4 h-4" />
                    <h3 className="text-sm font-semibold">Strategic Opportunities</h3>
                  </div>
                  <ul className="space-y-2 text-xs text-slate-700 dark:text-slate-300">
                    {activeReport.portfolio_opportunities.map((opp, idx) => (
                      <li key={idx} className="flex items-start gap-2 bg-emerald-500/5 p-2.5 rounded-lg border border-emerald-500/10">
                        <span className="text-emerald-600 dark:text-emerald-400 font-bold shrink-0">•</span>
                        <span className="leading-relaxed">{opp}</span>
                      </li>
                    ))}
                  </ul>
                </GlassCard>
              </div>

              {/* Watchlist Priorities & Recommended Research */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Watchlist Priorities */}
                <GlassCard className="p-5">
                  <div className="flex items-center gap-2 mb-3 text-cyan-600 dark:text-cyan-400">
                    <Bookmark className="w-4 h-4" />
                    <h3 className="text-sm font-semibold">Watchlist Recommendations</h3>
                  </div>
                  <ul className="space-y-2 text-xs text-slate-700 dark:text-slate-300">
                    {activeReport.watchlist_priorities.map((item, idx) => (
                      <li key={idx} className="flex items-start gap-2 bg-surface-50 dark:bg-surface-100 p-2.5 rounded-lg border border-border-subtle">
                        <span className="text-cyan-600 dark:text-cyan-400 font-bold shrink-0">•</span>
                        <span className="leading-relaxed">{item}</span>
                      </li>
                    ))}
                  </ul>
                </GlassCard>

                {/* Recommended Research */}
                <GlassCard className="p-5">
                  <div className="flex items-center gap-2 mb-3 text-brand-600 dark:text-brand-400">
                    <Compass className="w-4 h-4" />
                    <h3 className="text-sm font-semibold">Suggested Deep Dives</h3>
                  </div>
                  <ul className="space-y-2 text-xs text-slate-700 dark:text-slate-300">
                    {activeReport.recommended_research.map((item, idx) => (
                      <li key={idx} className="flex items-start gap-2 bg-surface-50 dark:bg-surface-100 p-2.5 rounded-lg border border-border-subtle">
                        <span className="text-brand-600 dark:text-brand-400 font-bold shrink-0">•</span>
                        <span className="leading-relaxed">{item}</span>
                      </li>
                    ))}
                  </ul>
                </GlassCard>
              </div>

              {/* Sources and Provenance */}
              {activeReport.sources && activeReport.sources.length > 0 && (
                <GlassCard className="p-5">
                  <div className="flex items-center gap-2 mb-3">
                    <Database className="w-4 h-4 text-slate-500 dark:text-slate-400" />
                    <h4 className="text-xs uppercase tracking-wider font-semibold text-slate-500 dark:text-slate-400">
                      Evidence Grounding & Source Provenance ({activeReport.sources.length})
                    </h4>
                  </div>
                  <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-2">
                    {activeReport.sources.map((src, idx) => (
                      <div
                        key={idx}
                        className="p-2.5 rounded-lg bg-surface-50 dark:bg-surface-300/60 border border-border-subtle text-[11px] font-mono text-slate-600 dark:text-slate-400"
                      >
                        <div className="text-slate-900 dark:text-white font-semibold flex items-center justify-between">
                          <span>{src.symbol}</span>
                          <span className="text-[10px] text-brand-600 dark:text-brand-400">{src.provider}</span>
                        </div>
                        <div className="text-[10px] text-slate-500 truncate mt-0.5">
                          {src.source_type || 'Market Telemetry'}
                        </div>
                      </div>
                    ))}
                  </div>
                </GlassCard>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
