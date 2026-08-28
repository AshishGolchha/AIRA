import React from 'react';
import { Badge, BadgeProps } from './Badge';

export interface StatusBadgeProps {
  status: string;
  className?: string;
  size?: BadgeProps['size'];
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status, className, size = 'sm' }) => {
  const normalized = status.toLowerCase();

  let variant: BadgeProps['variant'] = 'slate';
  let label = status;

  if (normalized === 'critical' || normalized === 'failed' || normalized === 'danger') {
    variant = 'rose';
    label = status.charAt(0).toUpperCase() + status.slice(1);
  } else if (normalized === 'warning' || normalized === 'pending' || normalized === 'high') {
    variant = 'amber';
    label = status.charAt(0).toUpperCase() + status.slice(1);
  } else if (normalized === 'info' || normalized === 'normal' || normalized === 'running') {
    variant = 'cyan';
    label = status.charAt(0).toUpperCase() + status.slice(1);
  } else if (normalized === 'delivered' || normalized === 'success' || normalized === 'completed' || normalized === 'active') {
    variant = 'emerald';
    label = status.charAt(0).toUpperCase() + status.slice(1);
  } else if (normalized === 'low') {
    variant = 'slate';
    label = 'Low';
  }

  return (
    <Badge variant={variant} size={size} className={className}>
      <span className={`w-1.5 h-1.5 rounded-full ${
        variant === 'rose' ? 'bg-rose-400' :
        variant === 'amber' ? 'bg-amber-400' :
        variant === 'cyan' ? 'bg-cyan-400' :
        variant === 'emerald' ? 'bg-emerald-400' : 'bg-slate-400'
      }`} />
      {label}
    </Badge>
  );
};
