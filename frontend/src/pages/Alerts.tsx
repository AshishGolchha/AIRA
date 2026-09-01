import React, { useEffect, useState } from 'react';
import {
  BellRing,
  CheckCircle,
  XCircle,
  Play,
} from 'lucide-react';
import { api } from '../lib/api';
import { Alert } from '../types';
import { useToast } from '../context/ToastContext';
import { GlassCard } from '../components/ui/GlassCard';
import { Button } from '../components/ui/Button';
import { StatusBadge } from '../components/ui/StatusBadge';
import { PageHeader } from '../components/ui/PageHeader';
import { EmptyState } from '../components/ui/EmptyState';
import { Skeleton } from '../components/ui/Skeleton';
import { ErrorState } from '../components/ui/ErrorState';
import { formatDate } from '../lib/utils';

export const Alerts: React.FC = () => {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [unreadOnly, setUnreadOnly] = useState(false);
  const [severityFilter, setSeverityFilter] = useState<string>('all');
  const [isLoading, setIsLoading] = useState(true);
  const [isChecking, setIsChecking] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const { showToast } = useToast();

  const fetchAlerts = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const res = await api.alerts.list({ unread_only: unreadOnly });
      setAlerts(res.alerts);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch alerts.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchAlerts();
  }, [unreadOnly]);

  const handleRunAlertCheck = async () => {
    setIsChecking(true);
    try {
      const res = await api.alerts.check();
      showToast(
        res.created_count > 0
          ? `Alert check complete: ${res.created_count} new alert(s) detected.`
          : 'Alert check complete: All monitored assets within nominal parameters.',
        res.created_count > 0 ? 'info' : 'success'
      );
      fetchAlerts();
    } catch (err: any) {
      showToast(err.message || 'Failed to run alert check.', 'error');
    } finally {
      setIsChecking(false);
    }
  };

  const handleMarkAsRead = async (id: number) => {
    try {
      await api.alerts.markAsRead(id);
      setAlerts((prev) => prev.map((a) => (a.id === id ? { ...a, is_read: true } : a)));
      showToast('Alert marked as read.', 'success');
    } catch (err: any) {
      showToast(err.message || 'Failed to update alert.', 'error');
    }
  };

  const handleDismiss = async (id: number) => {
    try {
      await api.alerts.dismiss(id);
      setAlerts((prev) => prev.filter((a) => a.id !== id));
      showToast('Alert dismissed.', 'info');
    } catch (err: any) {
      showToast(err.message || 'Failed to dismiss alert.', 'error');
    }
  };

  const filteredAlerts = alerts.filter((a) => {
    if (severityFilter !== 'all' && a.severity !== severityFilter) return false;
    return true;
  });

  const criticalCount = alerts.filter((a) => a.severity === 'critical').length;
  const warningCount = alerts.filter((a) => a.severity === 'warning').length;
  const unreadCount = alerts.filter((a) => !a.is_read).length;

  return (
    <div className="space-y-8 animate-in fade-in duration-300">
      <PageHeader
        title="Alert Telemetry"
        subtitle="Automated price thresholds, portfolio drawdown detection, and deterministic rule evaluation."
        actions={
          <Button
            onClick={handleRunAlertCheck}
            size="sm"
            variant="glow"
            isLoading={isChecking}
            leftIcon={<Play className="w-3.5 h-3.5 fill-current" />}
          >
            Run Alert Evaluation
          </Button>
        }
      />

      {/* Filter and Stats Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="flex items-center gap-2">
          <Button
            size="sm"
            variant={severityFilter === 'all' ? 'primary' : 'secondary'}
            onClick={() => setSeverityFilter('all')}
          >
            All ({alerts.length})
          </Button>
          <Button
            size="sm"
            variant={severityFilter === 'critical' ? 'danger' : 'secondary'}
            onClick={() => setSeverityFilter('critical')}
          >
            Critical ({criticalCount})
          </Button>
          <Button
            size="sm"
            variant={severityFilter === 'warning' ? 'primary' : 'secondary'}
            onClick={() => setSeverityFilter('warning')}
          >
            Warning ({warningCount})
          </Button>
        </div>

        <div className="flex items-center gap-3">
          <label className="flex items-center gap-2 text-xs text-slate-700 dark:text-slate-300 select-none cursor-pointer">
            <input
              type="checkbox"
              checked={unreadOnly}
              onChange={(e) => setUnreadOnly(e.target.checked)}
              className="rounded bg-surface-100 border-border-strong text-brand-600 focus:ring-brand-500"
            />
            <span>Show Unread Only ({unreadCount})</span>
          </label>
        </div>
      </div>

      {isLoading ? (
        <div className="space-y-4">
          <Skeleton className="h-28 rounded-2xl" />
          <Skeleton className="h-28 rounded-2xl" />
          <Skeleton className="h-28 rounded-2xl" />
        </div>
      ) : error ? (
        <ErrorState message={error} onRetry={fetchAlerts} />
      ) : filteredAlerts.length === 0 ? (
        <EmptyState
          icon={BellRing}
          title="No Alerts Found"
          description="All positions and watchlist securities are within acceptable thresholds. Click below to run a fresh evaluation cycle."
          actionLabel="Run Alert Evaluation"
          onAction={handleRunAlertCheck}
          actionIcon={<Play className="w-3.5 h-3.5 fill-current" />}
        />
      ) : (
        <div className="space-y-3">
          {filteredAlerts.map((alert) => (
            <GlassCard
              key={alert.id}
              className={`p-5 transition-all duration-200 ${
                !alert.is_read
                  ? 'border-border-strong bg-surface-50 dark:bg-surface-100/90 shadow-sm'
                  : 'border-border-subtle bg-surface-100/50 dark:bg-surface-200/50 opacity-80'
              }`}
            >
              <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4">
                <div className="space-y-1.5 flex-1">
                  <div className="flex flex-wrap items-center gap-2.5">
                    <span className="font-bold text-base text-slate-900 dark:text-white">{alert.symbol}</span>
                    <StatusBadge status={alert.severity} size="md" />
                    <span className="text-xs px-2 py-0.5 rounded-md bg-surface-100 dark:bg-surface-100 border border-border-subtle text-slate-600 dark:text-slate-400 font-mono">
                      {alert.alert_type.replace(/_/g, ' ')}
                    </span>
                    {!alert.is_read && (
                      <span className="w-2 h-2 rounded-full bg-brand-500 animate-ping" />
                    )}
                  </div>

                  <h4 className="text-sm font-semibold text-slate-900 dark:text-white pt-1">{alert.title}</h4>
                  <p className="text-xs text-slate-700 dark:text-slate-300 leading-relaxed">{alert.message}</p>

                  {alert.context_data && Object.keys(alert.context_data).length > 0 && (
                    <div className="mt-3 p-3 rounded-xl bg-surface-100 dark:bg-surface-300/80 border border-border-subtle/80 text-[11px] font-mono text-slate-600 dark:text-slate-400 space-y-1">
                      <div className="text-slate-500 dark:text-slate-400 uppercase tracking-wider text-[10px] font-semibold mb-1">
                        Deterministic Context Metrics
                      </div>
                      <div className="flex flex-wrap gap-4">
                        {Object.entries(alert.context_data).map(([k, v]) => (
                          <div key={k} className="flex items-center gap-1.5">
                            <span className="text-slate-500 dark:text-slate-400">{k}:</span>
                            <span className="text-slate-900 dark:text-slate-200 font-semibold">{String(v)}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  <div className="text-[11px] text-slate-500 dark:text-slate-400 font-mono pt-1">
                    Detected on {formatDate(alert.created_at)}
                  </div>
                </div>

                {/* Actions */}
                <div className="flex items-center gap-2 shrink-0 self-end sm:self-start">
                  {!alert.is_read && (
                    <Button
                      size="sm"
                      variant="secondary"
                      onClick={() => handleMarkAsRead(alert.id)}
                      leftIcon={<CheckCircle className="w-3.5 h-3.5 text-emerald-600 dark:text-emerald-400" />}
                    >
                      Mark Read
                    </Button>
                  )}
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={() => handleDismiss(alert.id)}
                    className="text-slate-400 hover:text-rose-600 dark:hover:text-rose-400"
                    leftIcon={<XCircle className="w-3.5 h-3.5" />}
                  >
                    Dismiss
                  </Button>
                </div>
              </div>
            </GlassCard>
          ))}
        </div>
      )}
    </div>
  );
};
