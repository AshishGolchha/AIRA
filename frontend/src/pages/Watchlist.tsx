import React, { useEffect, useState } from 'react';
import { Bookmark, Plus, Edit2, Trash2, RefreshCw } from 'lucide-react';
import { api } from '../lib/api';
import { WatchlistItem, WatchlistPriority } from '../types';
import { useToast } from '../context/ToastContext';
import { GlassCard } from '../components/ui/GlassCard';
import { Button } from '../components/ui/Button';
import { Modal } from '../components/ui/Modal';
import { Input } from '../components/ui/Input';
import { Select } from '../components/ui/Select';
import { PageHeader } from '../components/ui/PageHeader';
import { StatusBadge } from '../components/ui/StatusBadge';
import { Tabs } from '../components/ui/Tabs';
import { EmptyState } from '../components/ui/EmptyState';
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
import { formatCurrency, formatPercent, formatDateOnly } from '../lib/utils';

export const Watchlist: React.FC = () => {
  const [items, setItems] = useState<WatchlistItem[]>([]);
  const [activeTab, setActiveTab] = useState<string>('all');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Modals
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
  const [selectedItem, setSelectedItem] = useState<WatchlistItem | null>(null);

  // Form
  const [symbol, setSymbol] = useState('');
  const [priority, setPriority] = useState<WatchlistPriority>('normal');
  const [notes, setNotes] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  const { showToast } = useToast();

  const fetchWatchlist = async (filterPriority?: WatchlistPriority) => {
    setIsLoading(true);
    setError(null);
    try {
      const res = await api.watchlist.list(filterPriority);
      setItems(res.items);
    } catch (err: any) {
      setError(err.message || 'Failed to load watchlist items.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    const filter = activeTab === 'all' ? undefined : (activeTab as WatchlistPriority);
    fetchWatchlist(filter);
  }, [activeTab]);

  const handleOpenAdd = () => {
    setSymbol('');
    setPriority('normal');
    setNotes('');
    setFormError(null);
    setIsAddModalOpen(true);
  };

  const handleOpenEdit = (item: WatchlistItem) => {
    setSelectedItem(item);
    setSymbol(item.symbol);
    setPriority(item.priority);
    setNotes(item.notes || '');
    setFormError(null);
    setIsEditModalOpen(true);
  };

  const handleOpenDelete = (item: WatchlistItem) => {
    setSelectedItem(item);
    setIsDeleteModalOpen(true);
  };

  const handleCreateItem = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!symbol.trim()) {
      setFormError('Symbol is required.');
      return;
    }

    setIsSubmitting(true);
    setFormError(null);
    try {
      await api.watchlist.create({
        symbol: symbol.trim().toUpperCase(),
        priority,
        notes: notes.trim() || undefined,
      });
      showToast(`Added ${symbol.toUpperCase()} to watchlist.`, 'success');
      setIsAddModalOpen(false);
      fetchWatchlist(activeTab === 'all' ? undefined : (activeTab as WatchlistPriority));
    } catch (err: any) {
      setFormError(err.message || 'Failed to add item.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleUpdateItem = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedItem) return;

    setIsSubmitting(true);
    setFormError(null);
    try {
      await api.watchlist.update(selectedItem.id, {
        priority,
        notes: notes.trim() || undefined,
      });
      showToast(`Updated watchlist item ${selectedItem.symbol}.`, 'success');
      setIsEditModalOpen(false);
      fetchWatchlist(activeTab === 'all' ? undefined : (activeTab as WatchlistPriority));
    } catch (err: any) {
      setFormError(err.message || 'Failed to update item.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDeleteItem = async () => {
    if (!selectedItem) return;
    setIsSubmitting(true);
    try {
      await api.watchlist.delete(selectedItem.id);
      showToast(`Removed ${selectedItem.symbol} from watchlist.`, 'success');
      setIsDeleteModalOpen(false);
      fetchWatchlist(activeTab === 'all' ? undefined : (activeTab as WatchlistPriority));
    } catch (err: any) {
      showToast(err.message || 'Failed to delete item.', 'error');
    } finally {
      setIsSubmitting(false);
    }
  };

  const highCount = items.filter((i) => i.priority === 'high').length;
  const normalCount = items.filter((i) => i.priority === 'normal').length;
  const lowCount = items.filter((i) => i.priority === 'low').length;

  return (
    <div className="space-y-8 animate-in fade-in duration-300">
      <PageHeader
        title="Watchlist Intelligence"
        subtitle="Monitor high-conviction securities, price movements, and AI synthesis triggers."
        actions={
          <>
            <Button
              onClick={() => fetchWatchlist(activeTab === 'all' ? undefined : (activeTab as WatchlistPriority))}
              size="sm"
              variant="secondary"
              leftIcon={<RefreshCw className="w-3.5 h-3.5" />}
            >
              Refresh
            </Button>
            <Button onClick={handleOpenAdd} size="sm" variant="glow" leftIcon={<Plus className="w-4 h-4" />}>
              Add Ticker
            </Button>
          </>
        }
      />

      {/* Tabs Filter */}
      <div className="flex items-center justify-between gap-4">
        <Tabs
          tabs={[
            { id: 'all', label: 'All Items', count: items.length },
            { id: 'high', label: 'High Priority', count: highCount },
            { id: 'normal', label: 'Normal', count: normalCount },
            { id: 'low', label: 'Low Priority', count: lowCount },
          ]}
          activeTab={activeTab}
          onChange={setActiveTab}
        />
      </div>

      {isLoading ? (
        <Skeleton className="h-80 rounded-2xl" />
      ) : error ? (
        <ErrorState message={error} onRetry={() => fetchWatchlist()} />
      ) : items.length === 0 ? (
        <EmptyState
          icon={Bookmark}
          title="Watchlist is Empty"
          description="Track promising companies and receive automated alerts when key price thresholds are triggered."
          actionLabel="Add Security"
          onAction={handleOpenAdd}
          actionIcon={<Plus className="w-4 h-4" />}
        />
      ) : (
        <GlassCard className="p-6">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Symbol & Company</TableHead>
                <TableHead>Priority</TableHead>
                <TableHead className="text-right">Market Price</TableHead>
                <TableHead className="text-right">24h Change</TableHead>
                <TableHead>Research Notes</TableHead>
                <TableHead className="text-right">Added Date</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {items.map((item) => {
                const isGain = (item.price_change_24h_percent || 0) >= 0;
                return (
                  <TableRow key={item.id}>
                    <TableCell>
                      <div className="font-bold text-white text-sm">{item.symbol}</div>
                      <div className="text-xs text-slate-400 truncate max-w-[180px]">
                        {item.company_name || 'Equity Security'}
                      </div>
                    </TableCell>
                    <TableCell>
                      <StatusBadge status={item.priority} size="sm" />
                    </TableCell>
                    <TableCell className="text-right font-mono text-sm font-semibold text-white">
                      {item.quote_available !== false ? formatCurrency(item.current_price) : 'Quote Unavailable'}
                    </TableCell>
                    <TableCell className="text-right font-mono text-sm">
                      {item.price_change_24h_percent !== undefined && item.price_change_24h_percent !== null ? (
                        <span className={isGain ? 'text-emerald-400 font-medium' : 'text-rose-400 font-medium'}>
                          {formatPercent(item.price_change_24h_percent)}
                        </span>
                      ) : (
                        '—'
                      )}
                    </TableCell>
                    <TableCell>
                      <span className="text-xs text-slate-300 line-clamp-1 max-w-xs">{item.notes || '—'}</span>
                    </TableCell>
                    <TableCell className="text-right font-mono text-xs text-slate-400">
                      {formatDateOnly(item.created_at)}
                    </TableCell>
                    <TableCell className="text-right">
                      <div className="flex items-center justify-end gap-1.5">
                        <button
                          onClick={() => handleOpenEdit(item)}
                          className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-white/5 transition-colors"
                          title="Edit Item"
                        >
                          <Edit2 className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => handleOpenDelete(item)}
                          className="p-1.5 rounded-lg text-slate-400 hover:text-rose-400 hover:bg-rose-500/10 transition-colors"
                          title="Remove from Watchlist"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
        </GlassCard>
      )}

      {/* Add Modal */}
      <Modal isOpen={isAddModalOpen} onClose={() => setIsAddModalOpen(false)} title="Add to Watchlist">
        <form onSubmit={handleCreateItem} className="space-y-4">
          {formError && <p className="text-xs text-rose-400">{formError}</p>}
          <Input
            label="Ticker Symbol"
            placeholder="e.g. AMD, TSLA, PLTR"
            value={symbol}
            onChange={(e) => setSymbol(e.target.value.toUpperCase())}
            required
          />
          <Select
            label="Monitoring Priority"
            value={priority}
            onChange={(e) => setPriority(e.target.value as WatchlistPriority)}
            options={[
              { value: 'high', label: 'High Priority (Priority Telemetry)' },
              { value: 'normal', label: 'Normal Priority' },
              { value: 'low', label: 'Low Priority' },
            ]}
          />
          <Input
            label="Notes / Thesis (Optional)"
            placeholder="Target buy zone, catalyst date..."
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
          />
          <div className="flex justify-end gap-2.5 pt-3 border-t border-border-subtle">
            <Button type="button" variant="secondary" size="sm" onClick={() => setIsAddModalOpen(false)}>
              Cancel
            </Button>
            <Button type="submit" variant="glow" size="sm" isLoading={isSubmitting}>
              Add to Watchlist
            </Button>
          </div>
        </form>
      </Modal>

      {/* Edit Modal */}
      <Modal isOpen={isEditModalOpen} onClose={() => setIsEditModalOpen(false)} title={`Edit Watchlist: ${symbol}`}>
        <form onSubmit={handleUpdateItem} className="space-y-4">
          {formError && <p className="text-xs text-rose-400">{formError}</p>}
          <Select
            label="Monitoring Priority"
            value={priority}
            onChange={(e) => setPriority(e.target.value as WatchlistPriority)}
            options={[
              { value: 'high', label: 'High Priority' },
              { value: 'normal', label: 'Normal Priority' },
              { value: 'low', label: 'Low Priority' },
            ]}
          />
          <Input
            label="Notes / Thesis"
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
          />
          <div className="flex justify-end gap-2.5 pt-3 border-t border-border-subtle">
            <Button type="button" variant="secondary" size="sm" onClick={() => setIsEditModalOpen(false)}>
              Cancel
            </Button>
            <Button type="submit" variant="glow" size="sm" isLoading={isSubmitting}>
              Save Changes
            </Button>
          </div>
        </form>
      </Modal>

      {/* Delete Modal */}
      <Modal isOpen={isDeleteModalOpen} onClose={() => setIsDeleteModalOpen(false)} title="Remove from Watchlist">
        <div className="space-y-4">
          <p className="text-xs text-slate-300">
            Remove <strong className="text-white">{selectedItem?.symbol}</strong> from your watchlist?
          </p>
          <div className="flex justify-end gap-2.5 pt-3 border-t border-border-subtle">
            <Button variant="secondary" size="sm" onClick={() => setIsDeleteModalOpen(false)}>
              Cancel
            </Button>
            <Button variant="danger" size="sm" isLoading={isSubmitting} onClick={handleDeleteItem}>
              Remove
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
};
