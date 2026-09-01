import React, { useEffect, useState } from 'react';
import {
  Search,
  Sparkles,
  Building2,
  TrendingUp,
  ShieldAlert,
  Database,
  Trash2,
  Clock,
  Newspaper,
  Loader2,
  ExternalLink,
} from 'lucide-react';
import { api } from '../lib/api';
import {
  CompanyProfile,
  KeyMetrics,
  MarketQuote,
  NewsItem,
  ResearchHistoryItem,
  ResearchRecord,
} from '../types';
import { useToast } from '../context/ToastContext';
import { GlassCard } from '../components/ui/GlassCard';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { Badge } from '../components/ui/Badge';
import { Tabs } from '../components/ui/Tabs';
import { PageHeader } from '../components/ui/PageHeader';
import { EmptyState } from '../components/ui/EmptyState';
import { Skeleton } from '../components/ui/Skeleton';
import {
  formatCurrency,
  formatPercent,
  formatNumber,
  formatDate,
} from '../lib/utils';

export const Research: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [isSearching, setIsSearching] = useState(false);

  // Selected Security Data
  const [selectedSymbol, setSelectedSymbol] = useState<string | null>(null);
  const [profile, setProfile] = useState<CompanyProfile | null>(null);
  const [quote, setQuote] = useState<MarketQuote | null>(null);
  const [metrics, setMetrics] = useState<KeyMetrics | null>(null);
  const [news, setNews] = useState<NewsItem[]>([]);
  const [activeTab, setActiveTab] = useState('overview');
  const [isLoadingSecurity, setIsLoadingSecurity] = useState(false);

  // AI Deep Research Reports
  const [activeReport, setActiveReport] = useState<ResearchRecord | null>(null);
  const [history, setHistory] = useState<ResearchHistoryItem[]>([]);
  const [isLoadingHistory, setIsLoadingHistory] = useState(true);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [researchPrompt, setResearchPrompt] = useState('');

  const { showToast } = useToast();

  const fetchHistory = async () => {
    setIsLoadingHistory(true);
    try {
      const res = await api.research.getHistory();
      setHistory(res.history);
      if (res.history.length > 0 && !activeReport) {
        loadReport(res.history[0].id);
      }
    } catch {
      // ignore
    } finally {
      setIsLoadingHistory(false);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, []);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;

    setIsSearching(true);
    try {
      const res = await api.research.search(searchQuery.trim());
      if (res.results.length > 0) {
        handleSelectSecurity(res.results[0].symbol);
      } else {
        showToast(`No matching ticker found for "${searchQuery.trim()}".`, 'info');
      }
    } catch (err: any) {
      showToast(err.message || 'Search failed.', 'error');
    } finally {
      setIsSearching(false);
    }
  };

  const handleSelectSecurity = async (sym: string) => {
    setSelectedSymbol(sym);
    setActiveTab('overview');
    setIsLoadingSecurity(true);
    try {
      const [pRes, qRes, mRes, nRes] = await Promise.allSettled([
        api.research.getCompanyProfile(sym),
        api.research.getQuote(sym),
        api.research.getMetrics(sym),
        api.research.getNews(sym, 5),
      ]);

      if (pRes.status === 'fulfilled') setProfile(pRes.value.profile);
      if (qRes.status === 'fulfilled') setQuote(qRes.value.quote);
      if (mRes.status === 'fulfilled') setMetrics(mRes.value.metrics);
      if (nRes.status === 'fulfilled') setNews(nRes.value.news);
    } catch (err: any) {
      showToast(err.message || 'Failed to fetch security details.', 'error');
    } finally {
      setIsLoadingSecurity(false);
    }
  };

  const loadReport = async (id: number) => {
    try {
      const res = await api.research.getReport(id);
      setActiveReport(res.report);
      setActiveTab('ai_report');
    } catch (err: any) {
      showToast(err.message || 'Failed to load report.', 'error');
    }
  };

  const handleRunDeepAnalysis = async () => {
    const targetSymbol = selectedSymbol || searchQuery.trim().toUpperCase();
    if (!targetSymbol && !researchPrompt) {
      showToast('Please enter a company name or ticker.', 'error');
      return;
    }

    setIsAnalyzing(true);
    try {
      const res = await api.research.analyze({
        symbol: targetSymbol || undefined,
        query: researchPrompt.trim() || undefined,
      });
      setActiveReport(res.report);
      setActiveTab('ai_report');
      showToast(`Multi-agent research completed for ${res.report.symbol}.`, 'success');
      setResearchPrompt('');
      fetchHistory();
    } catch (err: any) {
      showToast(err.message || 'AI Research execution failed.', 'error');
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleDeleteReport = async (id: number) => {
    try {
      await api.research.deleteReport(id);
      showToast('Research report deleted.', 'info');
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
        title="Autonomous Equity Research"
        subtitle="Multi-agent company synthesis with automated fundamentals, valuations, and risk grounding."
      />

      {/* Search & AI Prompt Bar */}
      <GlassCard glow="brand" className="p-6">
        <form onSubmit={handleSearch} className="space-y-3">
          <div className="flex flex-col sm:flex-row items-center gap-3">
            <div className="flex-1 w-full">
              <Input
                placeholder="Search ticker or company name (e.g. NVDA, Apple, Microsoft)..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                leftIcon={<Search className="w-4 h-4" />}
                disabled={isSearching || isAnalyzing}
              />
            </div>
            <Button
              type="submit"
              variant="secondary"
              isLoading={isSearching}
              disabled={isSearching || isAnalyzing}
              className="w-full sm:w-auto"
            >
              Resolve Security
            </Button>
            <Button
              type="button"
              variant="glow"
              onClick={handleRunDeepAnalysis}
              isLoading={isAnalyzing}
              disabled={isSearching || isAnalyzing}
              className="w-full sm:w-auto shrink-0"
              leftIcon={<Sparkles className="w-4 h-4" />}
            >
              {isAnalyzing ? 'Analyzing...' : 'Run Autonomous Research'}
            </Button>
          </div>

          <div className="pt-2">
            <Input
              placeholder="Optional customized research query (e.g. 'Evaluate datacenter revenue growth vs pricing power')"
              value={researchPrompt}
              onChange={(e) => setResearchPrompt(e.target.value)}
              disabled={isAnalyzing}
            />
          </div>

          {isAnalyzing && (
            <div className="flex items-center gap-2 text-xs text-brand-300 animate-pulse pt-2">
              <Loader2 className="w-3.5 h-3.5 animate-spin" />
              <span>
                AIRA Research Agents are fetching balance sheets, income statements, news feeds, and computing valuation ratios...
              </span>
            </div>
          )}
        </form>
      </GlassCard>

      {/* Main Grid: Research History vs Active View */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left 4 Cols: History */}
        <div className="lg:col-span-4 space-y-3">
          <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400 px-1 flex items-center justify-between">
            <span>Research Reports ({history.length})</span>
            <Clock className="w-3.5 h-3.5 text-slate-400 dark:text-slate-500" />
          </h3>

          {isLoadingHistory ? (
            <div className="space-y-2">
              <Skeleton className="h-20 rounded-xl" />
              <Skeleton className="h-20 rounded-xl" />
            </div>
          ) : history.length === 0 ? (
            <div className="p-6 rounded-2xl border border-dashed border-border-strong text-center text-xs text-slate-500 bg-surface-100 dark:bg-surface-200/30">
              No saved research reports. Search a company above to run an analysis.
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
                      <div className="flex items-center justify-between">
                        <span className="font-bold text-xs text-slate-900 dark:text-white">{item.symbol}</span>
                        <span className="text-[10px] text-slate-500 font-mono">{formatDate(item.created_at)}</span>
                      </div>
                      <div className="text-xs text-slate-700 dark:text-slate-300 font-medium truncate">{item.company}</div>
                      <p className="text-[11px] text-slate-500 dark:text-slate-400 line-clamp-2 leading-relaxed">
                        {item.summary}
                      </p>
                    </div>

                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleDeleteReport(item.id);
                      }}
                      className="p-1 rounded-md text-slate-400 hover:text-rose-600 dark:hover:text-rose-400 hover:bg-rose-500/10 opacity-0 group-hover:opacity-100 transition-opacity shrink-0"
                      title="Delete Report"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* Right 8 Cols: Security Details & Report */}
        <div className="lg:col-span-8 space-y-6">
          <Tabs
            tabs={[
              { id: 'overview', label: 'Company Profile & Market Data' },
              { id: 'ai_report', label: 'AI Deep Synthesis', count: activeReport ? 1 : 0 },
            ]}
            activeTab={activeTab}
            onChange={setActiveTab}
          />

          {activeTab === 'overview' ? (
            isLoadingSecurity ? (
              <GlassCard className="space-y-4">
                <Skeleton className="h-8 w-1/2" />
                <Skeleton className="h-24 w-full" />
                <Skeleton className="h-48 w-full" />
              </GlassCard>
            ) : !selectedSymbol && !profile ? (
              <EmptyState
                icon={Building2}
                title="Search or Select an Equity"
                description="Search by company name or symbol to inspect market quotes, valuation multiples, and recent news."
              />
            ) : (
              <div className="space-y-6">
                {/* Profile & Quote Summary */}
                <GlassCard className="p-6">
                  <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4 mb-4 pb-4 border-b border-border-subtle">
                    <div>
                      <div className="flex items-center gap-3">
                        <h2 className="text-2xl font-bold text-slate-900 dark:text-white tracking-tight">{profile?.name || selectedSymbol}</h2>
                        <Badge variant="brand">{profile?.symbol || selectedSymbol}</Badge>
                      </div>
                      <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
                        {profile?.sector ? `${profile.sector} • ${profile.industry}` : 'Public Equity'}
                      </p>
                    </div>

                    {quote && (
                      <div className="text-right">
                        <div className="text-2xl font-bold font-mono text-slate-900 dark:text-white">
                          {formatCurrency(quote.current_price)}
                        </div>
                        {quote.day_change_percent !== undefined && (
                          <div
                            className={
                              quote.day_change_percent >= 0
                                ? 'text-xs text-emerald-600 dark:text-emerald-400 font-mono font-semibold'
                                : 'text-xs text-rose-600 dark:text-rose-400 font-mono font-semibold'
                            }
                          >
                            {formatPercent(quote.day_change_percent)}
                          </div>
                        )}
                      </div>
                    )}
                  </div>

                  {profile?.description && (
                    <div className="mb-6">
                      <h4 className="text-xs uppercase tracking-wider font-semibold text-slate-500 dark:text-slate-400 mb-1.5">Business Overview</h4>
                      <p className="text-xs text-slate-700 dark:text-slate-300 leading-relaxed bg-surface-50 dark:bg-surface-300/40 p-4 rounded-xl border border-border-subtle">
                        {profile.description}
                      </p>
                    </div>
                  )}

                  {/* Valuation Multiples */}
                  {metrics && (
                    <div>
                      <h4 className="text-xs uppercase tracking-wider font-semibold text-slate-500 dark:text-slate-400 mb-3">Key Financial Multiples</h4>
                      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-3">
                        <div className="p-3 rounded-xl bg-surface-50 dark:bg-surface-100/60 border border-border-subtle text-center">
                          <span className="text-[10px] text-slate-500 dark:text-slate-400 uppercase font-mono">P/E Ratio</span>
                          <div className="text-sm font-bold text-slate-900 dark:text-white font-mono mt-1">
                            {metrics.pe_ratio ? formatNumber(metrics.pe_ratio, 2) : '—'}
                          </div>
                        </div>
                        <div className="p-3 rounded-xl bg-surface-50 dark:bg-surface-100/60 border border-border-subtle text-center">
                          <span className="text-[10px] text-slate-500 dark:text-slate-400 uppercase font-mono">Forward P/E</span>
                          <div className="text-sm font-bold text-slate-900 dark:text-white font-mono mt-1">
                            {metrics.forward_pe ? formatNumber(metrics.forward_pe, 2) : '—'}
                          </div>
                        </div>
                        <div className="p-3 rounded-xl bg-surface-50 dark:bg-surface-100/60 border border-border-subtle text-center">
                          <span className="text-[10px] text-slate-500 dark:text-slate-400 uppercase font-mono">P/B Ratio</span>
                          <div className="text-sm font-bold text-slate-900 dark:text-white font-mono mt-1">
                            {metrics.price_to_book ? formatNumber(metrics.price_to_book, 2) : '—'}
                          </div>
                        </div>
                        <div className="p-3 rounded-xl bg-surface-50 dark:bg-surface-100/60 border border-border-subtle text-center">
                          <span className="text-[10px] text-slate-500 dark:text-slate-400 uppercase font-mono">Beta</span>
                          <div className="text-sm font-bold text-slate-900 dark:text-white font-mono mt-1">
                            {metrics.beta ? formatNumber(metrics.beta, 2) : '—'}
                          </div>
                        </div>
                        <div className="p-3 rounded-xl bg-surface-50 dark:bg-surface-100/60 border border-border-subtle text-center">
                          <span className="text-[10px] text-slate-500 dark:text-slate-400 uppercase font-mono">Div Yield</span>
                          <div className="text-sm font-bold text-slate-900 dark:text-white font-mono mt-1">
                            {metrics.dividend_yield ? formatPercent(metrics.dividend_yield * 100, false) : '—'}
                          </div>
                        </div>
                        <div className="p-3 rounded-xl bg-surface-50 dark:bg-surface-100/60 border border-border-subtle text-center">
                          <span className="text-[10px] text-slate-500 dark:text-slate-400 uppercase font-mono">EPS</span>
                          <div className="text-sm font-bold text-slate-900 dark:text-white font-mono mt-1">
                            {metrics.eps ? formatCurrency(metrics.eps) : '—'}
                          </div>
                        </div>
                      </div>
                    </div>
                  )}
                </GlassCard>

                {/* News Section */}
                {news.length > 0 && (
                  <GlassCard className="p-6">
                    <div className="flex items-center gap-2 mb-4">
                      <Newspaper className="w-4 h-4 text-brand-600 dark:text-brand-400" />
                      <h3 className="text-sm font-semibold text-slate-900 dark:text-white">Recent Verified Headlines</h3>
                    </div>
                    <div className="space-y-2.5">
                      {news.map((item, idx) => (
                        <div
                          key={idx}
                          className="p-3.5 rounded-xl bg-surface-50 dark:bg-surface-100/60 border border-border-subtle flex items-start justify-between gap-4"
                        >
                          <div className="space-y-1">
                            <h4 className="text-xs font-semibold text-slate-900 dark:text-white hover:text-brand-600 dark:hover:text-brand-300">
                              {item.title}
                            </h4>
                            <div className="flex items-center gap-2 text-[10px] text-slate-500 dark:text-slate-400 font-mono">
                              <span>{item.publisher || 'Financial Wire'}</span>
                              {item.publish_time && <span>• {item.publish_time}</span>}
                            </div>
                          </div>
                          {item.link && (
                            <a
                              href={item.link}
                              target="_blank"
                              rel="noreferrer"
                              className="text-slate-400 hover:text-brand-600 dark:hover:text-brand-300 p-1 rounded-lg"
                              title="Open Article"
                            >
                              <ExternalLink className="w-4 h-4" />
                            </a>
                          )}
                        </div>
                      ))}
                    </div>
                  </GlassCard>
                )}
              </div>
            )
          ) : (
            /* AI Deep Synthesis Report View */
            !activeReport ? (
              <EmptyState
                icon={Sparkles}
                title="No AI Synthesis Selected"
                description="Click 'Run Autonomous Research' above or select a report from the historical sidebar."
                actionLabel="Run Research"
                onAction={handleRunDeepAnalysis}
                actionIcon={<Sparkles className="w-4 h-4" />}
              />
            ) : (
              <div className="space-y-6">
                <GlassCard glow="brand" className="p-6">
                  <div className="flex items-center justify-between gap-4 mb-4 pb-3 border-b border-border-subtle">
                    <div>
                      <div className="flex items-center gap-2">
                        <Sparkles className="w-4 h-4 text-brand-600 dark:text-brand-400" />
                        <h2 className="text-lg font-bold text-slate-900 dark:text-white tracking-tight">
                          {activeReport.company} ({activeReport.symbol})
                        </h2>
                      </div>
                      <span className="text-[11px] text-slate-500 dark:text-slate-400 font-mono mt-0.5 block">
                        Synthesized on {formatDate(activeReport.created_at)}
                      </span>
                    </div>
                    <Badge variant="brand">Report #{activeReport.id}</Badge>
                  </div>

                  <div className="space-y-4">
                    <div>
                      <h4 className="text-xs uppercase tracking-wider font-semibold text-slate-500 dark:text-slate-400 mb-1.5">Executive Summary</h4>
                      <p className="text-sm text-slate-800 dark:text-slate-200 leading-relaxed bg-surface-50 dark:bg-surface-300/40 p-4 rounded-xl border border-border-subtle">
                        {activeReport.summary}
                      </p>
                    </div>

                    {activeReport.fundamentals && (
                      <div>
                        <h4 className="text-xs uppercase tracking-wider font-semibold text-slate-500 dark:text-slate-400 mb-1.5">Fundamental Analysis</h4>
                        <p className="text-xs text-slate-700 dark:text-slate-300 leading-relaxed bg-surface-50 dark:bg-surface-300/20 p-3.5 rounded-xl border border-border-subtle">
                          {activeReport.fundamentals}
                        </p>
                      </div>
                    )}

                    {activeReport.valuation && (
                      <div>
                        <h4 className="text-xs uppercase tracking-wider font-semibold text-slate-500 dark:text-slate-400 mb-1.5">Valuation & Multiples</h4>
                        <p className="text-xs text-slate-700 dark:text-slate-300 leading-relaxed bg-surface-50 dark:bg-surface-300/20 p-3.5 rounded-xl border border-border-subtle">
                          {activeReport.valuation}
                        </p>
                      </div>
                    )}
                  </div>
                </GlassCard>

                {/* Risks and Opportunities */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <GlassCard className="border-rose-500/20 p-5">
                    <div className="flex items-center gap-2 mb-3 text-rose-600 dark:text-rose-400">
                      <ShieldAlert className="w-4 h-4" />
                      <h3 className="text-sm font-semibold">Identified Risk Vectors</h3>
                    </div>
                    <ul className="space-y-2 text-xs text-slate-700 dark:text-slate-300">
                      {activeReport.risks.map((risk, idx) => (
                        <li key={idx} className="flex items-start gap-2 bg-rose-500/5 p-2.5 rounded-lg border border-rose-500/10">
                          <span className="text-rose-600 dark:text-rose-400 font-bold shrink-0">•</span>
                          <span className="leading-relaxed">{risk}</span>
                        </li>
                      ))}
                    </ul>
                  </GlassCard>

                  <GlassCard className="border-emerald-500/20 p-5">
                    <div className="flex items-center gap-2 mb-3 text-emerald-600 dark:text-emerald-400">
                      <TrendingUp className="w-4 h-4" />
                      <h3 className="text-sm font-semibold">Growth Catalysts & Opportunities</h3>
                    </div>
                    <ul className="space-y-2 text-xs text-slate-700 dark:text-slate-300">
                      {activeReport.opportunities.map((opp, idx) => (
                        <li key={idx} className="flex items-start gap-2 bg-emerald-500/5 p-2.5 rounded-lg border border-emerald-500/10">
                          <span className="text-emerald-600 dark:text-emerald-400 font-bold shrink-0">•</span>
                          <span className="leading-relaxed">{opp}</span>
                        </li>
                      ))}
                    </ul>
                  </GlassCard>
                </div>

                {/* Provenance */}
                {activeReport.sources && activeReport.sources.length > 0 && (
                  <GlassCard className="p-5">
                    <div className="flex items-center gap-2 mb-3">
                      <Database className="w-4 h-4 text-slate-500 dark:text-slate-400" />
                      <h4 className="text-xs uppercase tracking-wider font-semibold text-slate-500 dark:text-slate-400">
                        Evidence Grounding Sources ({activeReport.sources.length})
                      </h4>
                    </div>
                    <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-2">
                      {activeReport.sources.map((src, idx) => (
                        <div key={idx} className="p-2.5 rounded-lg bg-surface-50 dark:bg-surface-300/60 border border-border-subtle text-[11px] font-mono text-slate-600 dark:text-slate-400">
                          <div className="text-slate-900 dark:text-white font-semibold flex items-center justify-between">
                            <span>{src.symbol}</span>
                            <span className="text-[10px] text-brand-600 dark:text-brand-400">{src.provider}</span>
                          </div>
                          <div className="text-[10px] text-slate-500 truncate mt-0.5">{src.source_type || 'Financial API'}</div>
                        </div>
                      ))}
                    </div>
                  </GlassCard>
                )}
              </div>
            )
          )}
        </div>
      </div>
    </div>
  );
};
