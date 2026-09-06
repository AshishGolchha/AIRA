import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  PieChart,
  Bookmark,
  BellRing,
  Sparkles,
  Search,
  Radio,
  Settings,
  ChevronLeft,
  ChevronRight,
  LogOut,
  ShieldCheck,
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { AiraLogo } from '../ui/AiraLogo';
import { cn } from '../../lib/utils';

export interface SidebarProps {
  isCollapsed: boolean;
  onToggleCollapse: () => void;
}

export const navigationItems = [
  { label: 'Dashboard', path: '/app/dashboard', icon: LayoutDashboard },
  { label: 'Portfolio', path: '/app/portfolio', icon: PieChart },
  { label: 'Watchlist', path: '/app/watchlist', icon: Bookmark },
  { label: 'Alerts', path: '/app/alerts', icon: BellRing },
  { label: 'Intelligence', path: '/app/intelligence', icon: Sparkles, badge: 'AI' },
  { label: 'Research', path: '/app/research', icon: Search },
  { label: 'Notifications', path: '/app/notifications', icon: Radio },
  { label: 'Settings', path: '/app/settings', icon: Settings },
];

export const Sidebar: React.FC<SidebarProps> = ({ isCollapsed, onToggleCollapse }) => {
  const { user, logout } = useAuth();

  return (
    <aside
      className={cn(
        'hidden lg:flex flex-col justify-between border-r border-border-subtle bg-surface-300/90 backdrop-blur-xl h-screen sticky top-0 transition-all duration-300 z-30 shrink-0 select-none',
        isCollapsed ? 'w-20' : 'w-64'
      )}
    >
      {/* Top Brand Header */}
      <div>
        <div
          className={cn(
            'h-16 border-b border-border-subtle transition-all duration-300 flex items-center relative',
            isCollapsed ? 'justify-center px-2' : 'justify-between px-4'
          )}
        >
          {isCollapsed ? (
            <>
              <button
                onClick={onToggleCollapse}
                className="flex items-center justify-center focus:outline-none focus-visible:ring-2 focus-visible:ring-brand-500 rounded-xl transition-opacity hover:opacity-80 active:opacity-60"
                title="AIRA — Autonomous Investment Research & Analysis (Click to expand)"
                aria-label="Expand sidebar"
              >
                <img
                  src="/logo.png"
                  alt="AIRA"
                  draggable={false}
                  className="object-contain select-none"
                  style={{ height: 36, width: 'auto', maxWidth: 68 }}
                />
              </button>
              <button
                onClick={onToggleCollapse}
                className="absolute -right-3 top-5 w-6 h-6 rounded-full bg-surface-50 dark:bg-surface-200 border border-border-strong text-slate-500 hover:text-slate-900 dark:text-slate-400 dark:hover:text-white shadow-md flex items-center justify-center hover:scale-110 transition-all z-40"
                title="Expand Sidebar"
                aria-label="Expand sidebar"
              >
                <ChevronRight className="w-3.5 h-3.5" />
              </button>
            </>
          ) : (
            <>
              <div
                className="flex items-center min-w-0"
                title="AIRA — Autonomous Investment Research & Analysis"
              >
                <AiraLogo variant="full" size="sm" subtitle="INVESTMENT AI" />
              </div>
              <button
                onClick={onToggleCollapse}
                className="text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white p-1.5 rounded-lg hover:bg-slate-900/5 dark:hover:bg-white/5 transition-colors shrink-0"
                title="Collapse Sidebar"
                aria-label="Collapse sidebar"
              >
                <ChevronLeft className="w-4 h-4" />
              </button>
            </>
          )}
        </div>

        {!isCollapsed && (
          <div className="px-4 py-1.5 border-b border-border-subtle/60 bg-surface-100/40 dark:bg-surface-200/30">
            <span
              className="text-[9px] font-semibold text-brand-700 dark:text-brand-300 tracking-wide uppercase block truncate"
              title="Autonomous Investment Research & Analysis"
            >
              Autonomous Investment Research &amp; Analysis
            </span>
          </div>
        )}

        {/* Navigation Links */}
        <nav className={cn('p-3 space-y-1.5', isCollapsed && 'px-2')}>
          {navigationItems.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.path}
                to={item.path}
                className={({ isActive }) =>
                  cn(
                    'flex items-center rounded-xl text-sm font-medium transition-all duration-200 group relative',
                    isCollapsed
                      ? 'justify-center w-11 h-11 mx-auto'
                      : 'gap-3 px-3.5 py-2.5',
                    isActive
                      ? 'bg-brand-600 text-white shadow-md shadow-brand-600/10 border border-brand-500/30'
                      : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-100 hover:bg-slate-900/[0.04] dark:hover:bg-white/[0.04]'
                  )
                }
              >
                <Icon className="w-5 h-5 shrink-0 transition-transform duration-200 group-hover:scale-105" />
                {!isCollapsed && <span className="truncate">{item.label}</span>}
                {!isCollapsed && item.badge && (
                  <span className="ml-auto text-[10px] uppercase font-bold px-1.5 py-0.5 rounded-md bg-brand-500/20 text-brand-700 dark:text-brand-300 border border-brand-500/30 font-mono">
                    {item.badge}
                  </span>
                )}
                {isCollapsed && (
                  <div className="absolute left-full ml-3 px-2.5 py-1 bg-surface-50 dark:bg-surface-100 text-slate-900 dark:text-white text-xs font-semibold rounded-lg shadow-xl border border-border-strong whitespace-nowrap opacity-0 pointer-events-none group-hover:opacity-100 transition-opacity duration-150 z-50">
                    {item.label}
                  </div>
                )}
              </NavLink>
            );
          })}
        </nav>
      </div>

      {/* User Info & Logout */}
      <div className={cn('p-3 border-t border-border-subtle', isCollapsed && 'px-2')}>
        {isCollapsed ? (
          <div className="flex flex-col items-center justify-center gap-2 p-1.5 rounded-xl bg-surface-100/70 dark:bg-surface-200/50 border border-border-subtle mx-auto w-11">
            <div
              className="w-8 h-8 rounded-lg bg-surface-50 dark:bg-surface-100 border border-border-strong flex items-center justify-center text-slate-700 dark:text-slate-300 font-semibold shrink-0 text-xs relative group cursor-default"
              title={user?.profile?.display_name || user?.email || 'User'}
            >
              {user?.profile?.display_name ? user.profile.display_name.charAt(0).toUpperCase() : user?.email?.charAt(0).toUpperCase() || 'U'}
              <div className="absolute left-full ml-3 px-2.5 py-1 bg-surface-50 dark:bg-surface-100 text-slate-900 dark:text-white text-xs font-semibold rounded-lg shadow-xl border border-border-strong whitespace-nowrap opacity-0 pointer-events-none group-hover:opacity-100 transition-opacity duration-150 z-50">
                {user?.profile?.display_name || user?.email || 'Investor'}
              </div>
            </div>
            <button
              onClick={logout}
              title="Sign Out"
              aria-label="Sign out"
              className="text-slate-400 hover:text-rose-600 dark:hover:text-rose-400 p-1.5 rounded-lg hover:bg-rose-500/10 transition-colors relative group"
            >
              <LogOut className="w-4 h-4" />
              <div className="absolute left-full ml-3 px-2.5 py-1 bg-surface-50 dark:bg-surface-100 text-rose-600 dark:text-rose-400 text-xs font-semibold rounded-lg shadow-xl border border-border-strong whitespace-nowrap opacity-0 pointer-events-none group-hover:opacity-100 transition-opacity duration-150 z-50">
                Sign Out
              </div>
            </button>
          </div>
        ) : (
          <div className="flex items-center gap-3 p-2 rounded-xl bg-surface-100 dark:bg-surface-200/50 border border-border-subtle">
            <div className="w-8 h-8 rounded-lg bg-surface-50 dark:bg-surface-100 border border-border-strong flex items-center justify-center text-slate-700 dark:text-slate-300 font-semibold shrink-0 text-xs">
              {user?.profile?.display_name ? user.profile.display_name.charAt(0).toUpperCase() : user?.email?.charAt(0).toUpperCase() || 'U'}
            </div>
            <div className="flex-1 min-w-0">
              <div className="text-xs font-semibold text-slate-900 dark:text-white truncate">
                {user?.profile?.display_name || user?.email?.split('@')[0] || 'Investor'}
              </div>
              <div className="text-[10px] text-slate-500 dark:text-slate-400 truncate flex items-center gap-1 font-mono">
                <ShieldCheck className="w-3 h-3 text-emerald-600 dark:text-emerald-400 shrink-0" />
                {user?.email}
              </div>
            </div>
            <button
              onClick={logout}
              title="Sign Out"
              aria-label="Sign out"
              className="text-slate-500 dark:text-slate-400 hover:text-rose-600 dark:hover:text-rose-400 p-1.5 rounded-lg hover:bg-rose-500/10 transition-colors shrink-0"
            >
              <LogOut className="w-4 h-4" />
            </button>
          </div>
        )}
      </div>
    </aside>
  );
};
