import React from 'react';
import { Loader2 } from 'lucide-react';

export interface LoadingStateProps {
  message?: string;
  subMessage?: string;
}

export const LoadingState: React.FC<LoadingStateProps> = ({
  message = 'Loading data...',
  subMessage,
}) => {
  return (
    <div className="flex flex-col items-center justify-center p-12 text-center rounded-2xl border border-border-subtle bg-surface-200/50">
      <Loader2 className="w-8 h-8 animate-spin text-brand-500 mb-4" />
      <h4 className="text-sm font-medium text-slate-800 dark:text-slate-200">{message}</h4>
      {subMessage && <p className="text-xs text-slate-500 mt-1">{subMessage}</p>}
    </div>
  );
};
