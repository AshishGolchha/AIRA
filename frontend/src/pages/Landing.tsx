import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import {
  Sparkles,
  ArrowRight,
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
  Menu,
  X,
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { GlassCard } from '../components/ui/GlassCard';
import { Button } from '../components/ui/Button';
import { Badge } from '../components/ui/Badge';
import { HeroIntelligenceEngine } from '../components/landing/HeroIntelligenceEngine';
import { MarketTerminalChart } from '../components/landing/MarketTerminalChart';
import { PortfolioAllocationVisual } from '../components/landing/PortfolioAllocationVisual';
import { MultiAgentNetworkVisual } from '../components/landing/MultiAgentNetworkVisual';
import { DataTransformationFlow } from '../components/landing/DataTransformationFlow';
import { EvidenceGroundingFlow } from '../components/landing/EvidenceGroundingFlow';
import { ArchitectureCircuit } from '../components/landing/ArchitectureCircuit';

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
  jsonPayload: Record<string, any>;
}

const PIPELINE_STEPS: PipelineStep[] = [
  {
    id: 'discovery',
    stepNumber: '01',
    title: 'Multi-Source Discovery',
    category: 'Market Ingestion',
    icon: Search,
    description: 'Autonomous multi-source ingestion fetching live market quotes, SEC filings, and executive news sentiment.',
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
    jsonPayload: {
      target: 'NVDA',
      source: 'SEC_EDGAR_10Q',
      period: 'Q2_FY25',
      data_center_rev_usd: 26300000000,
      gross_margin_pct: 75.1,
      yoy_growth_pct: 122.4,
      status: 'INGESTION_VERIFIED',
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
    jsonPayload: {
      portfolio_id: 104,
      valuation_engine: 'DETERMINISTIC_SQL',
      total_value_usd: 125000.0,
      cost_basis_usd: 100000.0,
      unrealized_gain_usd: 25000.0,
      holding_weight_pct: 60.0,
      concentration_warning: true,
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
    jsonPayload: {
      crew_agents: ['FundamentalAnalyst', 'ValuationSpecialist', 'MacroRiskOfficer'],
      consensus_confidence_pct: 88,
      moat_rating: 'WIDE_NETWORK_EFFECT',
      primary_risk: 'CUSTOMER_CONCENTRATION_TOP_4',
      llm_model: 'gemini-3.6-flash',
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
    jsonPayload: {
      user_profile_id: 42,
      risk_tolerance: 'MODERATE',
      horizon: '3_TO_5_YEARS',
      thematic_fit: true,
      allocation_rebalance_suggested: true,
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
    jsonPayload: {
      alert_engine: 'DETERMINISTIC_RULES',
      threshold_pct: 5.0,
      channels: ['IN_APP', 'WEBHOOK_HMAC_SHA256'],
      retry_backoff: 'EXPONENTIAL_JITTER',
      idempotency_key: 'alert_nvda_2026_08_31',
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
    jsonPayload: {
      memory_id: 8429,
      vector_dim: 768,
      model: 'gemini-embedding-2',
      storage: 'supabase_pgvector',
      immutable_audit_logged: true,
    },
  },
];

export const Landing: React.FC = () => {
  const { isAuthenticated } = useAuth();
  const [activeStepId, setActiveStepId] = useState<string>('discovery');
  const [consoleViewMode, setConsoleViewMode] = useState<'report' | 'json'>('report');
  const [mobileMenuOpen, setMobileMenuOpen] = useState<boolean>(false);

  const activeStep = PIPELINE_STEPS.find((s) => s.id === activeStepId) || PIPELINE_STEPS[0];

  return (
    <div className="min-h-screen bg-background text-slate-100 selection:bg-brand-500/30 selection:text-brand-200 overflow-x-hidden font-sans">
      {/* Ambient Lighting & Grid */}
      <div className="fixed inset-0 pointer-events-none z-0">
        <div className="absolute top-[-15%] left-1/2 -translate-x-1/2 w-[900px] h-[600px] bg-gradient-to-b from-brand-600/15 via-brand-cyan/10 to-transparent blur-[140px] rounded-full" />
        <div className="absolute top-[40%] right-[-15%] w-[700px] h-[700px] bg-brand-500/8 blur-[160px] rounded-full" />
        <div className="absolute top-[75%] left-[-15%] w-[700px] h-[700px] bg-brand-emerald/8 blur-[160px] rounded-full" />
        <div className="absolute inset-0 bg-grid-pattern opacity-40" />
      </div>

      {/* ================================================================= */}
      {/* NAVIGATION BAR */}
      {/* ================================================================= */}
      <header className="fixed top-0 inset-x-0 z-50 backdrop-blur-xl bg-background/85 border-b border-border-subtle/80">
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

          {/* Desktop Nav */}
          <nav className="hidden md:flex items-center gap-7 text-sm text-slate-300 font-medium" aria-label="Main Navigation">
            <a href="#hero" className="hover:text-white transition-colors duration-150">Live Engine</a>
            <a href="#market-terminal" className="hover:text-white transition-colors duration-150">Market Terminal</a>
            <a href="#data-flow" className="hover:text-white transition-colors duration-150">Data Pipeline</a>
            <a href="#multi-agent-network" className="hover:text-white transition-colors duration-150">Agent Network</a>
            <a href="#portfolio-allocation" className="hover:text-white transition-colors duration-150">Portfolio</a>
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
              <a href="#hero" onClick={() => setMobileMenuOpen(false)} className="hover:text-white py-1">Live Engine</a>
              <a href="#market-terminal" onClick={() => setMobileMenuOpen(false)} className="hover:text-white py-1">Market Terminal</a>
              <a href="#data-flow" onClick={() => setMobileMenuOpen(false)} className="hover:text-white py-1">Data Pipeline</a>
              <a href="#multi-agent-network" onClick={() => setMobileMenuOpen(false)} className="hover:text-white py-1">Agent Network</a>
              <a href="#portfolio-allocation" onClick={() => setMobileMenuOpen(false)} className="hover:text-white py-1">Portfolio</a>
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

      {/* ================================================================= */}
      {/* MAIN CONTENT AREA */}
      {/* ================================================================= */}
      <main className="relative z-10 pt-24 sm:pt-28">
        {/* ================================================================= */}
        {/* 1. HERO SECTION WITH INTELLIGENCE ENGINE CENTERPIECE */}
        {/* ================================================================= */}
        <section id="hero" className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-8 sm:pt-12 pb-16 text-center">
          {/* Eyebrow Pill */}
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-surface-100/90 border border-brand-500/30 text-brand-300 text-xs font-semibold uppercase tracking-wider mb-6 shadow-glow-brand">
            <Sparkles className="w-3.5 h-3.5 text-brand-cyan animate-pulse" />
            <span>Autonomous Investment Research Agent</span>
          </div>

          {/* Main H1 Headline */}
          <h1 className="text-4xl sm:text-6xl md:text-7xl font-extrabold tracking-tight text-white max-w-4xl mx-auto leading-[1.08] mb-6">
            Your Investment Research,{' '}
            <span className="text-shimmer bg-clip-text text-transparent">
              Running on Autonomous Intelligence.
            </span>
          </h1>

          {/* Subtitle */}
          <p className="text-base sm:text-lg text-slate-300 max-w-3xl mx-auto leading-relaxed mb-8 font-normal">
            Turn scattered financial filings, balance sheet telemetry, and market noise into grounded, multi-agent investment intelligence with deterministic portfolio precision.
          </p>

          {/* Hero CTAs */}
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-12">
            <Link to={isAuthenticated ? '/app/dashboard' : '/register'} className="w-full sm:w-auto">
              <Button size="lg" variant="glow" className="w-full sm:w-auto px-8" rightIcon={<ArrowRight className="w-5 h-5" />}>
                {isAuthenticated ? 'Open Investor Dashboard' : 'Get Started Free'}
              </Button>
            </Link>
            <a href="#market-terminal" className="w-full sm:w-auto">
              <Button size="lg" variant="secondary" className="w-full sm:w-auto px-6" leftIcon={<Activity className="w-4 h-4 text-brand-cyan" />}>
                Explore Market Terminal
              </Button>
            </a>
          </div>

          {/* Hero Centerpiece: Live Intelligence Simulator */}
          <div className="mb-12">
            <HeroIntelligenceEngine />
          </div>
        </section>

        {/* ================================================================= */}
        {/* 2. REAL FINANCIAL DATA VISUALIZATION: MARKET TERMINAL */}
        {/* ================================================================= */}
        <section id="market-terminal" className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 border-t border-border-subtle/60">
          <div className="text-center max-w-3xl mx-auto mb-10">
            <Badge variant="brand" className="mb-2 uppercase tracking-wider">
              Financial Intelligence Terminal
            </Badge>
            <h2 className="text-2xl sm:text-4xl font-extrabold text-white tracking-tight mb-3">
              Interactive Market & Signal Terminal
            </h2>
            <p className="text-slate-300 text-xs sm:text-sm">
              Explore time-series price curves with pinned SEC filing milestones, agent consensus points, and fundamental multiple bands.
            </p>
          </div>

          <MarketTerminalChart />
        </section>

        {/* ================================================================= */}
        {/* 3. RAW DATA → INTELLIGENCE TRANSFORMATION FLOW */}
        {/* ================================================================= */}
        <section id="data-flow" className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 border-t border-border-subtle/60">
          <DataTransformationFlow />
        </section>

        {/* ================================================================= */}
        {/* 4. MULTI-AGENT REASONING NETWORK */}
        {/* ================================================================= */}
        <section id="multi-agent-network" className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 border-t border-border-subtle/60">
          <MultiAgentNetworkVisual />
        </section>

        {/* ================================================================= */}
        {/* 5. PORTFOLIO ALLOCATION & RISK/RETURN MATRIX */}
        {/* ================================================================= */}
        <section id="portfolio-allocation" className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 border-t border-border-subtle/60">
          <PortfolioAllocationVisual />
        </section>

        {/* ================================================================= */}
        {/* 6. ARCHITECTURE CIRCUIT: AI REASONING VS DETERMINISTIC MATH */}
        {/* ================================================================= */}
        <section id="architecture" className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 border-t border-border-subtle/60">
          <ArchitectureCircuit />
        </section>

        {/* ================================================================= */}
        {/* 7. EVIDENCE GROUNDING DISSECTION AUDIT TRAIL */}
        {/* ================================================================= */}
        <section id="evidence-grounding" className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 border-t border-border-subtle/60">
          <EvidenceGroundingFlow />
        </section>

        {/* ================================================================= */}
        {/* 8. INTERACTIVE 6-STAGE INTELLIGENCE CONSOLE */}
        {/* ================================================================= */}
        <section id="pipeline" className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 border-t border-border-subtle/60">
          <div className="text-center max-w-3xl mx-auto mb-10">
            <Badge variant="brand" className="mb-2 uppercase tracking-wider">
              Interactive Console
            </Badge>
            <h2 className="text-2xl sm:text-4xl font-extrabold text-white tracking-tight mb-3">
              The 6-Stage Intelligence Lifecycle
            </h2>
            <p className="text-slate-400 text-xs sm:text-sm">
              Inspect each stage of AIRA's synthesis pipeline, toggle structured JSON payloads, and examine evidence extraction.
            </p>
          </div>

          {/* Console Container */}
          <GlassCard glow="brand" className="p-4 sm:p-6 lg:p-8 rounded-3xl border-border-strong bg-surface-200/85">
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
              {/* Left Column: Stage Selector Tabs */}
              <div className="lg:col-span-4 space-y-2">
                <div className="text-xs font-semibold uppercase tracking-wider text-slate-400 px-3 pb-2 flex items-center justify-between">
                  <span>Lifecycle Stages</span>
                  <Activity className="w-3.5 h-3.5 text-brand-cyan animate-pulse" />
                </div>

                {PIPELINE_STEPS.map((step) => {
                  const isActive = step.id === activeStepId;
                  const Icon = step.icon;
                  return (
                    <button
                      key={step.id}
                      onClick={() => setActiveStepId(step.id)}
                      className={`w-full text-left p-3 rounded-2xl transition-all duration-200 border flex items-start gap-3 group focus:outline-none focus-visible:ring-2 focus-visible:ring-brand-400 ${
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
                          <span className="text-[11px] font-mono font-semibold text-brand-cyan">
                            STAGE {step.stepNumber}
                          </span>
                          <span className="text-[10px] text-slate-400 uppercase tracking-wider">
                            {step.category}
                          </span>
                        </div>
                        <h3 className="text-xs sm:text-sm font-semibold truncate mt-0.5">
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
                  {/* Terminal Header & Mode Switcher */}
                  <div>
                    <div className="flex flex-wrap items-center justify-between gap-3 pb-4 mb-4 border-b border-border-subtle/80">
                      <div className="flex items-center gap-2">
                        <div className="w-3 h-3 rounded-full bg-red-500/80" />
                        <div className="w-3 h-3 rounded-full bg-yellow-500/80" />
                        <div className="w-3 h-3 rounded-full bg-green-500/80" />
                        <span className="text-xs text-slate-400 ml-2 font-mono">
                          aira-engine://pipeline/{activeStep.id}
                        </span>
                      </div>

                      {/* View Mode Switcher */}
                      <div className="flex items-center gap-1 bg-surface-200/80 p-1 rounded-lg border border-border-subtle text-[10px]">
                        <button
                          onClick={() => setConsoleViewMode('report')}
                          className={`px-2 py-1 rounded transition-all ${
                            consoleViewMode === 'report' ? 'bg-brand-500 text-white font-bold' : 'text-slate-400 hover:text-white'
                          }`}
                        >
                          Report View
                        </button>
                        <button
                          onClick={() => setConsoleViewMode('json')}
                          className={`px-2 py-1 rounded transition-all ${
                            consoleViewMode === 'json' ? 'bg-brand-500 text-white font-bold' : 'text-slate-400 hover:text-white'
                          }`}
                        >
                          Structured JSON
                        </button>
                      </div>
                    </div>

                    {/* Step Title & Description */}
                    <div className="mb-4">
                      <span className="text-xs font-semibold text-brand-cyan tracking-wider uppercase">
                        Stage {activeStep.stepNumber} — {activeStep.category}
                      </span>
                      <h4 className="text-lg font-bold text-white font-sans mt-0.5 mb-1">
                        {activeStep.title}
                      </h4>
                      <p className="text-xs text-slate-300 font-sans leading-relaxed">
                        {activeStep.description}
                      </p>
                    </div>

                    {/* Report Mode View */}
                    {consoleViewMode === 'report' && (
                      <div>
                        {/* Status Badge */}
                        <div className="mb-4 inline-flex items-center gap-2 px-3 py-1.5 rounded-lg bg-surface-200 border border-border-subtle text-xs text-brand-300">
                          <Terminal className="w-3.5 h-3.5 text-brand-cyan" />
                          <span>{activeStep.sampleOutput.status}</span>
                        </div>

                        {/* Key Metrics Grid */}
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

                        {/* Insights */}
                        {activeStep.sampleOutput.insights && (
                          <div className="space-y-2 mb-3">
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

                        {/* Evidence */}
                        {activeStep.sampleOutput.evidence && (
                          <div className="space-y-2 mb-3">
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

                        {/* Risk Vector */}
                        {activeStep.sampleOutput.riskVector && (
                          <div className="mt-3 p-3 rounded-xl bg-amber-500/10 border border-amber-500/20 text-amber-200 text-xs font-sans">
                            <span className="font-semibold text-amber-300">Risk Vector: </span>
                            {activeStep.sampleOutput.riskVector}
                          </div>
                        )}
                      </div>
                    )}

                    {/* JSON Mode View */}
                    {consoleViewMode === 'json' && (
                      <pre className="p-4 rounded-xl bg-surface-300/80 border border-border-subtle text-xs text-brand-cyan overflow-x-auto leading-relaxed">
                        {JSON.stringify(activeStep.jsonPayload, null, 2)}
                      </pre>
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
        {/* 9. FINAL CALL TO ACTION */}
        {/* ================================================================= */}
        <section id="get-started" className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 border-t border-border-subtle/60">
          <GlassCard glow="brand" className="p-8 sm:p-12 lg:p-16 rounded-3xl text-center max-w-4xl mx-auto relative overflow-hidden">
            <div className="relative z-10">
              <Badge variant="brand" className="mb-3 uppercase tracking-wider">
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
      {/* 10. FOOTER */}
      {/* ================================================================= */}
      <footer className="border-t border-border-subtle/80 bg-surface-300/60 pt-14 pb-10 text-slate-400 text-xs">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8 pb-10 border-b border-border-subtle">
            {/* Brand */}
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

            {/* Navigation */}
            <div className="space-y-2.5">
              <div className="text-xs font-semibold text-white uppercase tracking-wider">Navigation</div>
              <ul className="space-y-2">
                <li><a href="#hero" className="hover:text-slate-200 transition-colors">Live Engine</a></li>
                <li><a href="#market-terminal" className="hover:text-slate-200 transition-colors">Market Terminal</a></li>
                <li><a href="#data-flow" className="hover:text-slate-200 transition-colors">Data Pipeline</a></li>
                <li><a href="#multi-agent-network" className="hover:text-slate-200 transition-colors">Agent Network</a></li>
                <li><a href="#portfolio-allocation" className="hover:text-slate-200 transition-colors">Portfolio</a></li>
                <li><a href="#architecture" className="hover:text-slate-200 transition-colors">Architecture</a></li>
              </ul>
            </div>

            {/* Access */}
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
          <div className="pt-6 flex flex-col md:flex-row items-center justify-between gap-4 text-[11px] text-slate-500">
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
