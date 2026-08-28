import React from 'react';
import { cn } from '../../lib/utils';

export interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: 'brand' | 'emerald' | 'amber' | 'rose' | 'cyan' | 'slate' | 'outline';
  size?: 'sm' | 'md';
}

export const Badge: React.FC<BadgeProps> = ({
  children,
  className,
  variant = 'brand',
  size = 'md',
  ...props
}) => {
  const variantStyles = {
    brand: 'bg-brand-500/10 text-brand-300 border border-brand-500/20',
    emerald: 'bg-emerald-500/10 text-emerald-300 border border-emerald-500/20',
    amber: 'bg-amber-500/10 text-amber-300 border border-amber-500/20',
    rose: 'bg-rose-500/10 text-rose-300 border border-rose-500/20',
    cyan: 'bg-cyan-500/10 text-cyan-300 border border-cyan-500/20',
    slate: 'bg-slate-500/10 text-slate-300 border border-slate-500/20',
    outline: 'bg-transparent text-slate-300 border border-border-strong',
  };

  const sizeStyles = {
    sm: 'text-xs px-2 py-0.5 rounded-md font-medium',
    md: 'text-xs px-2.5 py-1 rounded-lg font-medium',
  };

  return (
    <span
      className={cn('inline-flex items-center gap-1.5 leading-none select-none', variantStyles[variant], sizeStyles[size], className)}
      {...props}
    >
      {children}
    </span>
  );
};
