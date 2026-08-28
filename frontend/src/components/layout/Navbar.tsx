import React, { useState } from 'react';
import { Menu, LogOut, Sparkles, Activity } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { Button } from '../ui/Button';
import { Link } from 'react-router-dom';

export interface NavbarProps {
  onOpenMobileNav: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({ onOpenMobileNav }) => {
  const { user, logout } = useAuth();
  const [showUserDropdown, setShowUserDropdown] = useState(false);

  return (
    <header className="h-16 border-b border-border-subtle bg-surface-300/60 backdrop-blur-xl sticky top-0 z-20 px-4 sm:px-6 flex items-center justify-between">
      {/* Mobile Toggle & Left Title */}
      <div className="flex items-center gap-3">
        <button
          onClick={onOpenMobileNav}
          className="lg:hidden text-slate-400 hover:text-white p-2 rounded-xl bg-surface-200/50 border border-border-subtle transition-colors"
        >
          <Menu className="w-5 h-5" />
        </button>
        <div className="hidden sm:flex items-center gap-2">
          <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-mono">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
            <span>AI Core Active</span>
          </div>
        </div>
      </div>

      {/* Right Actions */}
      <div className="flex items-center gap-3">
        <Link to="/app/intelligence">
          <Button size="sm" variant="glow" leftIcon={<Sparkles className="w-3.5 h-3.5" />}>
            Run AI Analysis
          </Button>
        </Link>

        {/* User Dropdown */}
        <div className="relative">
          <button
            onClick={() => setShowUserDropdown(!showUserDropdown)}
            className="flex items-center gap-2 p-1.5 rounded-xl hover:bg-white/5 border border-border-subtle bg-surface-200/50 transition-colors"
          >
            <div className="w-7 h-7 rounded-lg bg-brand-600/30 border border-brand-500/30 flex items-center justify-center text-brand-300 font-semibold text-xs">
              {user?.profile?.display_name ? user.profile.display_name.charAt(0).toUpperCase() : user?.email?.charAt(0).toUpperCase() || 'U'}
            </div>
            <span className="hidden md:block text-xs font-medium text-slate-200 pr-1">
              {user?.profile?.display_name || user?.email?.split('@')[0]}
            </span>
          </button>

          {showUserDropdown && (
            <>
              <div
                className="fixed inset-0 z-40"
                onClick={() => setShowUserDropdown(false)}
              />
              <div className="absolute right-0 mt-2 w-56 bg-surface-200 border border-border-strong rounded-2xl shadow-2xl p-2 z-50 animate-in fade-in zoom-in-95 duration-150">
                <div className="px-3 py-2 border-b border-border-subtle">
                  <div className="text-xs font-semibold text-white truncate">
                    {user?.profile?.display_name || 'Investor'}
                  </div>
                  <div className="text-[10px] text-slate-400 font-mono truncate">{user?.email}</div>
                </div>
                <div className="py-1">
                  <Link
                    to="/app/settings"
                    onClick={() => setShowUserDropdown(false)}
                    className="flex items-center gap-2 px-3 py-2 rounded-xl text-xs text-slate-300 hover:text-white hover:bg-white/5 transition-colors"
                  >
                    <Activity className="w-4 h-4 text-slate-400" />
                    Account Settings
                  </Link>
                  <button
                    onClick={() => {
                      setShowUserDropdown(false);
                      logout();
                    }}
                    className="w-full flex items-center gap-2 px-3 py-2 rounded-xl text-xs text-rose-400 hover:text-rose-300 hover:bg-rose-500/10 transition-colors"
                  >
                    <LogOut className="w-4 h-4" />
                    Sign Out
                  </button>
                </div>
              </div>
            </>
          )}
        </div>
      </div>
    </header>
  );
};
