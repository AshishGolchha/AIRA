import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { Landing } from '../pages/Landing';
import * as AuthContextModule from '../context/AuthContext';

describe('Landing Page Component & Premium Product Story', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders landing page with main headline, CTA buttons, and trust strip when unauthenticated', () => {
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

    // Trust strip items
    expect(screen.getAllByText(/Multi-Agent Synthesis/i).length).toBeGreaterThan(0);
    expect(screen.getAllByText(/Real-Time Portfolio/i).length).toBeGreaterThan(0);
    expect(screen.getAllByText(/Deterministic Alerts/i).length).toBeGreaterThan(0);
    expect(screen.getAllByText(/Vector Memory/i).length).toBeGreaterThan(0);

    // Architecture section
    expect(screen.getByText(/Why AIRA Is Not "ChatGPT for Stocks"/i)).toBeInTheDocument();
    expect(screen.getByText(/Autonomous Consensus Through Specialized Agent Debate/i)).toBeInTheDocument();

    // Disclaimer
    expect(screen.getByText(/AIRA is an autonomous investment research intelligence/i)).toBeInTheDocument();
  });

  it('allows interactive ticker switching in Hero Intelligence Engine', () => {
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

    // Default ticker is NVDA
    expect(screen.getByText(/NVIDIA Corporation/i)).toBeInTheDocument();
    expect(screen.getByText(/Data Center compute segment revenue/i)).toBeInTheDocument();

    // Switch to AAPL
    const aaplBtn = screen.getByRole('button', { name: /\$AAPL/i });
    fireEvent.click(aaplBtn);

    expect(screen.getByText(/Apple Inc\./i)).toBeInTheDocument();
    expect(screen.getByText(/Installed base surpassed 2\.2 billion/i)).toBeInTheDocument();

    // Switch to MSFT
    const msftBtn = screen.getByRole('button', { name: /\$MSFT/i });
    fireEvent.click(msftBtn);

    expect(screen.getByText(/Microsoft Corporation/i)).toBeInTheDocument();
    expect(screen.getByText(/Azure Cloud revenue growth \+29%/i)).toBeInTheDocument();
  });

  it('allows interactive inspection in ArchitectureCircuit and MultiAgentDebate', () => {
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

    // In Architecture circuit: click Portfolio Valuation Math
    const mathBtn = screen.getByRole('button', { name: /Portfolio Valuation Math/i });
    fireEvent.click(mathBtn);
    expect(screen.getByText(/Zero LLM participation in mathematical calculations/i)).toBeInTheDocument();

    // In Multi-Agent Debate: click Agent 1
    const agent1Btn = screen.getByRole('button', { name: /Agent 1/i });
    fireEvent.click(agent1Btn);
    expect(screen.getByText(/Senior Equity Analyst/i)).toBeInTheDocument();
  });

  it('allows switching intelligence console stages and toggling JSON view mode', () => {
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

    // Default stage 1 should be visible
    expect(screen.getAllByText(/Multi-Source Discovery/i).length).toBeGreaterThan(0);

    // Click Stage 2: Deterministic Portfolio Valuation
    const stage2Btn = screen.getByRole('button', { name: /Deterministic Portfolio Valuation/i });
    fireEvent.click(stage2Btn);

    expect(screen.getAllByText(/Portfolio Snapshot Computed/i).length).toBeGreaterThan(0);

    // Toggle Structured JSON mode
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
