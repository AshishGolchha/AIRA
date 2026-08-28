import React from 'react';
import { NavLink } from 'react-router-dom';
import { X, LogOut } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { navigationItems } from './Sidebar';
import { cn } from '../../lib/utils';

export interface MobileNavProps {
  isOpen: boolean;
  onClose: () => void;
}

export const MobileNav: React.FC<MobileNavProps> = ({ isOpen, onClose }) => {
  const { user, logout } = useAuth();

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 lg:hidden">
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black/80 backdrop-blur-sm transition-opacity"
        onClick={onClose}
      />

      {/* Drawer */}
      <div className="fixed inset-y-0 left-0 w-72 bg-surface-300 border-r border-border-strong p-5 flex flex-col justify-between z-10 shadow-2xl animate-in slide-in-from-left duration-200">
        <div>
          {/* Header */}
          <div className="flex items-center justify-between pb-4 border-b border-border-subtle">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-brand-600 via-indigo-500 to-cyan-400 flex items-center justify-center text-white font-bold text-sm shadow-glow-brand">
                A
              </div>
              <div className="flex flex-col">
                <span className="font-bold tracking-tight text-white text-base">AIRA</span>
                <span className="text-[9px] text-slate-400 -mt-1 font-mono">INVESTMENT AI</span>
              </div>
            </div>
            <button
              onClick={onClose}
              className="text-slate-400 hover:text-white p-1.5 rounded-lg hover:bg-white/5"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Navigation Links */}
          <nav className="py-4 space-y-1">
            {navigationItems.map((item) => {
              const Icon = item.icon;
              return (
                <NavLink
                  key={item.path}
                  to={item.path}
                  onClick={onClose}
                  className={({ isActive }) =>
                    cn(
                      'flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-sm font-medium transition-all duration-150',
                      isActive
                        ? 'bg-brand-600/90 text-white shadow-md border border-brand-500/30 font-semibold'
                        : 'text-slate-400 hover:text-slate-100 hover:bg-white/[0.04]'
                    )
                  }
                >
                  <Icon className="w-5 h-5 shrink-0" />
                  <span>{item.label}</span>
                  {item.badge && (
                    <span className="ml-auto text-[10px] uppercase font-bold px-1.5 py-0.5 rounded-md bg-brand-500/20 text-brand-300 border border-brand-500/30 font-mono">
                      {item.badge}
                    </span>
                  )}
                </NavLink>
              );
            })}
          </nav>
        </div>

        {/* User Info & Logout */}
        <div className="pt-4 border-t border-border-subtle">
          <div className="flex items-center justify-between p-2 rounded-xl bg-surface-200/50 border border-border-subtle mb-2">
            <div className="flex items-center gap-2.5 min-w-0">
              <div className="w-8 h-8 rounded-lg bg-surface-100 border border-border-strong flex items-center justify-center text-slate-300 font-semibold shrink-0 text-xs">
                {user?.profile?.display_name ? user.profile.display_name.charAt(0).toUpperCase() : user?.email?.charAt(0).toUpperCase() || 'U'}
              </div>
              <div className="min-w-0">
                <div className="text-xs font-semibold text-white truncate">
                  {user?.profile?.display_name || user?.email?.split('@')[0]}
                </div>
                <div className="text-[10px] text-slate-400 font-mono truncate">{user?.email}</div>
              </div>
            </div>
            <button
              onClick={() => {
                onClose();
                logout();
              }}
              className="text-slate-400 hover:text-rose-400 p-1.5 rounded-lg hover:bg-rose-500/10"
              title="Sign Out"
            >
              <LogOut className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
