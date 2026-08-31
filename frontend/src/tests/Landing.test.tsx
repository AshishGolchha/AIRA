import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { Landing } from '../pages/Landing';
import * as AuthContextModule from '../context/AuthContext';

describe('Landing Page Component & Public Experience', () => {
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

    // Problem and Architecture sections
    expect(screen.getByText(/The AIRA Engine/i)).toBeInTheDocument();
    expect(screen.getByText(/Deterministic Math Meets Autonomous AI/i)).toBeInTheDocument();

    // Disclaimer
    expect(screen.getByText(/AIRA is an autonomous investment research intelligence/i)).toBeInTheDocument();
  });

  it('allows switching interactive intelligence console stages', () => {
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
    expect(screen.getByText(/Target Ingested: NVDA/i)).toBeInTheDocument();

    // Click Stage 2: Deterministic Portfolio Valuation
    const stage2Btn = screen.getByRole('button', { name: /Deterministic Portfolio Valuation/i });
    fireEvent.click(stage2Btn);

    expect(screen.getAllByText(/Portfolio Snapshot Computed/i).length).toBeGreaterThan(0);
    expect(screen.getByText(/\$125,000.00/i)).toBeInTheDocument();

    // Click Stage 3: Multi-Agent AI Synthesis
    const stage3Btn = screen.getByRole('button', { name: /Multi-Agent AI Synthesis/i });
    fireEvent.click(stage3Btn);

    expect(screen.getAllByText(/Multi-Agent Consensus Synthesized/i).length).toBeGreaterThan(0);
  });

  it('renders "Open Dashboard" CTA when user is already authenticated', () => {
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

    const dashboardBtns = screen.getAllByText(/Open Dashboard/i);
    expect(dashboardBtns.length).toBeGreaterThan(0);
  });
});
