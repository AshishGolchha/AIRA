import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import {
  Sparkles,
  ArrowRight,
  Shield,
  Search,
  Database,
  Cpu,
  CheckCircle2,
  PieChart,
  Bell,
  Sliders,
  ChevronRight,
  Terminal,
  Activity,
  Lock,
  FileText,
  Bookmark,
  Menu,
  X,
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { GlassCard } from '../components/ui/GlassCard';
import { Button } from '../components/ui/Button';
import { Badge } from '../components/ui/Badge';

interface PipelineStep {
  id: string;
  stepNumber: string;
  title: string;
  category: string;
  icon: React.ElementType;
  description: string;
  sampleOutput: {
    status: string;
    metrics?: Record<string, string>;
    insights?: string[];
    evidence?: string[];
    riskVector?: string;
  };
}

const PIPELINE_STEPS: PipelineStep[] = [
  {
    id: 'discovery',
    stepNumber: '01',
    title: 'Multi-Source Discovery',
    category: 'Market Ingestion',
    icon: Search,
    description: 'Autonomous multi-source ingestion fetching live market quotes, financial statements, and executive news sentiment.',
    sampleOutput: {
      status: 'Target Ingested: NVDA (NVIDIA Corp)',
      metrics: {
        'Current Price': '$128.50',
        'Market Cap': '$3.16T',
        'Trailing P/E': '64.2x',
        'EV / EBITDA': '51.8x',
        'Rev Growth YoY': '+122.4%',
      },
      evidence: [
        'SEC 10-Q filing confirmed Data Center compute segment revenue surged to $26.3B.',
        'Gross margin expanded to 75.1% driven by Blackwell architecture demand.',
      ],
    },
  },
  {
    id: 'portfolio-weight',
    stepNumber: '02',
    title: 'Deterministic Portfolio Valuation',
    category: 'Asset Weighting',
    icon: PieChart,
    description: 'Exact mathematical calculation of user holdings, true cost-basis, unrealized gains, and asset concentration.',
    sampleOutput: {
      status: 'Portfolio Snapshot Computed (Zero LLM Overhead)',
      metrics: {
        'Total Market Value': '$125,000.00',
        'Cost Basis': '$100,000.00',
        'Unrealized P&L': '+$25,000.00 (+25.0%)',
        'NVDA Weight': '60.0% of Portfolio',
      },
      insights: [
        'Holding concentration in semiconductor hardware exceeds standard diversification threshold (40.0%).',
        'Cost-basis calculated deterministically via weighted average FIFO accounting.',
      ],
    },
  },
  {
    id: 'multi-agent',
    stepNumber: '03',
    title: 'Multi-Agent AI Synthesis',
    category: 'CrewAI + Gemini',
    icon: Cpu,
    description: 'Specialized autonomous agents evaluate competitive moats, valuation multiples, and macroeconomic headwinds.',
    sampleOutput: {
      status: 'Multi-Agent Consensus Synthesized',
      insights: [
        'Financial Analyst Agent: Blackwell ramp supports FY26 margin defensibility against custom ASIC competition.',
        'Risk Agent: High hyperscaler capex dependency creates cyclical vulnerability if AI ROI moderation occurs.',
      ],
      riskVector: 'Elevated customer concentration (top 4 cloud providers account for ~40% of total revenue).',
    },
  },
  {
    id: 'personalization',
    stepNumber: '04',
    title: 'Investor Profile Alignment',
    category: 'Personalized Context',
    icon: Sliders,
    description: 'Contextualizes research against individual risk preferences (Moderate) and investment time horizon (5+ Years).',
    sampleOutput: {
      status: 'Personalized Alignment Matrix',
      metrics: {
        'Target Risk Profile': 'Moderate Growth',
        'Time Horizon': 'Long-Term (3-5 yrs)',
        'Focus Theme': 'Artificial Intelligence Infrastructure',
      },
      insights: [
        'Thesis fits long-term thematic focus, but current 60% portfolio weighting conflicts with moderate risk parameters.',
      ],
    },
  },
  {
    id: 'monitoring',
    stepNumber: '05',
    title: 'Deterministic Telemetry & Alerts',
    category: 'Rule Engine',
    icon: Bell,
    description: 'Automated monitoring evaluates price swings and portfolio drawdowns using strict mathematical rules.',
    sampleOutput: {
      status: 'Telemetry Active (15s polling)',
      metrics: {
        'Price Move Rule': 'Trigger on >5.0% 24h delta',
        'Drawdown Rule': 'Trigger on >10.0% portfolio shift',
        'Delivery Channels': 'In-App + Signed Webhooks',
      },
      insights: [
        'Automated idempotent dispatch ensures zero duplicate notifications with exponential retry backoff.',
      ],
    },
  },
  {
    id: 'reconciliation',
    stepNumber: '06',
    title: 'Persistent Semantic Memory',
    category: 'Memory Provenance',
    icon: Database,
    description: 'Persists structured findings to vector storage (pgvector) to ground future research and track thesis evolution.',
    sampleOutput: {
      status: 'Vector Record Stored (#8429)',
      insights: [
        'Semantic embedding generated and indexed in Supabase pgvector.',
        'Historical provenance linked to immutable user audit log for verifiable research recall.',
      ],
    },
  },
];

export const Landing: React.FC = () => {
  const { isAuthenticated } = useAuth();
  const [activeStepId, setActiveStepId] = useState<string>('discovery');
  const [mobileMenuOpen, setMobileMenuOpen] = useState<boolean>(false);

  const activeStep = PIPELINE_STEPS.find((s) => s.id === activeStepId) || PIPELINE_STEPS[0];

  return (
    <div className="min-h-screen bg-background text-slate-100 selection:bg-brand-500/30 selection:text-brand-200 overflow-x-hidden font-sans">
      {/* Background Ambient Glows & Grid */}
      <div className="fixed inset-0 pointer-events-none z-0">
        <div className="absolute top-[-10%] left-1/2 -translate-x-1/2 w-[800px] h-[500px] bg-gradient-to-b from-brand-600/15 via-brand-cyan/10 to-transparent blur-[120px] rounded-full" />
        <div className="absolute top-[35%] right-[-10%] w-[600px] h-[600px] bg-brand-500/5 blur-[140px] rounded-full" />
        <div className="absolute top-[70%] left-[-10%] w-[600px] h-[600px] bg-brand-emerald/5 blur-[140px] rounded-full" />
        <div className="absolute inset-0 bg-[radial-gradient(rgba(255,255,255,0.03)_1px,transparent_1px)] [background-size:32px_32px] opacity-70" />
      </div>

      {/* Top Navigation Bar */}
      <header className="fixed top-0 inset-x-0 z-50 backdrop-blur-md bg-background/80 border-b border-border-subtle/80">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-3 group focus:outline-none focus-visible:ring-2 focus-visible:ring-brand-400 rounded-lg">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-brand-600 via-brand-500 to-brand-cyan p-[1px] shadow-glow-brand flex items-center justify-center">
              <div className="w-full h-full bg-surface-200 rounded-[11px] flex items-center justify-center">
                <Sparkles className="w-4 h-4 text-brand-300 group-hover:scale-110 transition-transform duration-200" />
              </div>
            </div>
            <div className="flex flex-col">
              <span className="text-lg font-bold text-white tracking-tight flex items-center gap-1.5">
                AIRA
                <span className="text-[10px] uppercase font-semibold tracking-wider text-brand-cyan bg-brand-cyan/10 px-1.5 py-0.5 rounded border border-brand-cyan/20">
                  v1.0
                </span>
              </span>
            </div>
          </Link>

          {/* Desktop Navigation Links */}
          <nav className="hidden md:flex items-center gap-8 text-sm text-slate-300 font-medium" aria-label="Main Navigation">
            <a href="#capabilities" className="hover:text-white transition-colors duration-150">Capabilities</a>
            <a href="#pipeline" className="hover:text-white transition-colors duration-150">Intelligence Console</a>
            <a href="#how-it-works" className="hover:text-white transition-colors duration-150">How It Works</a>
            <a href="#architecture" className="hover:text-white transition-colors duration-150">Architecture</a>
          </nav>

          {/* Action CTAs */}
          <div className="hidden md:flex items-center gap-3">
            {isAuthenticated ? (
              <Link to="/app/dashboard">
                <Button size="sm" variant="glow" rightIcon={<ArrowRight className="w-4 h-4" />}>
                  Open Dashboard
                </Button>
              </Link>
            ) : (
              <>
                <Link to="/login">
                  <Button size="sm" variant="ghost">
                    Sign In
                  </Button>
                </Link>
                <Link to="/register">
                  <Button size="sm" variant="glow" rightIcon={<ArrowRight className="w-4 h-4" />}>
                    Get Started
                  </Button>
                </Link>
              </>
            )}
          </div>

          {/* Mobile Menu Toggle */}
          <div className="md:hidden flex items-center">
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="p-2 text-slate-400 hover:text-white focus:outline-none"
              aria-label="Toggle Mobile Navigation"
            >
              {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>

        {/* Mobile Dropdown */}
        {mobileMenuOpen && (
          <div className="md:hidden px-4 pt-2 pb-6 bg-surface-200/95 border-b border-border-subtle space-y-4 animate-in slide-in-from-top-2">
            <nav className="flex flex-col space-y-3 text-sm text-slate-300 font-medium">
              <a href="#capabilities" onClick={() => setMobileMenuOpen(false)} className="hover:text-white py-1">Capabilities</a>
              <a href="#pipeline" onClick={() => setMobileMenuOpen(false)} className="hover:text-white py-1">Intelligence Console</a>
              <a href="#how-it-works" onClick={() => setMobileMenuOpen(false)} className="hover:text-white py-1">How It Works</a>
              <a href="#architecture" onClick={() => setMobileMenuOpen(false)} className="hover:text-white py-1">Architecture</a>
            </nav>
            <div className="pt-2 flex flex-col gap-2">
              {isAuthenticated ? (
                <Link to="/app/dashboard" onClick={() => setMobileMenuOpen(false)}>
                  <Button className="w-full justify-center" variant="glow">
                    Open Dashboard
                  </Button>
                </Link>
              ) : (
                <>
                  <Link to="/login" onClick={() => setMobileMenuOpen(false)}>
                    <Button className="w-full justify-center" variant="secondary">
                      Sign In
                    </Button>
                  </Link>
                  <Link to="/register" onClick={() => setMobileMenuOpen(false)}>
                    <Button className="w-full justify-center" variant="glow">
                      Get Started
                    </Button>
                  </Link>
                </>
              )}
            </div>
          </div>
        )}
      </header>

      {/* Main Page Content */}
      <main className="relative z-10 pt-28">
        {/* ================================================================= */}
        {/* 1. HERO SECTION */}
        {/* ================================================================= */}
        <section id="hero" className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-12 pb-20 text-center">
          {/* Eyebrow Pill */}
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-surface-100/90 border border-brand-500/30 text-brand-300 text-xs font-semibold uppercase tracking-wider mb-8 shadow-glow-brand animate-in fade-in duration-500">
            <Sparkles className="w-3.5 h-3.5 text-brand-cyan animate-pulse" />
            <span>Autonomous Investment Research Agent</span>
          </div>

          {/* Main H1 Headline */}
          <h1 className="text-4xl sm:text-6xl md:text-7xl font-extrabold tracking-tight text-white max-w-4xl mx-auto leading-[1.1] mb-6">
            Your Investment Research,{' '}
            <span className="bg-gradient-to-r from-brand-300 via-brand-cyan to-brand-400 bg-clip-text text-transparent">
              Running on Autonomous Intelligence.
            </span>
          </h1>

          {/* Subtitle */}
          <p className="text-base sm:text-xl text-slate-300 max-w-2xl mx-auto leading-relaxed mb-10 font-normal">
            Turn scattered financial statements, market quotes, news, and portfolio weights into evidence-grounded, multi-agent investment intelligence.
          </p>

          {/* Hero CTAs */}
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-16">
            <Link to={isAuthenticated ? '/app/dashboard' : '/register'} className="w-full sm:w-auto">
              <Button size="lg" variant="glow" className="w-full sm:w-auto px-8" rightIcon={<ArrowRight className="w-5 h-5" />}>
                {isAuthenticated ? 'Open Investor Dashboard' : 'Get Started Free'}
              </Button>
            </Link>
            <a href="#pipeline" className="w-full sm:w-auto">
              <Button size="lg" variant="secondary" className="w-full sm:w-auto px-6" leftIcon={<Terminal className="w-4 h-4 text-brand-cyan" />}>
                Explore Intelligence Console
              </Button>
            </a>
          </div>

          {/* Trust / Capability Strip */}
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3 max-w-5xl mx-auto pt-6 border-t border-border-subtle/60">
            {[
              { icon: Cpu, label: 'Multi-Agent Synthesis' },
              { icon: PieChart, label: 'Real-Time Portfolio' },
              { icon: Shield, label: 'Deterministic Alerts' },
              { icon: FileText, label: 'Evidence-Grounded' },
              { icon: Database, label: 'Vector Memory (pgvector)' },
              { icon: Lock, label: 'Multi-Tenant Isolation' },
            ].map((item, idx) => (
              <div
                key={idx}
                className="flex items-center justify-center gap-2 p-2.5 rounded-xl bg-surface-200/40 border border-border-subtle text-slate-300 text-xs font-medium"
              >
                <item.icon className="w-3.5 h-3.5 text-brand-400 shrink-0" />
                <span>{item.label}</span>
              </div>
            ))}
          </div>
        </section>

        {/* ================================================================= */}
        {/* 2. WOW FACTOR: INTERACTIVE INTELLIGENCE CONSOLE */}
        {/* ================================================================= */}
        <section id="pipeline" className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
          <div className="text-center max-w-3xl mx-auto mb-12">
            <Badge variant="brand" className="mb-3 uppercase tracking-wider">
              Interactive Preview
            </Badge>
            <h2 className="text-3xl sm:text-4xl font-bold text-white tracking-tight mb-4">
              The AIRA Intelligence Console
            </h2>
            <p className="text-slate-400 text-sm sm:text-base">
              Observe how raw signals progress through multi-agent reasoning, deterministic portfolio valuation, and telemetry dispatch.
            </p>
          </div>

          {/* Console Container */}
          <GlassCard glow="brand" className="p-4 sm:p-6 lg:p-8 rounded-3xl border-border-strong bg-surface-200/80">
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
              {/* Left Column: Stage Selector Tabs */}
              <div className="lg:col-span-4 space-y-2">
                <div className="text-xs font-semibold uppercase tracking-wider text-slate-400 px-3 pb-2 flex items-center justify-between">
                  <span>Intelligence Pipeline</span>
                  <Activity className="w-3.5 h-3.5 text-brand-cyan animate-pulse" />
                </div>

                {PIPELINE_STEPS.map((step) => {
                  const isActive = step.id === activeStepId;
                  const Icon = step.icon;
                  return (
                    <button
                      key={step.id}
                      onClick={() => setActiveStepId(step.id)}
                      className={`w-full text-left p-3.5 rounded-2xl transition-all duration-200 border flex items-start gap-3.5 group focus:outline-none focus-visible:ring-2 focus-visible:ring-brand-400 ${
                        isActive
                          ? 'bg-brand-500/15 border-brand-500/40 text-white shadow-glow-brand'
                          : 'bg-surface-100/40 border-border-subtle text-slate-400 hover:bg-surface-100 hover:text-slate-200'
                      }`}
                    >
                      <div
                        className={`w-8 h-8 rounded-lg flex items-center justify-center shrink-0 mt-0.5 ${
                          isActive
                            ? 'bg-brand-500 text-white shadow-sm'
                            : 'bg-surface-300 text-slate-400 group-hover:text-white'
                        }`}
                      >
                        <Icon className="w-4 h-4" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center justify-between">
                          <span className="text-xs font-mono font-semibold text-brand-cyan">
                            STAGE {step.stepNumber}
                          </span>
                          <span className="text-[10px] text-slate-400 uppercase tracking-wider">
                            {step.category}
                          </span>
                        </div>
                        <h3 className="text-sm font-semibold truncate mt-0.5">
                          {step.title}
                        </h3>
                      </div>
                    </button>
                  );
                })}
              </div>

              {/* Right Column: Terminal Viewport */}
              <div className="lg:col-span-8 flex flex-col">
                <div className="flex-1 rounded-2xl bg-surface-400/90 border border-border-subtle p-5 sm:p-6 font-mono flex flex-col justify-between shadow-inner">
                  {/* Terminal Header */}
                  <div>
                    <div className="flex items-center justify-between pb-4 mb-4 border-b border-border-subtle/80">
                      <div className="flex items-center gap-2">
                        <div className="w-3 h-3 rounded-full bg-red-500/80" />
                        <div className="w-3 h-3 rounded-full bg-yellow-500/80" />
                        <div className="w-3 h-3 rounded-full bg-green-500/80" />
                        <span className="text-xs text-slate-400 ml-2 font-mono">
                          aira-engine://pipeline/{activeStep.id}
                        </span>
                      </div>
                      <span className="text-[10px] text-brand-emerald bg-brand-emerald/10 px-2 py-0.5 rounded-full border border-brand-emerald/20 flex items-center gap-1">
                        <span className="w-1.5 h-1.5 rounded-full bg-brand-emerald animate-ping" />
                        SYNTHESIS OK
                      </span>
                    </div>

                    {/* Step Title & Description */}
                    <div className="mb-5">
                      <span className="text-xs font-semibold text-brand-cyan tracking-wider uppercase">
                        Stage {activeStep.stepNumber} — {activeStep.category}
                      </span>
                      <h4 className="text-lg font-bold text-white font-sans mt-0.5 mb-1.5">
                        {activeStep.title}
                      </h4>
                      <p className="text-xs text-slate-300 font-sans leading-relaxed">
                        {activeStep.description}
                      </p>
                    </div>

                    {/* Status Badge */}
                    <div className="mb-4 inline-flex items-center gap-2 px-3 py-1.5 rounded-lg bg-surface-200 border border-border-subtle text-xs text-brand-300">
                      <Terminal className="w-3.5 h-3.5 text-brand-cyan" />
                      <span>{activeStep.sampleOutput.status}</span>
                    </div>

                    {/* Key Metrics Grid (if present) */}
                    {activeStep.sampleOutput.metrics && (
                      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 mb-4">
                        {Object.entries(activeStep.sampleOutput.metrics).map(([key, val]) => (
                          <div key={key} className="p-2.5 rounded-xl bg-surface-200/60 border border-border-subtle">
                            <div className="text-[10px] text-slate-400 uppercase tracking-tight">{key}</div>
                            <div className="text-xs sm:text-sm font-bold text-white mt-0.5">{val}</div>
                          </div>
                        ))}
                      </div>
                    )}

                    {/* Evidence & Insights */}
                    {activeStep.sampleOutput.insights && (
                      <div className="space-y-2 mb-4">
                        <div className="text-[11px] uppercase tracking-wider text-slate-400 font-semibold">
                          Synthesized Findings:
                        </div>
                        {activeStep.sampleOutput.insights.map((ins, i) => (
                          <div key={i} className="flex items-start gap-2 text-xs text-slate-200 font-sans leading-relaxed">
                            <ChevronRight className="w-3.5 h-3.5 text-brand-cyan shrink-0 mt-0.5" />
                            <span>{ins}</span>
                          </div>
                        ))}
                      </div>
                    )}

                    {activeStep.sampleOutput.evidence && (
                      <div className="space-y-2 mb-4">
                        <div className="text-[11px] uppercase tracking-wider text-slate-400 font-semibold">
                          Grounding Evidence:
                        </div>
                        {activeStep.sampleOutput.evidence.map((ev, i) => (
                          <div key={i} className="flex items-start gap-2 text-xs text-slate-300 font-sans leading-relaxed bg-surface-200/40 p-2 rounded-lg border border-border-subtle">
                            <CheckCircle2 className="w-3.5 h-3.5 text-brand-emerald shrink-0 mt-0.5" />
                            <span>{ev}</span>
                          </div>
                        ))}
                      </div>
                    )}

                    {activeStep.sampleOutput.riskVector && (
                      <div className="mt-3 p-3 rounded-xl bg-amber-500/10 border border-amber-500/20 text-amber-200 text-xs font-sans">
                        <span className="font-semibold text-amber-300">Risk Vector: </span>
                        {activeStep.sampleOutput.riskVector}
                      </div>
                    )}
                  </div>

                  {/* Terminal Footer Disclaimer */}
                  <div className="pt-4 mt-4 border-t border-border-subtle/80 flex items-center justify-between text-[11px] text-slate-400 font-sans">
                    <span>Illustrative Synthesis Preview</span>
                    <span className="text-brand-cyan font-mono">AIRA Engine v1.0</span>
                  </div>
                </div>
              </div>
            </div>
          </GlassCard>
        </section>

        {/* ================================================================= */}
        {/* 3. THE PROBLEM VS AIRA */}
        {/* ================================================================= */}
        <section id="problem" className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 border-t border-border-subtle/60">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <Badge variant="amber" className="mb-3 uppercase tracking-wider">
              The Problem
            </Badge>
            <h2 className="text-3xl sm:text-4xl font-bold text-white tracking-tight mb-4">
              Investment Research is Fragmented. AIRA Unifies It.
            </h2>
            <p className="text-slate-300 text-base">
              Investors today juggle dozens of isolated data sources with no unified intelligence layer connecting research to portfolio reality.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-5xl mx-auto">
            {/* The Old Way */}
            <div className="p-6 sm:p-8 rounded-3xl bg-surface-200/40 border border-red-500/20 relative overflow-hidden">
              <div className="text-xs font-bold uppercase tracking-wider text-red-400 mb-2">
                Traditional Fragmentation
              </div>
              <h3 className="text-xl font-bold text-white mb-4">Scattered, Stale & Disconnected</h3>
              <ul className="space-y-3.5 text-sm text-slate-400">
                <li className="flex items-start gap-2.5">
                  <span className="w-1.5 h-1.5 rounded-full bg-red-400 mt-2 shrink-0" />
                  <span>10+ browser tabs open across SEC filings, news outlets, valuation charts, and stock screeners.</span>
                </li>
                <li className="flex items-start gap-2.5">
                  <span className="w-1.5 h-1.5 rounded-full bg-red-400 mt-2 shrink-0" />
                  <span>Research notes stored in separate documents that never reconcile against actual portfolio holdings.</span>
                </li>
                <li className="flex items-start gap-2.5">
                  <span className="w-1.5 h-1.5 rounded-full bg-red-400 mt-2 shrink-0" />
                  <span>Alerts configured on basic price thresholds with zero thematic or multi-agent context.</span>
                </li>
                <li className="flex items-start gap-2.5">
                  <span className="w-1.5 h-1.5 rounded-full bg-red-400 mt-2 shrink-0" />
                  <span>Investment thesis lost over time, leading to repeated work and forgotten conviction reasoning.</span>
                </li>
              </ul>
            </div>

            {/* The AIRA Way */}
            <div className="p-6 sm:p-8 rounded-3xl bg-surface-200/80 border border-brand-500/40 relative shadow-glow-brand">
              <div className="text-xs font-bold uppercase tracking-wider text-brand-cyan mb-2">
                The AIRA Engine
              </div>
              <h3 className="text-xl font-bold text-white mb-4">Continuous, Context-Aware Intelligence</h3>
              <ul className="space-y-3.5 text-sm text-slate-200">
                <li className="flex items-start gap-2.5">
                  <CheckCircle2 className="w-4 h-4 text-brand-cyan mt-0.5 shrink-0" />
                  <span>Multi-agent synthesis extracts fundamental metrics and key risks in seconds.</span>
                </li>
                <li className="flex items-start gap-2.5">
                  <CheckCircle2 className="w-4 h-4 text-brand-cyan mt-0.5 shrink-0" />
                  <span>Live portfolio weighting directly influences research risk evaluation and diversification alerts.</span>
                </li>
                <li className="flex items-start gap-2.5">
                  <CheckCircle2 className="w-4 h-4 text-brand-cyan mt-0.5 shrink-0" />
                  <span>Deterministic mathematical telemetry detects drawdowns and price spikes with retry-safe webhook delivery.</span>
                </li>
                <li className="flex items-start gap-2.5">
                  <CheckCircle2 className="w-4 h-4 text-brand-cyan mt-0.5 shrink-0" />
                  <span>Persistent vector memory (pgvector) ensures historical research grounds future investment decisions.</span>
                </li>
              </ul>
            </div>
          </div>
        </section>

        {/* ================================================================= */}
        {/* 4. HOW AIRA WORKS: 6-STEP WORKFLOW */}
        {/* ================================================================= */}
        <section id="how-it-works" className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 border-t border-border-subtle/60">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <Badge variant="brand" className="mb-3 uppercase tracking-wider">
              Workflow Architecture
            </Badge>
            <h2 className="text-3xl sm:text-4xl font-bold text-white tracking-tight mb-4">
              How AIRA Transforms Data into Decisions
            </h2>
            <p className="text-slate-300 text-base">
              A structured 6-step lifecycle that balances autonomous AI reasoning with deterministic mathematical precision.
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {[
              {
                num: '01',
                title: 'Discover & Search',
                desc: 'Locate equities, tickers, and companies with real-time quote resolution and fundamental data indexing.',
                icon: Search,
              },
              {
                num: '02',
                title: 'Ingest Financials',
                desc: 'Fetch financial statements, valuation multiples, and recent news articles into a structured evidence corpus.',
                icon: FileText,
              },
              {
                num: '03',
                title: 'Multi-Agent Synthesis',
                desc: 'Specialized AI agents debate moat sustainability, valuation risks, and growth catalysts to form a consensus.',
                icon: Cpu,
              },
              {
                num: '04',
                title: 'Portfolio Contextualize',
                desc: 'Weigh research findings against actual user holdings, asset allocation percentages, and watchlist priorities.',
                icon: PieChart,
              },
              {
                num: '05',
                title: 'Monitor & Alert',
                desc: 'Run deterministic background monitoring for price threshold breaches, drawdown limits, and notification delivery.',
                icon: Bell,
              },
              {
                num: '06',
                title: 'Retain in Memory',
                desc: 'Store verified reports in vector memory to track thesis evolution and power continuous recall.',
                icon: Database,
              },
            ].map((step, idx) => (
              <div
                key={idx}
                className="p-6 rounded-3xl bg-surface-200/50 border border-border-subtle hover:border-brand-500/40 hover:bg-surface-200 transition-all duration-200 group"
              >
                <div className="flex items-center justify-between mb-4">
                  <span className="text-2xl font-black font-mono text-brand-cyan/60 group-hover:text-brand-cyan transition-colors">
                    {step.num}
                  </span>
                  <div className="w-10 h-10 rounded-xl bg-surface-100 flex items-center justify-center text-slate-300 group-hover:text-brand-300 group-hover:bg-brand-500/10 transition-colors">
                    <step.icon className="w-5 h-5" />
                  </div>
                </div>
                <h3 className="text-lg font-bold text-white mb-2">{step.title}</h3>
                <p className="text-xs text-slate-400 leading-relaxed">{step.desc}</p>
              </div>
            ))}
          </div>
        </section>

        {/* ================================================================= */}
        {/* 5. CORE CAPABILITIES */}
        {/* ================================================================= */}
        <section id="capabilities" className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 border-t border-border-subtle/60">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <Badge variant="brand" className="mb-3 uppercase tracking-wider">
              Core Capabilities
            </Badge>
            <h2 className="text-3xl sm:text-4xl font-bold text-white tracking-tight mb-4">
              Engineered for Serious Research
            </h2>
            <p className="text-slate-300 text-base">
              Explore the dedicated feature suites that power autonomous investment intelligence across the platform.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <GlassCard className="p-6 rounded-3xl flex flex-col justify-between">
              <div>
                <div className="w-10 h-10 rounded-xl bg-brand-500/10 border border-brand-500/20 flex items-center justify-center text-brand-cyan mb-4">
                  <Cpu className="w-5 h-5" />
                </div>
                <h3 className="text-lg font-bold text-white mb-2">Autonomous Company Research</h3>
                <p className="text-xs text-slate-400 leading-relaxed mb-4">
                  Multi-agent deep dives analyzing company business models, revenue drivers, valuation multiples, and latest market news.
                </p>
              </div>
              <div className="pt-4 border-t border-border-subtle/60 flex items-center justify-between text-[11px] text-slate-400">
                <span>CrewAI + Gemini 2.0</span>
                <span className="text-brand-cyan font-semibold">Evidence Grounded</span>
              </div>
            </GlassCard>

            <GlassCard className="p-6 rounded-3xl flex flex-col justify-between">
              <div>
                <div className="w-10 h-10 rounded-xl bg-brand-500/10 border border-brand-500/20 flex items-center justify-center text-brand-cyan mb-4">
                  <PieChart className="w-5 h-5" />
                </div>
                <h3 className="text-lg font-bold text-white mb-2">Portfolio Intelligence</h3>
                <p className="text-xs text-slate-400 leading-relaxed mb-4">
                  Whole-portfolio valuation and risk analysis combining exact holding weights, cost-basis accounting, and watchlist priorities.
                </p>
              </div>
              <div className="pt-4 border-t border-border-subtle/60 flex items-center justify-between text-[11px] text-slate-400">
                <span>Deterministic Math</span>
                <span className="text-brand-cyan font-semibold">Asset Weights</span>
              </div>
            </GlassCard>

            <GlassCard className="p-6 rounded-3xl flex flex-col justify-between">
              <div>
                <div className="w-10 h-10 rounded-xl bg-brand-500/10 border border-brand-500/20 flex items-center justify-center text-brand-cyan mb-4">
                  <Bookmark className="w-5 h-5" />
                </div>
                <h3 className="text-lg font-bold text-white mb-2">High-Conviction Watchlists</h3>
                <p className="text-xs text-slate-400 leading-relaxed mb-4">
                  Tiered watchlist management with priority filters (High, Normal, Low) and automated price delta monitoring.
                </p>
              </div>
              <div className="pt-4 border-t border-border-subtle/60 flex items-center justify-between text-[11px] text-slate-400">
                <span>Priority Filters</span>
                <span className="text-brand-cyan font-semibold">24h Price Feeds</span>
              </div>
            </GlassCard>

            <GlassCard className="p-6 rounded-3xl flex flex-col justify-between">
              <div>
                <div className="w-10 h-10 rounded-xl bg-brand-500/10 border border-brand-500/20 flex items-center justify-center text-brand-cyan mb-4">
                  <Bell className="w-5 h-5" />
                </div>
                <h3 className="text-lg font-bold text-white mb-2">Deterministic Alert Telemetry</h3>
                <p className="text-xs text-slate-400 leading-relaxed mb-4">
                  Threshold monitoring with multi-channel dispatch (In-App, Email, HMAC-signed Webhooks) and automated retry backoff.
                </p>
              </div>
              <div className="pt-4 border-t border-border-subtle/60 flex items-center justify-between text-[11px] text-slate-400">
                <span>Zero Hallucination</span>
                <span className="text-brand-cyan font-semibold">HMAC Signed</span>
              </div>
            </GlassCard>

            <GlassCard className="p-6 rounded-3xl flex flex-col justify-between">
              <div>
                <div className="w-10 h-10 rounded-xl bg-brand-500/10 border border-brand-500/20 flex items-center justify-center text-brand-cyan mb-4">
                  <Database className="w-5 h-5" />
                </div>
                <h3 className="text-lg font-bold text-white mb-2">Persistent Semantic Memory</h3>
                <p className="text-xs text-slate-400 leading-relaxed mb-4">
                  Supabase pgvector embedding memory preserving historical research reports to ground subsequent analytical sessions.
                </p>
              </div>
              <div className="pt-4 border-t border-border-subtle/60 flex items-center justify-between text-[11px] text-slate-400">
                <span>pgvector Storage</span>
                <span className="text-brand-cyan font-semibold">Immutable Provenance</span>
              </div>
            </GlassCard>

            <GlassCard className="p-6 rounded-3xl flex flex-col justify-between">
              <div>
                <div className="w-10 h-10 rounded-xl bg-brand-500/10 border border-brand-500/20 flex items-center justify-center text-brand-cyan mb-4">
                  <Sliders className="w-5 h-5" />
                </div>
                <h3 className="text-lg font-bold text-white mb-2">Investor Personalization</h3>
                <p className="text-xs text-slate-400 leading-relaxed mb-4">
                  Customizable risk tolerance (Conservative, Moderate, Aggressive) and investment horizons (Short, Medium, Long-Term).
                </p>
              </div>
              <div className="pt-4 border-t border-border-subtle/60 flex items-center justify-between text-[11px] text-slate-400">
                <span>Risk Profiles</span>
                <span className="text-brand-cyan font-semibold">Tailored Guidance</span>
              </div>
            </GlassCard>
          </div>
        </section>

        {/* ================================================================= */}
        {/* 6. ARCHITECTURE: DETERMINISTIC VS AI SEPARATION */}
        {/* ================================================================= */}
        <section id="architecture" className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 border-t border-border-subtle/60">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <Badge variant="brand" className="mb-3 uppercase tracking-wider">
              System Design
            </Badge>
            <h2 className="text-3xl sm:text-4xl font-bold text-white tracking-tight mb-4">
              Deterministic Math Meets Autonomous AI
            </h2>
            <p className="text-slate-300 text-base">
              AIRA enforces strict architectural boundaries: AI reasoning is never permitted in mathematical calculations, threshold evaluations, or auth.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-5xl mx-auto">
            {/* AI Tier */}
            <div className="p-6 sm:p-8 rounded-3xl bg-surface-200/60 border border-brand-500/30">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-8 h-8 rounded-lg bg-brand-500/20 flex items-center justify-center text-brand-cyan">
                  <Cpu className="w-4 h-4" />
                </div>
                <h3 className="text-lg font-bold text-white">Autonomous AI Tier</h3>
              </div>
              <p className="text-xs text-slate-300 mb-4 leading-relaxed">
                Applied strictly to qualitative synthesis, competitive moat evaluations, and evidence-grounded thesis exploration.
              </p>
              <ul className="space-y-2 text-xs text-slate-400">
                <li className="flex items-center gap-2">
                  <CheckCircle2 className="w-3.5 h-3.5 text-brand-cyan shrink-0" />
                  <span>CrewAI Multi-Agent Coordination</span>
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircle2 className="w-3.5 h-3.5 text-brand-cyan shrink-0" />
                  <span>Google Gemini 2.0 Flash Reasoning</span>
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircle2 className="w-3.5 h-3.5 text-brand-cyan shrink-0" />
                  <span>Evidence Grounding with Cited Citations</span>
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircle2 className="w-3.5 h-3.5 text-brand-cyan shrink-0" />
                  <span>Vector Embedding Memory Synthesis</span>
                </li>
              </ul>
            </div>

            {/* Deterministic Tier */}
            <div className="p-6 sm:p-8 rounded-3xl bg-surface-200/60 border border-brand-emerald/30">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-8 h-8 rounded-lg bg-brand-emerald/20 flex items-center justify-center text-brand-emerald">
                  <Shield className="w-4 h-4" />
                </div>
                <h3 className="text-lg font-bold text-white">Deterministic Rule Tier</h3>
              </div>
              <p className="text-xs text-slate-300 mb-4 leading-relaxed">
                Applied to all mathematical calculations, alert thresholds, authorization guards, and notification retry mechanics.
              </p>
              <ul className="space-y-2 text-xs text-slate-400">
                <li className="flex items-center gap-2">
                  <CheckCircle2 className="w-3.5 h-3.5 text-brand-emerald shrink-0" />
                  <span>Cost-Basis & Valuation Mathematics</span>
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircle2 className="w-3.5 h-3.5 text-brand-emerald shrink-0" />
                  <span>Price Delta & Drawdown Threshold Logic</span>
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircle2 className="w-3.5 h-3.5 text-brand-emerald shrink-0" />
                  <span>JWT Auth & Multi-Tenant Data Isolation</span>
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircle2 className="w-3.5 h-3.5 text-brand-emerald shrink-0" />
                  <span>Exponential Backoff Webhook Delivery</span>
                </li>
              </ul>
            </div>
          </div>
        </section>

        {/* ================================================================= */}
        {/* 7. FINAL CALL TO ACTION */}
        {/* ================================================================= */}
        <section id="get-started" className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24 border-t border-border-subtle/60">
          <GlassCard glow="brand" className="p-8 sm:p-12 lg:p-16 rounded-3xl text-center max-w-4xl mx-auto relative overflow-hidden">
            <div className="relative z-10">
              <Badge variant="brand" className="mb-4 uppercase tracking-wider">
                Start Exploring Today
              </Badge>
              <h2 className="text-3xl sm:text-5xl font-extrabold text-white tracking-tight mb-4">
                Build Your Investment Intelligence Layer.
              </h2>
              <p className="text-slate-300 text-sm sm:text-base max-w-xl mx-auto mb-8 leading-relaxed">
                Join autonomous investment research with grounded multi-agent synthesis, deterministic telemetry, and personalized portfolio intelligence.
              </p>
              <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
                <Link to={isAuthenticated ? '/app/dashboard' : '/register'} className="w-full sm:w-auto">
                  <Button size="lg" variant="glow" className="w-full sm:w-auto px-8" rightIcon={<ArrowRight className="w-5 h-5" />}>
                    {isAuthenticated ? 'Open Dashboard' : 'Create Free Account'}
                  </Button>
                </Link>
                {!isAuthenticated && (
                  <Link to="/login" className="w-full sm:w-auto">
                    <Button size="lg" variant="secondary" className="w-full sm:w-auto px-8">
                      Sign In
                    </Button>
                  </Link>
                )}
              </div>
            </div>
          </GlassCard>
        </section>
      </main>

      {/* ================================================================= */}
      {/* 8. FOOTER */}
      {/* ================================================================= */}
      <footer className="border-t border-border-subtle/80 bg-surface-300/60 pt-16 pb-12 text-slate-400 text-xs">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8 pb-12 border-b border-border-subtle">
            {/* Column 1: Brand */}
            <div className="space-y-3 md:col-span-2">
              <div className="flex items-center gap-2.5">
                <div className="w-7 h-7 rounded-lg bg-gradient-to-tr from-brand-600 to-brand-cyan flex items-center justify-center text-white">
                  <Sparkles className="w-3.5 h-3.5" />
                </div>
                <span className="text-base font-bold text-white tracking-tight">AIRA</span>
              </div>
              <p className="text-slate-400 text-xs max-w-sm leading-relaxed">
                Autonomous Investment Research Agent. Unifying company fundamentals, multi-agent AI reasoning, and deterministic portfolio telemetry.
              </p>
            </div>

            {/* Column 2: Navigation */}
            <div className="space-y-2.5">
              <div className="text-xs font-semibold text-white uppercase tracking-wider">Navigation</div>
              <ul className="space-y-2">
                <li><a href="#hero" className="hover:text-slate-200 transition-colors">Overview</a></li>
                <li><a href="#pipeline" className="hover:text-slate-200 transition-colors">Intelligence Console</a></li>
                <li><a href="#capabilities" className="hover:text-slate-200 transition-colors">Capabilities</a></li>
                <li><a href="#architecture" className="hover:text-slate-200 transition-colors">Architecture</a></li>
              </ul>
            </div>

            {/* Column 3: Platform Access */}
            <div className="space-y-2.5">
              <div className="text-xs font-semibold text-white uppercase tracking-wider">Access</div>
              <ul className="space-y-2">
                <li><Link to="/login" className="hover:text-slate-200 transition-colors">Sign In</Link></li>
                <li><Link to="/register" className="hover:text-slate-200 transition-colors">Create Account</Link></li>
                <li><Link to="/app/dashboard" className="hover:text-slate-200 transition-colors">Investor Dashboard</Link></li>
              </ul>
            </div>
          </div>

          {/* Bottom Copyright & Financial Disclaimer */}
          <div className="pt-8 flex flex-col md:flex-row items-center justify-between gap-4 text-[11px] text-slate-500">
            <div>
              &copy; {new Date().getFullYear()} AIRA. All rights reserved. Version 1.0.0.
            </div>
            <div className="max-w-2xl text-center md:text-right text-slate-500">
              Disclaimer: AIRA is an autonomous investment research intelligence and decision-support platform. It does not provide guaranteed returns, automated trading execution, or personalized registered financial advice.
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};
