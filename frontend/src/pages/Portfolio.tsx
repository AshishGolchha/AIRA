import React, { useEffect, useState } from 'react';
import {
  PieChart,
  Plus,
  Edit2,
  Trash2,
  RefreshCw,
  Layers,
} from 'lucide-react';
import { api } from '../lib/api';
import { HoldingValuation, PortfolioSnapshot } from '../types';
import { useToast } from '../context/ToastContext';
import { GlassCard } from '../components/ui/GlassCard';
import { Button } from '../components/ui/Button';
import { Modal } from '../components/ui/Modal';
import { Input } from '../components/ui/Input';
import { PageHeader } from '../components/ui/PageHeader';
import { MetricCard } from '../components/ui/MetricCard';
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
import {
  formatCurrency,
  formatPercent,
  formatNumber,
  formatDate,
} from '../lib/utils';

export const Portfolio: React.FC = () => {
  const [snapshot, setSnapshot] = useState<PortfolioSnapshot | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Modal States
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
  const [selectedHolding, setSelectedHolding] = useState<HoldingValuation | null>(null);

  // Form States
  const [symbol, setSymbol] = useState('');
  const [quantity, setQuantity] = useState('');
  const [averageCost, setAverageCost] = useState('');
  const [notes, setNotes] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  const { showToast } = useToast();

  const fetchPortfolio = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const res = await api.portfolio.getSnapshot();
      setSnapshot(res.snapshot);
    } catch (err: any) {
      setError(err.message || 'Failed to load portfolio snapshot.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchPortfolio();
  }, []);

  const handleOpenAdd = () => {
    setSymbol('');
    setQuantity('');
    setAverageCost('');
    setNotes('');
    setFormError(null);
    setIsAddModalOpen(true);
  };

  const handleOpenEdit = (holding: HoldingValuation) => {
    setSelectedHolding(holding);
    setSymbol(holding.symbol);
    setQuantity(holding.quantity.toString());
    setAverageCost(holding.average_cost.toString());
    setNotes(holding.notes || '');
    setFormError(null);
    setIsEditModalOpen(true);
  };

  const handleOpenDelete = (holding: HoldingValuation) => {
    setSelectedHolding(holding);
    setIsDeleteModalOpen(true);
  };

  const handleCreateHolding = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!symbol.trim()) {
      setFormError('Symbol is required.');
      return;
    }
    const qty = parseFloat(quantity);
    const cost = parseFloat(averageCost);
    if (isNaN(qty) || qty <= 0) {
      setFormError('Quantity must be a positive number.');
      return;
    }
    if (isNaN(cost) || cost < 0) {
      setFormError('Average cost must be a non-negative number.');
      return;
    }

    setIsSubmitting(true);
    setFormError(null);
    try {
      await api.portfolio.createHolding({
        symbol: symbol.trim().toUpperCase(),
        quantity: qty,
        average_cost: cost,
        notes: notes.trim() || undefined,
      });
      showToast(`Position in ${symbol.toUpperCase()} added successfully.`, 'success');
      setIsAddModalOpen(false);
      fetchPortfolio();
    } catch (err: any) {
      setFormError(err.message || 'Failed to create holding.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleUpdateHolding = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedHolding) return;

    const qty = parseFloat(quantity);
    const cost = parseFloat(averageCost);
    if (isNaN(qty) || qty <= 0) {
      setFormError('Quantity must be a positive number.');
      return;
    }
    if (isNaN(cost) || cost < 0) {
      setFormError('Average cost must be a non-negative number.');
      return;
    }

    setIsSubmitting(true);
    setFormError(null);
    try {
      await api.portfolio.updateHolding(selectedHolding.id, {
        quantity: qty,
        average_cost: cost,
        notes: notes.trim() || undefined,
      });
      showToast(`Position in ${selectedHolding.symbol} updated.`, 'success');
      setIsEditModalOpen(false);
      fetchPortfolio();
    } catch (err: any) {
      setFormError(err.message || 'Failed to update holding.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDeleteHolding = async () => {
    if (!selectedHolding) return;
    setIsSubmitting(true);
    try {
      await api.portfolio.deleteHolding(selectedHolding.id);
      showToast(`Deleted position in ${selectedHolding.symbol}.`, 'success');
      setIsDeleteModalOpen(false);
      fetchPortfolio();
    } catch (err: any) {
      showToast(err.message || 'Failed to delete holding.', 'error');
    } finally {
      setIsSubmitting(false);
    }
  };

  if (isLoading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-10 w-64" />
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <Skeleton className="h-32 rounded-2xl" />
          <Skeleton className="h-32 rounded-2xl" />
          <Skeleton className="h-32 rounded-2xl" />
          <Skeleton className="h-32 rounded-2xl" />
        </div>
        <Skeleton className="h-96 rounded-2xl" />
      </div>
    );
  }

  if (error || !snapshot) {
    return <ErrorState message={error || 'Failed to load portfolio snapshot'} onRetry={fetchPortfolio} />;
  }

  return (
    <div className="space-y-8 animate-in fade-in duration-300">
      <PageHeader
        title="Portfolio Management"
        subtitle="Real-time portfolio valuation with deterministic cost-basis tracking and asset weighting."
        actions={
          <>
            <Button onClick={fetchPortfolio} size="sm" variant="secondary" leftIcon={<RefreshCw className="w-3.5 h-3.5" />}>
              Refresh Quotes
            </Button>
            <Button onClick={handleOpenAdd} size="sm" variant="glow" leftIcon={<Plus className="w-4 h-4" />}>
              Add Position
            </Button>
          </>
        }
      />

      {/* Summary Metrics */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          label="Total Market Value"
          value={formatCurrency(snapshot.total_market_value)}
          change={snapshot.total_unrealized_gain_loss_percent}
          changeLabel="Gain / Loss"
          icon={PieChart}
          glow="brand"
        />

        <MetricCard
          label="Total Cost Basis"
          value={formatCurrency(snapshot.total_cost_basis)}
          subtext={`${snapshot.holdings_count} position${snapshot.holdings_count === 1 ? '' : 's'}`}
          icon={Layers}
        />

        <MetricCard
          label="Unrealized Gain / Loss"
          value={formatCurrency(snapshot.total_unrealized_gain_loss)}
          change={snapshot.total_unrealized_gain_loss_percent}
          changeLabel="Return"
          glow={snapshot.total_unrealized_gain_loss >= 0 ? 'emerald' : 'none'}
        />

        <MetricCard
          label="Valuation Timestamp"
          value={snapshot.holdings_count > 0 ? 'Live Quotes' : '0 Assets'}
          subtext={`As of ${formatDate(snapshot.as_of)}`}
          glow="cyan"
        />
      </div>

      {/* Holdings Table */}
      <GlassCard className="p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <PieChart className="w-4 h-4 text-brand-400" />
            <h3 className="text-sm font-semibold text-white">Active Positions ({snapshot.holdings_count})</h3>
          </div>
        </div>

        {snapshot.holdings.length === 0 ? (
          <EmptyState
            icon={PieChart}
            title="No Portfolio Holdings"
            description="Add stocks, ETFs, or equities to track real-time valuations, cost basis, and portfolio concentration."
            actionLabel="Add Your First Position"
            onAction={handleOpenAdd}
            actionIcon={<Plus className="w-4 h-4" />}
          />
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Symbol & Company</TableHead>
                <TableHead className="text-right">Shares</TableHead>
                <TableHead className="text-right">Avg Cost</TableHead>
                <TableHead className="text-right">Current Price</TableHead>
                <TableHead className="text-right">Market Value</TableHead>
                <TableHead className="text-right">Unrealized P&L</TableHead>
                <TableHead className="text-right">Weight</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {snapshot.holdings.map((h) => {
                const isGain = (h.unrealized_gain_loss || 0) >= 0;
                return (
                  <TableRow key={h.id || h.symbol}>
                    <TableCell>
                      <div className="font-bold text-white text-sm">{h.symbol}</div>
                      <div className="text-xs text-slate-400 truncate max-w-[180px]">
                        {h.company_name || 'Equity Security'}
                      </div>
                      {h.notes && <div className="text-[10px] text-slate-500 italic mt-0.5">{h.notes}</div>}
                    </TableCell>
                    <TableCell className="text-right font-mono text-sm">{formatNumber(h.quantity, 4)}</TableCell>
                    <TableCell className="text-right font-mono text-sm">{formatCurrency(h.average_cost)}</TableCell>
                    <TableCell className="text-right font-mono text-sm">
                      {h.quote_available !== false ? formatCurrency(h.current_price) : 'Quote Unavailable'}
                    </TableCell>
                    <TableCell className="text-right font-mono font-semibold text-white text-sm">
                      {formatCurrency(h.market_value)}
                    </TableCell>
                    <TableCell className="text-right font-mono text-sm">
                      <div className={isGain ? 'text-emerald-400 font-medium' : 'text-rose-400 font-medium'}>
                        {formatCurrency(h.unrealized_gain_loss)}
                      </div>
                      <div className={isGain ? 'text-[11px] text-emerald-400/80' : 'text-[11px] text-rose-400/80'}>
                        {formatPercent(h.unrealized_gain_loss_percent)}
                      </div>
                    </TableCell>
                    <TableCell className="text-right font-mono text-sm">
                      <span className="px-2 py-0.5 rounded-md bg-surface-100 border border-border-subtle text-xs">
                        {h.weight_percent !== undefined ? `${h.weight_percent.toFixed(1)}%` : '—'}
                      </span>
                    </TableCell>
                    <TableCell className="text-right">
                      <div className="flex items-center justify-end gap-1.5">
                        <button
                          onClick={() => handleOpenEdit(h)}
                          className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-white/5 transition-colors"
                          title="Edit Position"
                        >
                          <Edit2 className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => handleOpenDelete(h)}
                          className="p-1.5 rounded-lg text-slate-400 hover:text-rose-400 hover:bg-rose-500/10 transition-colors"
                          title="Delete Position"
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
        )}
      </GlassCard>

      {/* Add Holding Modal */}
      <Modal isOpen={isAddModalOpen} onClose={() => setIsAddModalOpen(false)} title="Add Portfolio Position">
        <form onSubmit={handleCreateHolding} className="space-y-4">
          {formError && <p className="text-xs text-rose-400">{formError}</p>}
          <Input
            label="Ticker Symbol"
            placeholder="e.g. NVDA, AAPL, MSFT"
            value={symbol}
            onChange={(e) => setSymbol(e.target.value.toUpperCase())}
            disabled={isSubmitting}
            required
          />
          <div className="grid grid-cols-2 gap-3">
            <Input
              label="Shares Quantity"
              type="number"
              step="any"
              min="0.000001"
              placeholder="10.5"
              value={quantity}
              onChange={(e) => setQuantity(e.target.value)}
              disabled={isSubmitting}
              required
            />
            <Input
              label="Average Cost ($)"
              type="number"
              step="any"
              min="0"
              placeholder="120.00"
              value={averageCost}
              onChange={(e) => setAverageCost(e.target.value)}
              disabled={isSubmitting}
              required
            />
          </div>
          <Input
            label="Notes (Optional)"
            placeholder="Investment thesis, target exit..."
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            disabled={isSubmitting}
          />
          <div className="flex justify-end gap-2.5 pt-3 border-t border-border-subtle">
            <Button type="button" variant="secondary" size="sm" onClick={() => setIsAddModalOpen(false)}>
              Cancel
            </Button>
            <Button type="submit" variant="glow" size="sm" isLoading={isSubmitting}>
              Add Position
            </Button>
          </div>
        </form>
      </Modal>

      {/* Edit Holding Modal */}
      <Modal isOpen={isEditModalOpen} onClose={() => setIsEditModalOpen(false)} title={`Edit Position: ${symbol}`}>
        <form onSubmit={handleUpdateHolding} className="space-y-4">
          {formError && <p className="text-xs text-rose-400">{formError}</p>}
          <div className="grid grid-cols-2 gap-3">
            <Input
              label="Shares Quantity"
              type="number"
              step="any"
              value={quantity}
              onChange={(e) => setQuantity(e.target.value)}
              required
            />
            <Input
              label="Average Cost ($)"
              type="number"
              step="any"
              value={averageCost}
              onChange={(e) => setAverageCost(e.target.value)}
              required
            />
          </div>
          <Input
            label="Notes (Optional)"
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

      {/* Delete Confirmation Modal */}
      <Modal isOpen={isDeleteModalOpen} onClose={() => setIsDeleteModalOpen(false)} title="Delete Position">
        <div className="space-y-4">
          <p className="text-xs text-slate-300">
            Are you sure you want to remove <strong className="text-white">{selectedHolding?.symbol}</strong> from your portfolio? This action cannot be undone.
          </p>
          <div className="flex justify-end gap-2.5 pt-3 border-t border-border-subtle">
            <Button variant="secondary" size="sm" onClick={() => setIsDeleteModalOpen(false)}>
              Cancel
            </Button>
            <Button variant="danger" size="sm" isLoading={isSubmitting} onClick={handleDeleteHolding}>
              Delete Position
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
};
