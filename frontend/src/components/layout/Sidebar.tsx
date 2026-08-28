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
        <div className="flex items-center justify-between px-5 h-16 border-b border-border-subtle">
          <div className="flex items-center gap-3 overflow-hidden">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-brand-600 via-indigo-500 to-cyan-400 flex items-center justify-center text-white font-bold tracking-wider shadow-glow-brand shrink-0">
              A
            </div>
            {!isCollapsed && (
              <div className="flex flex-col">
                <span className="font-bold tracking-tight text-white text-base">AIRA</span>
                <span className="text-[10px] text-slate-400 -mt-1 font-mono tracking-wider">INVESTMENT AI</span>
              </div>
            )}
          </div>
          <button
            onClick={onToggleCollapse}
            className="text-slate-400 hover:text-white p-1.5 rounded-lg hover:bg-white/5 transition-colors"
            title={isCollapsed ? 'Expand Sidebar' : 'Collapse Sidebar'}
          >
            {isCollapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
          </button>
        </div>

        {/* Navigation Links */}
        <nav className="p-3 space-y-1.5">
          {navigationItems.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.path}
                to={item.path}
                className={({ isActive }) =>
                  cn(
                    'flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-sm font-medium transition-all duration-200 group relative',
                    isActive
                      ? 'bg-brand-600/90 text-white shadow-md shadow-brand-600/10 border border-brand-500/30'
                      : 'text-slate-400 hover:text-slate-100 hover:bg-white/[0.04]'
                  )
                }
              >
                <Icon className="w-5 h-5 shrink-0 transition-transform duration-200 group-hover:scale-105" />
                {!isCollapsed && <span className="truncate">{item.label}</span>}
                {!isCollapsed && item.badge && (
                  <span className="ml-auto text-[10px] uppercase font-bold px-1.5 py-0.5 rounded-md bg-brand-500/20 text-brand-300 border border-brand-500/30 font-mono">
                    {item.badge}
                  </span>
                )}
                {isCollapsed && (
                  <div className="absolute left-full ml-3 px-2 py-1 bg-surface-100 text-white text-xs rounded-md shadow-lg border border-border-strong whitespace-nowrap opacity-0 pointer-events-none group-hover:opacity-100 transition-opacity z-50">
                    {item.label}
                  </div>
                )}
              </NavLink>
            );
          })}
        </nav>
      </div>

      {/* User Info & Logout */}
      <div className="p-3 border-t border-border-subtle">
        <div className={cn('flex items-center gap-3 p-2 rounded-xl bg-surface-200/50 border border-border-subtle', isCollapsed && 'justify-center p-1.5')}>
          <div className="w-8 h-8 rounded-lg bg-surface-100 border border-border-strong flex items-center justify-center text-slate-300 font-semibold shrink-0 text-xs">
            {user?.profile?.display_name ? user.profile.display_name.charAt(0).toUpperCase() : user?.email?.charAt(0).toUpperCase() || 'U'}
          </div>
          {!isCollapsed && (
            <div className="flex-1 min-w-0">
              <div className="text-xs font-semibold text-white truncate">
                {user?.profile?.display_name || user?.email?.split('@')[0] || 'Investor'}
              </div>
              <div className="text-[10px] text-slate-400 truncate flex items-center gap-1 font-mono">
                <ShieldCheck className="w-3 h-3 text-emerald-400 shrink-0" />
                {user?.email}
              </div>
            </div>
          )}
          {!isCollapsed && (
            <button
              onClick={logout}
              title="Sign Out"
              className="text-slate-400 hover:text-rose-400 p-1.5 rounded-lg hover:bg-rose-500/10 transition-colors"
            >
              <LogOut className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>
    </aside>
  );
};
