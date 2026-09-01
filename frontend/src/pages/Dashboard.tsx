import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  PieChart,
  Bookmark,
  BellRing,
  Sparkles,
  ArrowRight,
  Radio,
  Activity,
  Layers,
  Search,
} from 'lucide-react';
import { api } from '../lib/api';
import { DashboardResponse } from '../types';
import { GlassCard } from '../components/ui/GlassCard';
import { Button } from '../components/ui/Button';
import { StatusBadge } from '../components/ui/StatusBadge';
import { Badge } from '../components/ui/Badge';
import { Skeleton } from '../components/ui/Skeleton';
import { ErrorState } from '../components/ui/ErrorState';
import { MetricCard } from '../components/ui/MetricCard';
import {
  formatCurrency,
  formatPercent,
  formatDate,
  formatNumber,
} from '../lib/utils';

export const Dashboard: React.FC = () => {
  const [data, setData] = useState<DashboardResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchDashboard = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const res = await api.dashboard.get();
      setData(res);
    } catch (err: any) {
      setError(err.message || 'Failed to load dashboard data.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboard();
  }, []);

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="space-y-2">
          <Skeleton className="h-8 w-64" />
          <Skeleton className="h-4 w-96" />
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <Skeleton className="h-32 rounded-2xl" />
          <Skeleton className="h-32 rounded-2xl" />
          <Skeleton className="h-32 rounded-2xl" />
          <Skeleton className="h-32 rounded-2xl" />
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <Skeleton className="h-80 lg:col-span-2 rounded-2xl" />
          <Skeleton className="h-80 rounded-2xl" />
        </div>
      </div>
    );
  }

  if (error || !data) {
    return <ErrorState message={error || 'Failed to load dashboard data'} onRetry={fetchDashboard} />;
  }

  const { user, portfolio, watchlist, alerts, research, notifications, monitoring, portfolio_intelligence } = data;

  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good morning';
    if (hour < 18) return 'Good afternoon';
    return 'Good evening';
  };

  return (
    <div className="space-y-8 animate-in fade-in duration-300">
      {/* 1. Header Area */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-2xl sm:text-3xl font-bold text-slate-900 dark:text-white tracking-tight">
              {getGreeting()}, {user.name}
            </h1>
            <Badge variant="brand">
              {user.risk_tolerance.charAt(0).toUpperCase() + user.risk_tolerance.slice(1)} Profile
            </Badge>
          </div>
          <p className="text-xs sm:text-sm text-slate-600 dark:text-slate-400 mt-1">
            Real-time portfolio valuation, deterministic alert telemetry, and personalized intelligence synthesis.
          </p>
        </div>

        <div className="flex items-center gap-2.5 shrink-0">
          <Button
            size="sm"
            variant="secondary"
            onClick={fetchDashboard}
            leftIcon={<Activity className="w-3.5 h-3.5" />}
          >
            Refresh Metrics
          </Button>
          <Link to="/app/portfolio">
            <Button size="sm" variant="secondary" leftIcon={<PieChart className="w-4 h-4" />}>
              View Portfolio
            </Button>
          </Link>
          <Link to="/app/intelligence">
            <Button size="sm" variant="glow" leftIcon={<Sparkles className="w-4 h-4" />}>
              Generate Report
            </Button>
          </Link>
        </div>
      </div>

      {/* 2. Top Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          label="Total Market Value"
          value={formatCurrency(portfolio.total_market_value)}
          change={portfolio.unrealized_gain_loss_percent}
          changeLabel="Total Return"
          icon={PieChart}
          glow="brand"
        />

        <MetricCard
          label="Total Cost Basis"
          value={formatCurrency(portfolio.total_cost_basis)}
          subtext={`${portfolio.holdings_count} active position${portfolio.holdings_count === 1 ? '' : 's'}`}
          icon={Layers}
        />

        <MetricCard
          label="Active Alerts"
          value={alerts.unread_count.toString()}
          subtext={`${alerts.critical_count} critical, ${alerts.warning_count} warning`}
          icon={BellRing}
          glow={alerts.critical_count > 0 ? 'none' : 'none'}
        />

        <MetricCard
          label="Monitored Assets"
          value={(portfolio.holdings_count + watchlist.total_count).toString()}
          subtext={`${watchlist.total_count} watchlist, ${portfolio.holdings_count} holdings`}
          icon={Bookmark}
          glow="cyan"
        />
      </div>

      {/* 3. Main Grid: Holdings & Portfolio Intelligence */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left 2 Cols: Top Holdings Table */}
        <GlassCard className="lg:col-span-2 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <PieChart className="w-4 h-4 text-brand-600 dark:text-brand-400" />
                <h3 className="text-sm font-semibold text-slate-900 dark:text-white">Top Portfolio Holdings</h3>
              </div>
              <Link to="/app/portfolio" className="text-xs text-brand-600 dark:text-brand-400 hover:text-brand-700 dark:hover:text-brand-300 font-medium flex items-center gap-1">
                All ({portfolio.holdings_count}) <ArrowRight className="w-3 h-3" />
              </Link>
            </div>

            {portfolio.top_holdings.length === 0 ? (
              <div className="text-center py-10 text-slate-500 text-xs">
                No portfolio holdings found.{' '}
                <Link to="/app/portfolio" className="text-brand-600 dark:text-brand-400 underline">
                  Add your first holding
                </Link>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs text-slate-700 dark:text-slate-300">
                  <thead className="text-[11px] text-slate-500 dark:text-slate-400 uppercase font-semibold border-b border-border-subtle">
                    <tr>
                      <th className="pb-2.5">Asset</th>
                      <th className="pb-2.5 text-right">Shares</th>
                      <th className="pb-2.5 text-right">Price</th>
                      <th className="pb-2.5 text-right">Market Value</th>
                      <th className="pb-2.5 text-right">Gain / Loss</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-border-subtle/50">
                    {portfolio.top_holdings.map((h) => {
                      const isGain = (h.unrealized_gain_loss || 0) >= 0;
                      return (
                        <tr key={h.id || h.symbol} className="hover:bg-black/[0.02] dark:hover:bg-white/[0.02]">
                          <td className="py-3">
                            <div className="font-semibold text-slate-900 dark:text-white">{h.symbol}</div>
                            <div className="text-[10px] text-slate-500 dark:text-slate-400 truncate max-w-[120px]">{h.company_name || 'Equity'}</div>
                          </td>
                          <td className="py-3 text-right font-mono">{formatNumber(h.quantity, 2)}</td>
                          <td className="py-3 text-right font-mono">{formatCurrency(h.current_price)}</td>
                          <td className="py-3 text-right font-mono font-medium text-slate-900 dark:text-white">{formatCurrency(h.market_value)}</td>
                          <td className="py-3 text-right font-mono">
                            <span className={isGain ? 'text-emerald-600 dark:text-emerald-400 font-medium' : 'text-rose-600 dark:text-rose-400 font-medium'}>
                              {formatCurrency(h.unrealized_gain_loss)} ({formatPercent(h.unrealized_gain_loss_percent)})
                            </span>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            )}
          </div>

          <div className="mt-4 pt-3 border-t border-border-subtle/60 flex items-center justify-between text-xs text-slate-500 dark:text-slate-400">
            <span>Net Unrealized Position</span>
            <span className={portfolio.unrealized_gain_loss >= 0 ? 'text-emerald-600 dark:text-emerald-400 font-semibold font-mono' : 'text-rose-600 dark:text-rose-400 font-semibold font-mono'}>
              {formatCurrency(portfolio.unrealized_gain_loss)} ({formatPercent(portfolio.unrealized_gain_loss_percent)})
            </span>
          </div>
        </GlassCard>

        {/* Right 1 Col: Latest AI Portfolio Intelligence */}
        <GlassCard glow="brand" className="flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-brand-600 dark:text-brand-400" />
                <h3 className="text-sm font-semibold text-slate-900 dark:text-white">Latest AI Intelligence</h3>
              </div>
              {portfolio_intelligence.available && (
                <Badge variant="brand" size="sm">Persisted</Badge>
              )}
            </div>

            {portfolio_intelligence.available && portfolio_intelligence.latest ? (
              <div className="space-y-3">
                <p className="text-xs text-slate-700 dark:text-slate-300 leading-relaxed line-clamp-4">
                  {portfolio_intelligence.latest.summary}
                </p>

                {portfolio_intelligence.latest.symbols_analyzed.length > 0 && (
                  <div className="space-y-1.5">
                    <span className="text-[10px] text-slate-500 dark:text-slate-400 uppercase tracking-wider font-semibold">
                      Analyzed Securities
                    </span>
                    <div className="flex flex-wrap gap-1.5">
                      {portfolio_intelligence.latest.symbols_analyzed.map((sym) => (
                        <span key={sym} className="px-2 py-0.5 rounded-md bg-surface-100 dark:bg-surface-100 border border-border-strong text-[11px] font-mono text-slate-700 dark:text-slate-300">
                          {sym}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                <div className="text-[11px] text-slate-500 dark:text-slate-400 font-mono pt-1">
                  Generated {formatDate(portfolio_intelligence.latest.created_at)}
                </div>
              </div>
            ) : (
              <div className="text-center py-6 space-y-3">
                <div className="w-10 h-10 rounded-xl bg-brand-500/10 border border-brand-500/20 flex items-center justify-center text-brand-600 dark:text-brand-400 mx-auto">
                  <Sparkles className="w-5 h-5" />
                </div>
                <p className="text-xs text-slate-600 dark:text-slate-400 leading-relaxed max-w-xs mx-auto">
                  No portfolio intelligence report generated yet. Generate personalized risk and opportunity synthesis.
                </p>
              </div>
            )}
          </div>

          <div className="pt-4 border-t border-border-subtle mt-4">
            <Link to="/app/intelligence" className="w-full block">
              <Button size="sm" variant={portfolio_intelligence.available ? 'outline' : 'glow'} className="w-full" rightIcon={<ArrowRight className="w-3.5 h-3.5" />}>
                {portfolio_intelligence.available ? 'View Full Report' : 'Generate Intelligence'}
              </Button>
            </Link>
          </div>
        </GlassCard>
      </div>

      {/* 4. Watchlist & Recent Alerts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Watchlist Priorities */}
        <GlassCard>
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <Bookmark className="w-4 h-4 text-cyan-600 dark:text-cyan-400" />
              <h3 className="text-sm font-semibold text-slate-900 dark:text-white">Watchlist Priorities</h3>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-xs text-slate-500 dark:text-slate-400 font-mono">
                {watchlist.high_priority_count} High Priority
              </span>
              <Link to="/app/watchlist" className="text-xs text-cyan-600 dark:text-cyan-400 hover:text-cyan-700 dark:hover:text-cyan-300 font-medium">
                Manage
              </Link>
            </div>
          </div>

          {watchlist.items.length === 0 ? (
            <div className="text-center py-8 text-slate-500 text-xs">
              No watchlist items added yet.{' '}
              <Link to="/app/watchlist" className="text-cyan-600 dark:text-cyan-400 underline">
                Add securities
              </Link>
            </div>
          ) : (
            <div className="space-y-2">
              {watchlist.items.map((item) => (
                <div
                  key={item.id}
                  className="flex items-center justify-between p-3 rounded-xl bg-surface-100/60 border border-border-subtle hover:border-border-strong transition-colors"
                >
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="font-bold text-slate-900 dark:text-white text-xs">{item.symbol}</span>
                      <StatusBadge status={item.priority} size="sm" />
                    </div>
                    {item.notes && <p className="text-[11px] text-slate-600 dark:text-slate-400 truncate max-w-xs mt-0.5">{item.notes}</p>}
                  </div>
                  <div className="text-right">
                    <div className="text-xs font-mono font-semibold text-slate-900 dark:text-white">{formatCurrency(item.current_price)}</div>
                    {item.price_change_24h_percent !== undefined && item.price_change_24h_percent !== null && (
                      <div className={item.price_change_24h_percent >= 0 ? 'text-[10px] text-emerald-600 dark:text-emerald-400 font-mono' : 'text-[10px] text-rose-600 dark:text-rose-400 font-mono'}>
                        {formatPercent(item.price_change_24h_percent)}
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </GlassCard>

        {/* Recent Alerts */}
        <GlassCard>
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <BellRing className="w-4 h-4 text-amber-600 dark:text-amber-400" />
              <h3 className="text-sm font-semibold text-slate-900 dark:text-white">Recent Security Alerts</h3>
            </div>
            <Link to="/app/alerts" className="text-xs text-amber-600 dark:text-amber-400 hover:text-amber-700 dark:hover:text-amber-300 font-medium">
              View All ({alerts.unread_count} unread)
            </Link>
          </div>

          {alerts.recent.length === 0 ? (
            <div className="text-center py-8 text-slate-500 text-xs">
              No recent alerts detected. All monitored positions within normal thresholds.
            </div>
          ) : (
            <div className="space-y-2">
              {alerts.recent.map((alert) => (
                <div
                  key={alert.id}
                  className={`p-3 rounded-xl border transition-colors ${
                    !alert.is_read
                      ? 'bg-surface-100 border-border-strong'
                      : 'bg-surface-100/40 border-border-subtle opacity-80'
                  }`}
                >
                  <div className="flex items-center justify-between mb-1">
                    <div className="flex items-center gap-2">
                      <span className="font-bold text-xs text-slate-900 dark:text-white">{alert.symbol}</span>
                      <StatusBadge status={alert.severity} size="sm" />
                    </div>
                    <span className="text-[10px] text-slate-500 font-mono">{formatDate(alert.created_at)}</span>
                  </div>
                  <p className="text-xs text-slate-700 dark:text-slate-300 line-clamp-1">{alert.title}</p>
                </div>
              ))}
            </div>
          )}
        </GlassCard>
      </div>

      {/* 5. System Health, Notifications & Research Row */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Research History Summary */}
        <GlassCard>
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              <Search className="w-4 h-4 text-brand-600 dark:text-brand-400" />
              <h3 className="text-sm font-semibold text-slate-900 dark:text-white">Recent Research</h3>
            </div>
            <Link to="/app/research" className="text-xs text-brand-600 dark:text-brand-400 hover:text-brand-700 dark:hover:text-brand-300">
              History ({research.total_reports})
            </Link>
          </div>
          {research.recent.length === 0 ? (
            <p className="text-xs text-slate-500 py-4">No equity research reports conducted yet.</p>
          ) : (
            <div className="space-y-2">
              {research.recent.slice(0, 3).map((r) => (
                <div key={r.id} className="p-2.5 rounded-lg bg-surface-100/50 border border-border-subtle text-xs">
                  <div className="font-semibold text-slate-900 dark:text-white flex items-center justify-between">
                    <span>{r.symbol}</span>
                    <span className="text-[10px] text-slate-500 dark:text-slate-400 font-mono">{formatDate(r.created_at)}</span>
                  </div>
                  <p className="text-slate-600 dark:text-slate-400 text-[11px] truncate mt-0.5">{r.summary}</p>
                </div>
              ))}
            </div>
          )}
        </GlassCard>

        {/* Notifications Status */}
        <GlassCard>
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              <Radio className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
              <h3 className="text-sm font-semibold text-slate-900 dark:text-white">Notification Delivery</h3>
            </div>
            <Link to="/app/notifications" className="text-xs text-emerald-600 dark:text-emerald-400 hover:text-emerald-700 dark:hover:text-emerald-300">
              Preferences
            </Link>
          </div>
          <div className="space-y-2 text-xs">
            <div className="flex justify-between py-1 border-b border-border-subtle/50">
              <span className="text-slate-500 dark:text-slate-400">Enabled Channels:</span>
              <span className="text-slate-900 dark:text-white font-mono">
                {notifications.enabled_channels.length > 0 ? notifications.enabled_channels.join(', ') : 'None'}
              </span>
            </div>
            <div className="flex justify-between py-1 border-b border-border-subtle/50">
              <span className="text-slate-500 dark:text-slate-400">Successful Deliveries:</span>
              <span className="text-emerald-600 dark:text-emerald-400 font-mono font-medium">{notifications.delivered_count}</span>
            </div>
            <div className="flex justify-between py-1">
              <span className="text-slate-500 dark:text-slate-400">Failed / Retrying:</span>
              <span className={notifications.failed_delivery_count > 0 ? 'text-rose-600 dark:text-rose-400 font-mono font-medium' : 'text-slate-500 dark:text-slate-400 font-mono'}>
                {notifications.failed_delivery_count} failed ({notifications.pending_retry_count} pending)
              </span>
            </div>
          </div>
        </GlassCard>

        {/* Monitoring Operational Status */}
        <GlassCard>
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              <Activity className="w-4 h-4 text-cyan-600 dark:text-cyan-400" />
              <h3 className="text-sm font-semibold text-slate-900 dark:text-white">Monitoring Health</h3>
            </div>
            <Badge variant={monitoring.system_monitoring_enabled ? 'emerald' : 'slate'} size="sm">
              {monitoring.system_monitoring_enabled ? 'System Active' : 'Disabled'}
            </Badge>
          </div>
          <div className="space-y-2 text-xs">
            <div className="flex justify-between py-1 border-b border-border-subtle/50">
              <span className="text-slate-500 dark:text-slate-400">User Alerts Telemetry:</span>
              <span className="text-slate-900 dark:text-white font-mono">{monitoring.user_alerts_enabled ? 'Enabled' : 'Disabled'}</span>
            </div>
            {monitoring.latest_run ? (
              <>
                <div className="flex justify-between py-1 border-b border-border-subtle/50">
                  <span className="text-slate-500 dark:text-slate-400">Latest Scheduled Cycle:</span>
                  <StatusBadge status={monitoring.latest_run.status} size="sm" />
                </div>
                <div className="flex justify-between py-1">
                  <span className="text-slate-500 dark:text-slate-400">Execution Duration:</span>
                  <span className="text-slate-700 dark:text-slate-300 font-mono">
                    {monitoring.latest_run.duration_seconds !== null && monitoring.latest_run.duration_seconds !== undefined
                      ? `${monitoring.latest_run.duration_seconds.toFixed(2)}s`
                      : '—'}
                  </span>
                </div>
              </>
            ) : (
              <p className="text-xs text-slate-500 py-1">No scheduled monitoring runs logged yet.</p>
            )}
          </div>
        </GlassCard>
      </div>
    </div>
  );
};
