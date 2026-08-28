import React from 'react';
import { Link } from 'react-router-dom';
import { Compass, Home } from 'lucide-react';
import { Button } from '../components/ui/Button';
import { GlassCard } from '../components/ui/GlassCard';

export const NotFound: React.FC = () => {
  return (
    <div className="min-h-screen flex items-center justify-center p-4 bg-background">
      <GlassCard className="max-w-md w-full p-8 text-center">
        <div className="w-14 h-14 rounded-2xl bg-brand-500/10 border border-brand-500/20 flex items-center justify-center text-brand-400 mx-auto mb-4">
          <Compass className="w-7 h-7" />
        </div>
        <h1 className="text-3xl font-bold text-white mb-2">404</h1>
        <h3 className="text-base font-semibold text-slate-200 mb-2">Resource Not Found</h3>
        <p className="text-xs text-slate-400 mb-6 leading-relaxed">
          The requested route does not exist or has been relocated within the intelligence platform.
        </p>
        <Link to="/app/dashboard" className="block">
          <Button variant="glow" className="w-full" leftIcon={<Home className="w-4 h-4" />}>
            Return to Dashboard
          </Button>
        </Link>
      </GlassCard>
    </div>
  );
};
