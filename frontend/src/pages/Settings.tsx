import React, { useEffect, useState } from 'react';
import { Save, User, Shield } from 'lucide-react';
import { api } from '../lib/api';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';
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
        <div className="lg:col-span-7">
          <GlassCard className="p-6">
            <div className="flex items-center gap-2 mb-4 pb-3 border-b border-border-subtle">
              <User className="w-4 h-4 text-brand-400" />
              <h3 className="text-sm font-semibold text-white">Investment Parameters</h3>
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
        </div>

        {/* Right 5 Cols: Account Info */}
        <div className="lg:col-span-5 space-y-6">
          <GlassCard className="p-6">
            <div className="flex items-center gap-2 mb-4 pb-3 border-b border-border-subtle">
              <Shield className="w-4 h-4 text-emerald-400" />
              <h3 className="text-sm font-semibold text-white">Account Security & Tenancy</h3>
            </div>

            <div className="space-y-3 text-xs">
              <div className="flex justify-between py-1.5 border-b border-border-subtle/50">
                <span className="text-slate-400">Authenticated Email:</span>
                <span className="text-white font-mono">{user?.email}</span>
              </div>
              <div className="flex justify-between py-1.5 border-b border-border-subtle/50">
                <span className="text-slate-400">Account ID:</span>
                <span className="text-slate-300 font-mono">USER-{user?.id}</span>
              </div>
              <div className="flex justify-between py-1.5 border-b border-border-subtle/50">
                <span className="text-slate-400">Tenant Isolation:</span>
                <span className="text-emerald-400 font-mono font-medium">Strict (Server Scoped)</span>
              </div>
              <div className="flex justify-between py-1.5">
                <span className="text-slate-400">Alert Engine:</span>
                <span className="text-brand-300 font-mono font-medium">
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
