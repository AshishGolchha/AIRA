import React from 'react';
import { TrendingDown, TrendingUp, LucideIcon } from 'lucide-react';
import { GlassCard } from './GlassCard';
import { cn, formatPercent } from '../../lib/utils';

export interface MetricCardProps {
  label: string;
  value: string;
  change?: number | null;
  changeLabel?: string;
  icon?: LucideIcon;
  subtext?: string;
  glow?: 'none' | 'brand' | 'emerald' | 'cyan';
  className?: string;
}

export const MetricCard: React.FC<MetricCardProps> = ({
  label,
  value,
  change,
  changeLabel,
  icon: Icon,
  subtext,
  glow = 'none',
  className,
}) => {
  const isPositive = change !== undefined && change !== null && change > 0;
  const isNegative = change !== undefined && change !== null && change < 0;

  return (
    <GlassCard glow={glow} className={cn('flex flex-col justify-between p-5 relative overflow-hidden', className)}>
      <div className="flex items-center justify-between gap-2 mb-2">
        <span className="text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">{label}</span>
        {Icon && (
          <div className="p-2 rounded-xl bg-slate-900/[0.04] dark:bg-white/[0.04] text-slate-600 dark:text-slate-400 border border-border-subtle">
            <Icon className="w-4 h-4" />
          </div>
        )}
      </div>

      <div className="space-y-1">
        <div className="text-2xl font-bold tracking-tight text-slate-900 dark:text-white">{value}</div>

        {(change !== undefined && change !== null) || subtext ? (
          <div className="flex items-center gap-2 text-xs">
            {change !== undefined && change !== null && (
              <span
                className={cn(
                  'inline-flex items-center gap-0.5 font-medium px-1.5 py-0.5 rounded-md',
                  isPositive && 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400',
                  isNegative && 'bg-rose-500/10 text-rose-600 dark:text-rose-400',
                  !isPositive && !isNegative && 'bg-slate-500/10 text-slate-600 dark:text-slate-400'
                )}
              >
                {isPositive && <TrendingUp className="w-3 h-3" />}
                {isNegative && <TrendingDown className="w-3 h-3" />}
                {formatPercent(change)}
              </span>
            )}
            {changeLabel && <span className="text-slate-500 dark:text-slate-400">{changeLabel}</span>}
            {subtext && !changeLabel && <span className="text-slate-500 dark:text-slate-400">{subtext}</span>}
          </div>
        ) : null}
      </div>
    </GlassCard>
  );
};
