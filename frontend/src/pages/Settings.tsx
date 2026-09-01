import React, { useEffect, useState } from 'react';
import { Save, User, Shield, Sun, Moon, Palette, Check } from 'lucide-react';
import { api } from '../lib/api';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';
import { useTheme } from '../context/ThemeContext';
import { GlassCard } from '../components/ui/GlassCard';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { Select } from '../components/ui/Select';
import { PageHeader } from '../components/ui/PageHeader';
import { Skeleton } from '../components/ui/Skeleton';
import { ErrorState } from '../components/ui/ErrorState';

export const Settings: React.FC = () => {
  const { user, refreshUser } = useAuth();
  const { showToast } = useToast();
  const { theme, setTheme } = useTheme();

  const [displayName, setDisplayName] = useState('');
  const [investmentFocus, setInvestmentFocus] = useState('');
  const [riskPreference, setRiskPreference] = useState('moderate');
  const [investmentHorizon, setInvestmentHorizon] = useState('medium_term');

  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchProfile = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const res = await api.profile.get();
      setDisplayName(res.profile.display_name || '');
      setInvestmentFocus(res.profile.investment_focus || '');
      setRiskPreference(res.profile.risk_preference || 'moderate');
      setInvestmentHorizon(res.profile.investment_horizon || 'medium_term');
    } catch (err: any) {
      setError(err.message || 'Failed to fetch user profile.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchProfile();
  }, []);

  const handleSaveProfile = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSaving(true);
    try {
      await api.profile.update({
        display_name: displayName.trim() || null,
        investment_focus: investmentFocus.trim() || null,
        risk_preference: riskPreference,
        investment_horizon: investmentHorizon,
      });
      await refreshUser();
      showToast('Investor preferences saved successfully.', 'success');
    } catch (err: any) {
      showToast(err.message || 'Failed to save profile.', 'error');
    } finally {
      setIsSaving(false);
    }
  };

  if (isLoading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-10 w-64" />
        <Skeleton className="h-96 rounded-2xl" />
      </div>
    );
  }

  if (error) {
    return <ErrorState message={error} onRetry={fetchProfile} />;
  }

  return (
    <div className="space-y-8 animate-in fade-in duration-300">
      <PageHeader
        title="Investor Profile & Preferences"
        subtitle="Customize investment horizon, risk tolerance, and AI personalization context."
      />

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left 7 Cols: Profile Settings Form */}
        <div className="lg:col-span-7 space-y-6">
          <GlassCard className="p-6">
            <div className="flex items-center gap-2 mb-4 pb-3 border-b border-border-subtle">
              <User className="w-4 h-4 text-brand-600 dark:text-brand-400" />
              <h3 className="text-sm font-semibold text-slate-900 dark:text-white">Investment Parameters</h3>
            </div>

            <form onSubmit={handleSaveProfile} className="space-y-4">
              <Input
                label="Full Name / Display Name"
                value={displayName}
                onChange={(e) => setDisplayName(e.target.value)}
                placeholder="Jane Doe"
                helperText="Personalizes greeting headers and research export signatures."
              />

              <Input
                label="Investment Focus / Strategy"
                value={investmentFocus}
                onChange={(e) => setInvestmentFocus(e.target.value)}
                placeholder="e.g. AI hardware, SaaS growth, clean energy, dividend value"
                helperText="Grounds AI multi-agent prompts in your key sector focus."
              />

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <Select
                  label="Risk Tolerance"
                  value={riskPreference}
                  onChange={(e) => setRiskPreference(e.target.value)}
                  options={[
                    { value: 'conservative', label: 'Conservative (Capital Preservation)' },
                    { value: 'moderate', label: 'Moderate (Balanced Growth & Risk)' },
                    { value: 'aggressive', label: 'Aggressive (High Alpha / Volatility)' },
                  ]}
                />

                <Select
                  label="Investment Horizon"
                  value={investmentHorizon}
                  onChange={(e) => setInvestmentHorizon(e.target.value)}
                  options={[
                    { value: 'short_term', label: 'Short Term (< 1 year)' },
                    { value: 'medium_term', label: 'Medium Term (1 - 3 years)' },
                    { value: 'long_term', label: 'Long Term (3+ years)' },
                  ]}
                />
              </div>

              <div className="pt-3">
                <Button
                  type="submit"
                  variant="glow"
                  isLoading={isSaving}
                  leftIcon={<Save className="w-4 h-4" />}
                >
                  Save Profile Settings
                </Button>
              </div>
            </form>
          </GlassCard>

          {/* Theme & Appearance Card */}
          <GlassCard className="p-6">
            <div className="flex items-center gap-2 mb-4 pb-3 border-b border-border-subtle">
              <Palette className="w-4 h-4 text-brand-600 dark:text-brand-400" />
              <h3 className="text-sm font-semibold text-slate-900 dark:text-white">Interface Appearance</h3>
            </div>

            <p className="text-xs text-slate-600 dark:text-slate-400 mb-4">
              Select your preferred visual mode for AIRA. Light mode is optimized for daytime research readability, while dark mode provides an immersive, high-contrast terminal feel.
            </p>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {/* Light Mode Selection */}
              <button
                type="button"
                onClick={() => setTheme('light')}
                className={`flex items-start gap-3 p-4 rounded-xl border text-left transition-all ${
                  theme === 'light'
                    ? 'border-brand-500 bg-brand-500/10 shadow-sm'
                    : 'border-border-subtle bg-surface-50 dark:bg-surface-200/50 hover:border-border-strong'
                }`}
              >
                <div className="w-9 h-9 rounded-lg bg-amber-500/15 text-amber-600 flex items-center justify-center shrink-0">
                  <Sun className="w-5 h-5" />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-slate-900 dark:text-white">Light Mode</span>
                    {theme === 'light' && <Check className="w-4 h-4 text-brand-600" />}
                  </div>
                  <span className="text-[11px] text-slate-500 dark:text-slate-400 mt-0.5 block">
                    Warm slate surfaces with crisp typography and subtle glass depth.
                  </span>
                </div>
              </button>

              {/* Dark Mode Selection */}
              <button
                type="button"
                onClick={() => setTheme('dark')}
                className={`flex items-start gap-3 p-4 rounded-xl border text-left transition-all ${
                  theme === 'dark'
                    ? 'border-brand-500 bg-brand-500/10 shadow-glow-brand'
                    : 'border-border-subtle bg-surface-50 dark:bg-surface-200/50 hover:border-border-strong'
                }`}
              >
                <div className="w-9 h-9 rounded-lg bg-indigo-500/15 text-indigo-400 flex items-center justify-center shrink-0">
                  <Moon className="w-5 h-5" />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-slate-900 dark:text-white">Dark Mode</span>
                    {theme === 'dark' && <Check className="w-4 h-4 text-brand-400" />}
                  </div>
                  <span className="text-[11px] text-slate-500 dark:text-slate-400 mt-0.5 block">
                    Cinematic midnight surfaces with vibrant luminous highlights.
                  </span>
                </div>
              </button>
            </div>
          </GlassCard>
        </div>

        {/* Right 5 Cols: Account Info */}
        <div className="lg:col-span-5 space-y-6">
          <GlassCard className="p-6">
            <div className="flex items-center gap-2 mb-4 pb-3 border-b border-border-subtle">
              <Shield className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
              <h3 className="text-sm font-semibold text-slate-900 dark:text-white">Account Security & Tenancy</h3>
            </div>

            <div className="space-y-3 text-xs">
              <div className="flex justify-between py-1.5 border-b border-border-subtle/50">
                <span className="text-slate-500 dark:text-slate-400">Authenticated Email:</span>
                <span className="text-slate-900 dark:text-white font-mono">{user?.email}</span>
              </div>
              <div className="flex justify-between py-1.5 border-b border-border-subtle/50">
                <span className="text-slate-500 dark:text-slate-400">Account ID:</span>
                <span className="text-slate-700 dark:text-slate-300 font-mono">USER-{user?.id}</span>
              </div>
              <div className="flex justify-between py-1.5 border-b border-border-subtle/50">
                <span className="text-slate-500 dark:text-slate-400">Tenant Isolation:</span>
                <span className="text-emerald-700 dark:text-emerald-400 font-mono font-medium">Strict (Server Scoped)</span>
              </div>
              <div className="flex justify-between py-1.5">
                <span className="text-slate-500 dark:text-slate-400">Alert Engine:</span>
                <span className="text-brand-700 dark:text-brand-300 font-mono font-medium">
                  {user?.alerts_enabled ? 'Active' : 'Disabled'}
                </span>
              </div>
            </div>
          </GlassCard>
        </div>
      </div>
    </div>
  );
};
