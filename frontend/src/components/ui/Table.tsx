import React from 'react';
import { cn } from '../../lib/utils';

export interface TableProps extends React.TableHTMLAttributes<HTMLTableElement> {
  wrapperClassName?: string;
}

export const Table: React.FC<TableProps> = ({ children, className, wrapperClassName, ...props }) => {
  return (
    <div className={cn('w-full overflow-x-auto rounded-xl border border-border-subtle bg-surface-200/50', wrapperClassName)}>
      <table className={cn('w-full text-left text-sm text-slate-300 border-collapse', className)} {...props}>
        {children}
      </table>
    </div>
  );
};

export const TableHeader: React.FC<React.HTMLAttributes<HTMLTableSectionElement>> = ({ children, className, ...props }) => {
  return (
    <thead className={cn('border-b border-border-subtle bg-surface-300/80 text-xs uppercase font-semibold text-slate-400', className)} {...props}>
      {children}
    </thead>
  );
};

export const TableBody: React.FC<React.HTMLAttributes<HTMLTableSectionElement>> = ({ children, className, ...props }) => {
  return (
    <tbody className={cn('divide-y divide-border-subtle/50', className)} {...props}>
      {children}
    </tbody>
  );
};

export const TableRow: React.FC<React.HTMLAttributes<HTMLTableRowElement>> = ({ children, className, ...props }) => {
  return (
    <tr className={cn('hover:bg-white/[0.02] transition-colors', className)} {...props}>
      {children}
    </tr>
  );
};

export const TableHead: React.FC<React.ThHTMLAttributes<HTMLTableCellElement>> = ({ children, className, ...props }) => {
  return (
    <th className={cn('px-4 py-3.5 font-semibold text-slate-400 tracking-wider text-xs', className)} {...props}>
      {children}
    </th>
  );
};

export const TableCell: React.FC<React.TdHTMLAttributes<HTMLTableCellElement>> = ({ children, className, ...props }) => {
  return (
    <td className={cn('px-4 py-3.5 align-middle', className)} {...props}>
      {children}
    </td>
  );
};
