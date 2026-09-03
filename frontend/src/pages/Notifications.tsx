import React, { useEffect, useState } from 'react';
import {
  Radio,
  Plus,
  Trash2,
  CheckCircle,
  Clock,
  Save,
  Link as LinkIcon,
  RefreshCw,
} from 'lucide-react';
import { api } from '../lib/api';
import {
  NotificationDelivery,
  NotificationEndpoint,
  NotificationPreference,
} from '../types';
import { useToast } from '../context/ToastContext';
import { GlassCard } from '../components/ui/GlassCard';
import { Button } from '../components/ui/Button';
import { Modal } from '../components/ui/Modal';
import { Input } from '../components/ui/Input';
import { Select } from '../components/ui/Select';
import { StatusBadge } from '../components/ui/StatusBadge';
import { PageHeader } from '../components/ui/PageHeader';
import { Skeleton } from '../components/ui/Skeleton';
import { ErrorState } from '../components/ui/ErrorState';
import {
  Table,
  TableHeader,
  TableBody,
  TableRow,
  TableHead,
  TableCell,
} from '../components/ui/Table';
import { formatDate } from '../lib/utils';

export const Notifications: React.FC = () => {
  const [preferences, setPreferences] = useState<NotificationPreference | null>(null);
  const [endpoints, setEndpoints] = useState<NotificationEndpoint[]>([]);
  const [deliveries, setDeliveries] = useState<NotificationDelivery[]>([]);

  const [isLoading, setIsLoading] = useState(true);
  const [isSavingPrefs, setIsSavingPrefs] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Endpoint Modal
  const [isAddEndpointModalOpen, setIsAddEndpointModalOpen] = useState(false);
  const [isDeleteEndpointModalOpen, setIsDeleteEndpointModalOpen] = useState(false);
  const [selectedEndpoint, setSelectedEndpoint] = useState<NotificationEndpoint | null>(null);
  const [endpointUrl, setEndpointUrl] = useState('');
  const [secretKey, setSecretKey] = useState('');
  const [isSubmittingEndpoint, setIsSubmittingEndpoint] = useState(false);
  const [endpointError, setEndpointError] = useState<string | null>(null);

  const { showToast } = useToast();

  const fetchNotificationData = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const [prefRes, epRes, delRes] = await Promise.all([
        api.notifications.getPreferences(),
        api.notifications.listEndpoints(),
        api.notifications.listDeliveries({ limit: 20 }),
      ]);
      const loadedPrefs = prefRes.preferences
        ? {
            ...prefRes.preferences,
            alert_types: Array.isArray(prefRes.preferences.alert_types)
              ? prefRes.preferences.alert_types
              : ['price_move', 'portfolio_gain_loss', 'watchlist_move', 'data_quality'],
          }
        : null;
      setPreferences(loadedPrefs);
      setEndpoints(epRes.endpoints || []);
      setDeliveries(delRes.deliveries || []);
    } catch (err: any) {
      setError(err.message || 'Failed to load notification settings.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchNotificationData();
  }, []);

  const handleSavePreferences = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!preferences) return;

    setIsSavingPrefs(true);
    try {
      const res = await api.notifications.updatePreferences({
        in_app_enabled: preferences.in_app_enabled,
        email_enabled: preferences.email_enabled,
        webhook_enabled: preferences.webhook_enabled,
        minimum_severity: preferences.minimum_severity,
        alert_types: preferences.alert_types || ['price_move', 'portfolio_gain_loss', 'watchlist_move', 'data_quality'],
      });
      setPreferences({
        ...res.preferences,
        alert_types: Array.isArray(res.preferences.alert_types)
          ? res.preferences.alert_types
          : ['price_move', 'portfolio_gain_loss', 'watchlist_move', 'data_quality'],
      });
      showToast('Notification preferences saved.', 'success');
    } catch (err: any) {
      showToast(err.message || 'Failed to save preferences.', 'error');
    } finally {
      setIsSavingPrefs(false);
    }
  };

  const handleToggleAlertType = (type: string) => {
    if (!preferences) return;
    const currentTypes = Array.isArray(preferences.alert_types)
      ? preferences.alert_types
      : ['price_move', 'portfolio_gain_loss', 'watchlist_move', 'data_quality'];
    const exists = currentTypes.includes(type);
    const updated = exists
      ? currentTypes.filter((t) => t !== type)
      : [...currentTypes, type];
    setPreferences({ ...preferences, alert_types: updated });
  };

  const handleCreateEndpoint = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!endpointUrl.trim()) {
      setEndpointError('Endpoint URL is required.');
      return;
    }

    setIsSubmittingEndpoint(true);
    setEndpointError(null);
    try {
      await api.notifications.createEndpoint({
        endpoint_url: endpointUrl.trim(),
        secret_key: secretKey.trim() || undefined,
      });
      showToast('Webhook endpoint configured.', 'success');
      setIsAddEndpointModalOpen(false);
      setEndpointUrl('');
      setSecretKey('');
      const epRes = await api.notifications.listEndpoints();
      setEndpoints(epRes.endpoints);
    } catch (err: any) {
      setEndpointError(err.message || 'Failed to create endpoint.');
    } finally {
      setIsSubmittingEndpoint(false);
    }
  };

  const handleDeleteEndpoint = async () => {
    if (!selectedEndpoint) return;
    setIsSubmittingEndpoint(true);
    try {
      await api.notifications.deleteEndpoint(selectedEndpoint.id);
      showToast('Webhook endpoint removed.', 'info');
      setIsDeleteEndpointModalOpen(false);
      const epRes = await api.notifications.listEndpoints();
      setEndpoints(epRes.endpoints);
    } catch (err: any) {
      showToast(err.message || 'Failed to delete endpoint.', 'error');
    } finally {
      setIsSubmittingEndpoint(false);
    }
  };

  if (isLoading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-10 w-64" />
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Skeleton className="h-80 rounded-2xl" />
          <Skeleton className="h-80 rounded-2xl" />
        </div>
        <Skeleton className="h-80 rounded-2xl" />
      </div>
    );
  }

  if (error || !preferences) {
    return <ErrorState message={error || 'Failed to load notifications'} onRetry={fetchNotificationData} />;
  }

  return (
    <div className="space-y-8 animate-in fade-in duration-300">
      <PageHeader
        title="Notification Channels & Telemetry"
        subtitle="Multi-channel delivery preferences, webhook endpoints, and immutable audit logs."
        actions={
          <Button onClick={fetchNotificationData} size="sm" variant="secondary" leftIcon={<RefreshCw className="w-3.5 h-3.5" />}>
            Refresh
          </Button>
        }
      />

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left 6 Cols: Notification Preferences */}
        <div className="lg:col-span-6 space-y-6">
          <GlassCard className="p-6">
            <div className="flex items-center gap-2 mb-4 pb-3 border-b border-border-subtle">
              <Radio className="w-4 h-4 text-emerald-400" />
              <h3 className="text-sm font-semibold text-white">Delivery Channel Preferences</h3>
            </div>

            <form onSubmit={handleSavePreferences} className="space-y-5">
              {/* Channel Toggles */}
              <div className="space-y-3">
                <label className="text-xs font-semibold uppercase tracking-wider text-slate-400 block">
                  Active Channels
                </label>

                <div className="space-y-2">
                  <label className="flex items-center justify-between p-3 rounded-xl bg-surface-100/60 dark:bg-surface-100/60 border border-border-subtle hover:border-border-strong cursor-pointer transition-colors">
                    <div>
                      <div className="text-xs font-semibold text-slate-900 dark:text-white">In-App Notification Stream</div>
                      <div className="text-[11px] text-slate-500 dark:text-slate-400">Display instant toast and badge alerts in dashboard.</div>
                    </div>
                    <input
                      type="checkbox"
                      checked={preferences.in_app_enabled}
                      onChange={(e) => setPreferences({ ...preferences, in_app_enabled: e.target.checked })}
                      className="rounded bg-surface-200 border-border-strong text-brand-600 focus:ring-brand-500 w-4 h-4"
                    />
                  </label>

                  <label className="flex items-center justify-between p-3 rounded-xl bg-surface-100/60 dark:bg-surface-100/60 border border-border-subtle hover:border-border-strong cursor-pointer transition-colors">
                    <div>
                      <div className="text-xs font-semibold text-slate-900 dark:text-white">Email Digest & Alerts</div>
                      <div className="text-[11px] text-slate-500 dark:text-slate-400">Send critical alerts to verified registered email.</div>
                    </div>
                    <input
                      type="checkbox"
                      checked={preferences.email_enabled}
                      onChange={(e) => setPreferences({ ...preferences, email_enabled: e.target.checked })}
                      className="rounded bg-surface-200 border-border-strong text-brand-600 focus:ring-brand-500 w-4 h-4"
                    />
                  </label>

                  <label className="flex items-center justify-between p-3 rounded-xl bg-surface-100/60 dark:bg-surface-100/60 border border-border-subtle hover:border-border-strong cursor-pointer transition-colors">
                    <div>
                      <div className="text-xs font-semibold text-slate-900 dark:text-white">External Webhooks</div>
                      <div className="text-[11px] text-slate-500 dark:text-slate-400">Deliver signed HMAC payloads to custom endpoints.</div>
                    </div>
                    <input
                      type="checkbox"
                      checked={preferences.webhook_enabled}
                      onChange={(e) => setPreferences({ ...preferences, webhook_enabled: e.target.checked })}
                      className="rounded bg-surface-200 border-border-strong text-brand-600 focus:ring-brand-500 w-4 h-4"
                    />
                  </label>
                </div>
              </div>

              {/* Minimum Severity */}
              <Select
                label="Minimum Severity Threshold"
                value={preferences.minimum_severity}
                onChange={(e) => setPreferences({ ...preferences, minimum_severity: e.target.value })}
                options={[
                  { value: 'info', label: 'Info (All Alerts & Status Updates)' },
                  { value: 'warning', label: 'Warning (Significant Moves & Drawdowns)' },
                  { value: 'critical', label: 'Critical Only (Emergency Thresholds)' },
                ]}
              />

              {/* Alert Types Multi-Select */}
              <div className="space-y-2">
                <label className="text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400 block">
                  Included Alert Categories
                </label>
                <div className="grid grid-cols-2 gap-2">
                  {[
                    { id: 'price_move', label: 'Price Move' },
                    { id: 'portfolio_gain_loss', label: 'Portfolio Gain/Loss' },
                    { id: 'watchlist_move', label: 'Watchlist Move' },
                    { id: 'data_quality', label: 'Data Quality' },
                  ].map((cat) => {
                    const isChecked = Array.isArray(preferences.alert_types) && preferences.alert_types.includes(cat.id);
                    return (
                      <button
                        type="button"
                        key={cat.id}
                        onClick={() => handleToggleAlertType(cat.id)}
                        className={`px-3 py-2 rounded-xl text-xs font-medium border text-left flex items-center justify-between transition-colors ${
                          isChecked
                            ? 'bg-brand-500/15 dark:bg-brand-600/10 border-brand-500 text-brand-700 dark:text-brand-200'
                            : 'bg-surface-50 dark:bg-surface-100/40 border-border-subtle text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200'
                        }`}
                      >
                        <span>{cat.label}</span>
                        {isChecked && <CheckCircle className="w-3.5 h-3.5 text-brand-600 dark:text-brand-400" />}
                      </button>
                    );
                  })}
                </div>
              </div>

              <div className="pt-2">
                <Button
                  type="submit"
                  variant="glow"
                  isLoading={isSavingPrefs}
                  leftIcon={<Save className="w-4 h-4" />}
                >
                  Save Notification Preferences
                </Button>
              </div>
            </form>
          </GlassCard>
        </div>

        {/* Right 6 Cols: Webhook Endpoints */}
        <div className="lg:col-span-6 space-y-6">
          <GlassCard className="p-6">
            <div className="flex items-center justify-between gap-4 mb-4 pb-3 border-b border-border-subtle">
              <div className="flex items-center gap-2">
                <LinkIcon className="w-4 h-4 text-cyan-600 dark:text-cyan-400" />
                <h3 className="text-sm font-semibold text-slate-900 dark:text-white">Webhook Endpoints ({endpoints.length})</h3>
              </div>
              <Button
                onClick={() => {
                  setEndpointUrl('');
                  setSecretKey('');
                  setEndpointError(null);
                  setIsAddEndpointModalOpen(true);
                }}
                size="sm"
                variant="secondary"
                leftIcon={<Plus className="w-3.5 h-3.5" />}
              >
                Add Webhook
              </Button>
            </div>

            {endpoints.length === 0 ? (
              <div className="p-8 rounded-2xl border border-dashed border-border-strong text-center text-xs text-slate-500 bg-surface-100 dark:bg-surface-200/30">
                No webhook endpoints registered. Add an HTTPS webhook endpoint to receive machine-readable alert notifications.
              </div>
            ) : (
              <div className="space-y-2.5">
                {endpoints.map((ep) => (
                  <div
                    key={ep.id}
                    className="p-3.5 rounded-xl bg-surface-50 dark:bg-surface-100/60 border border-border-subtle flex items-start justify-between gap-3 hover:border-border-strong transition-colors"
                  >
                    <div className="space-y-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <span className="font-mono text-xs font-semibold text-slate-900 dark:text-white truncate max-w-sm">
                          {ep.endpoint_url}
                        </span>
                        <StatusBadge status={ep.is_enabled ? 'active' : 'disabled'} size="sm" />
                      </div>
                      <div className="flex items-center gap-2 text-[10px] text-slate-500 dark:text-slate-400 font-mono">
                        <span>Channel: {ep.channel}</span>
                        <span>• Added {formatDate(ep.created_at)}</span>
                      </div>
                    </div>

                    <button
                      onClick={() => {
                        setSelectedEndpoint(ep);
                        setIsDeleteEndpointModalOpen(true);
                      }}
                      className="p-1.5 rounded-lg text-slate-400 hover:text-rose-600 dark:hover:text-rose-400 hover:bg-rose-500/10 transition-colors shrink-0"
                      title="Delete Webhook"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </GlassCard>
        </div>
      </div>

      {/* Delivery Logs Table */}
      <GlassCard className="p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <Clock className="w-4 h-4 text-slate-500 dark:text-slate-400" />
            <h3 className="text-sm font-semibold text-slate-900 dark:text-white">Recent Delivery Audit Trail ({deliveries.length})</h3>
          </div>
        </div>

        {deliveries.length === 0 ? (
          <div className="text-center py-8 text-slate-500 text-xs">
            No notification deliveries recorded yet.
          </div>
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Channel</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Alert ID</TableHead>
                <TableHead>Attempts</TableHead>
                <TableHead>Error Message</TableHead>
                <TableHead className="text-right">Timestamp</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {deliveries.map((del) => (
                <TableRow key={del.id}>
                  <TableCell>
                    <span className="font-mono text-xs font-semibold text-slate-900 dark:text-white uppercase">{del.channel}</span>
                  </TableCell>
                  <TableCell>
                    <StatusBadge status={del.status} size="sm" />
                  </TableCell>
                  <TableCell className="font-mono text-xs text-slate-700 dark:text-slate-300">#{del.alert_id}</TableCell>
                  <TableCell className="font-mono text-xs text-slate-700 dark:text-slate-300">{del.attempt_count}</TableCell>
                  <TableCell>
                    <span className="text-xs text-rose-600 dark:text-rose-300 line-clamp-1 max-w-xs font-mono">
                      {del.error_message || '—'}
                    </span>
                  </TableCell>
                  <TableCell className="text-right font-mono text-xs text-slate-500 dark:text-slate-400">
                    {formatDate(del.created_at)}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </GlassCard>

      {/* Add Webhook Modal */}
      <Modal
        isOpen={isAddEndpointModalOpen}
        onClose={() => setIsAddEndpointModalOpen(false)}
        title="Configure Webhook Endpoint"
      >
        <form onSubmit={handleCreateEndpoint} className="space-y-4">
          {endpointError && <p className="text-xs text-rose-600 dark:text-rose-400">{endpointError}</p>}
          <Input
            label="Webhook URL"
            type="url"
            placeholder="https://api.domain.com/v1/webhook"
            value={endpointUrl}
            onChange={(e) => setEndpointUrl(e.target.value)}
            required
            helperText="Must be a valid HTTPS URL (SSRF protected)."
          />
          <Input
            label="Secret Key (Optional HMAC Signing)"
            type="password"
            placeholder="webhook_secret_key"
            value={secretKey}
            onChange={(e) => setSecretKey(e.target.value)}
            helperText="Used to compute SHA-256 HMAC signatures."
          />
          <div className="flex justify-end gap-2.5 pt-3 border-t border-border-subtle">
            <Button type="button" variant="secondary" size="sm" onClick={() => setIsAddEndpointModalOpen(false)}>
              Cancel
            </Button>
            <Button type="submit" variant="glow" size="sm" isLoading={isSubmittingEndpoint}>
              Register Webhook
            </Button>
          </div>
        </form>
      </Modal>

      {/* Delete Webhook Modal */}
      <Modal
        isOpen={isDeleteEndpointModalOpen}
        onClose={() => setIsDeleteEndpointModalOpen(false)}
        title="Remove Webhook Endpoint"
      >
        <div className="space-y-4">
          <p className="text-xs text-slate-700 dark:text-slate-300">
            Are you sure you want to delete <strong className="text-slate-900 dark:text-white">{selectedEndpoint?.endpoint_url}</strong>?
          </p>
          <div className="flex justify-end gap-2.5 pt-3 border-t border-border-subtle">
            <Button variant="secondary" size="sm" onClick={() => setIsDeleteEndpointModalOpen(false)}>
              Cancel
            </Button>
            <Button variant="danger" size="sm" isLoading={isSubmittingEndpoint} onClick={handleDeleteEndpoint}>
              Delete Webhook
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
};
