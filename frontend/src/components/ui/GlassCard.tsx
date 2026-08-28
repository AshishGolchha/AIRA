import React from 'react';
import { cn } from '../../lib/utils';

export interface GlassCardProps extends React.HTMLAttributes<HTMLDivElement> {
  glow?: 'none' | 'brand' | 'emerald' | 'cyan';
  interactive?: boolean;
}

export const GlassCard: React.FC<GlassCardProps> = ({
  children,
  className,
  glow = 'none',
  interactive = false,
  ...props
}) => {
  const glowStyles = {
    none: '',
    brand: 'border-brand-500/20 shadow-glow-brand',
    emerald: 'border-emerald-500/20 shadow-glow-emerald',
    cyan: 'border-cyan-500/20 shadow-[0_0_25px_-5px_rgba(6,182,212,0.3)]',
  };

  return (
    <div
      className={cn(
        interactive ? 'glass-panel-interactive' : 'glass-panel',
        'rounded-2xl p-6 shadow-glass',
        glowStyles[glow],
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
};
