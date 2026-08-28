import React from 'react';
import { cn } from '../../lib/utils';

export interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  hoverEffect?: boolean;
}

export const Card: React.FC<CardProps> = ({ children, className, hoverEffect = false, ...props }) => {
  return (
    <div
      className={cn(
        'bg-surface-200/90 border border-border-subtle rounded-2xl p-6 shadow-sm',
        hoverEffect && 'transition-all duration-200 hover:border-border-strong hover:bg-surface-100/90 hover:shadow-md',
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
};
