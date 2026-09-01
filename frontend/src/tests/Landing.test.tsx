import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { Landing } from '../pages/Landing';
import * as AuthContextModule from '../context/AuthContext';

describe('Landing Page Component & Phase 20C Cinematic Data Storytelling', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders landing page with main headline, CTA buttons, and interactive visual sections', () => {
    vi.spyOn(AuthContextModule, 'useAuth').mockReturnValue({
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: false,
      login: vi.fn(),
      register: vi.fn(),
      logout: vi.fn(),
      refreshUser: vi.fn(),
    });

    render(
      <BrowserRouter>
        <Landing />
      </BrowserRouter>
    );

    // H1 Heading
    expect(screen.getByRole('heading', { level: 1 })).toBeInTheDocument();
    expect(screen.getByText(/Your Investment Research/i)).toBeInTheDocument();
    expect(screen.getByText(/Running on Autonomous Intelligence/i)).toBeInTheDocument();

    // CTA buttons
    const getStartedBtns = screen.getAllByText(/Get Started/i);
    expect(getStartedBtns.length).toBeGreaterThan(0);

    const signInBtns = screen.getAllByText(/Sign In/i);
    expect(signInBtns.length).toBeGreaterThan(0);

    // Section Titles
    expect(screen.getByText(/Interactive Market & Signal Terminal/i)).toBeInTheDocument();
    expect(screen.getByText(/From Chaotic Market Noise to Grounded Intelligence/i)).toBeInTheDocument();
    expect(screen.getByText(/Specialized Agents Debate Evidence Before Synthesizing Consensus/i)).toBeInTheDocument();
    expect(screen.getByText(/Research Is Grounded in Your Exact Portfolio Weights/i)).toBeInTheDocument();
    expect(screen.getByText(/Every Thesis Claim Maps to a Verifiable Source Filing/i)).toBeInTheDocument();
    expect(screen.getByText(/Why AIRA Is Not "ChatGPT for Stocks"/i)).toBeInTheDocument();

    // Disclaimer
    expect(screen.getByText(/AIRA is an autonomous investment research intelligence/i)).toBeInTheDocument();
  });

  it('allows interactive ticker switching in MarketTerminalChart', () => {
    vi.spyOn(AuthContextModule, 'useAuth').mockReturnValue({
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: false,
      login: vi.fn(),
      register: vi.fn(),
      logout: vi.fn(),
      refreshUser: vi.fn(),
    });

    render(
      <BrowserRouter>
        <Landing />
      </BrowserRouter>
    );

    // Default ticker in Market Terminal is NVDA
    expect(screen.getAllByText(/NVIDIA Corp/i).length).toBeGreaterThan(0);

    // Switch to $AAPL
    const aaplBtns = screen.getAllByRole('button', { name: /\$AAPL/i });
    fireEvent.click(aaplBtns[0]);
    expect(screen.getAllByText(/Apple Inc/i).length).toBeGreaterThan(0);

    // Switch to $MSFT
    const msftBtns = screen.getAllByRole('button', { name: /\$MSFT/i });
    fireEvent.click(msftBtns[0]);
    expect(screen.getAllByText(/Microsoft Corp/i).length).toBeGreaterThan(0);
  });

  it('allows switching views in PortfolioAllocationVisual and MultiAgentNetworkVisual', () => {
    vi.spyOn(AuthContextModule, 'useAuth').mockReturnValue({
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: false,
      login: vi.fn(),
      register: vi.fn(),
      logout: vi.fn(),
      refreshUser: vi.fn(),
    });

    render(
      <BrowserRouter>
        <Landing />
      </BrowserRouter>
    );

    // In Portfolio visual: switch to Risk vs Return
    const scatterBtn = screen.getByRole('button', { name: /Risk vs Return/i });
    fireEvent.click(scatterBtn);
    expect(screen.getByText(/Annualized Volatility/i)).toBeInTheDocument();

    // In Portfolio visual: switch to Telemetry Drawdown
    const drawdownBtn = screen.getByRole('button', { name: /Telemetry Drawdown/i });
    fireEvent.click(drawdownBtn);
    expect(screen.getByText(/Continuous Equity Curve Telemetry/i)).toBeInTheDocument();

    // In Multi-Agent visual: switch to Active Debate Nodes
    const debateBtn = screen.getByRole('button', { name: /Active Debate Nodes/i });
    fireEvent.click(debateBtn);
    expect(screen.getByText(/Consensus requires cross-validation/i)).toBeInTheDocument();
  });

  it('allows switching raw signal inputs in DataTransformationFlow', () => {
    vi.spyOn(AuthContextModule, 'useAuth').mockReturnValue({
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: false,
      login: vi.fn(),
      register: vi.fn(),
      logout: vi.fn(),
      refreshUser: vi.fn(),
    });

    render(
      <BrowserRouter>
        <Landing />
      </BrowserRouter>
    );

    // Click Position Weighting signal
    const posSignalBtn = screen.getByRole('button', { name: /Position Weighting/i });
    fireEvent.click(posSignalBtn);
    expect(screen.getByText(/Represents 22\.4% of total equity allocation/i)).toBeInTheDocument();
  });

  it('allows switching intelligence console stages and toggling JSON mode', () => {
    vi.spyOn(AuthContextModule, 'useAuth').mockReturnValue({
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: false,
      login: vi.fn(),
      register: vi.fn(),
      logout: vi.fn(),
      refreshUser: vi.fn(),
    });

    render(
      <BrowserRouter>
        <Landing />
      </BrowserRouter>
    );

    // Stage 1
    expect(screen.getAllByText(/Multi-Source Discovery/i).length).toBeGreaterThan(0);

    // Stage 2
    const stage2Btn = screen.getByRole('button', { name: /Deterministic Portfolio Valuation/i });
    fireEvent.click(stage2Btn);
    expect(screen.getAllByText(/Portfolio Snapshot Computed/i).length).toBeGreaterThan(0);

    // JSON Toggle
    const jsonToggleBtn = screen.getByRole('button', { name: /Structured JSON/i });
    fireEvent.click(jsonToggleBtn);
    expect(screen.getByText(/"valuation_engine": "DETERMINISTIC_SQL"/i)).toBeInTheDocument();
  });

  it('renders "Open Dashboard" CTA when user is authenticated', () => {
    vi.spyOn(AuthContextModule, 'useAuth').mockReturnValue({
      user: {
        id: 1,
        email: 'investor@aira.internal',
        name: 'Alex Vance',
        profile: { display_name: 'Alex Vance' },
      } as any,
      token: 'jwt_token',
      isAuthenticated: true,
      isLoading: false,
      login: vi.fn(),
      register: vi.fn(),
      logout: vi.fn(),
      refreshUser: vi.fn(),
    });

    render(
      <BrowserRouter>
        <Landing />
      </BrowserRouter>
    );

    const dashboardBtns = screen.getAllByText(/Open (Investor )?Dashboard/i);
    expect(dashboardBtns.length).toBeGreaterThan(0);
  });
});
