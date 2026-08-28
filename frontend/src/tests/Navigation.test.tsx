import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { AppLayout } from '../components/layout/AppLayout';
import * as AuthContextModule from '../context/AuthContext';

describe('AppLayout, Sidebar, and Navbar Navigation', () => {
  const mockLogout = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
    vi.spyOn(AuthContextModule, 'useAuth').mockReturnValue({
      user: {
        id: 1,
        email: 'investor@aira.internal',
        name: 'Alex Vance',
        profile: { display_name: 'Alex Vance' },
        risk_tolerance: 'moderate',
        alerts_enabled: true,
      } as any,
      token: 'jwt_token',
      isAuthenticated: true,
      isLoading: false,
      login: vi.fn(),
      register: vi.fn(),
      logout: mockLogout,
      refreshUser: vi.fn(),
    });
  });

  it('renders sidebar navigation links and brand banner', () => {
    render(
      <BrowserRouter>
        <AppLayout />
      </BrowserRouter>
    );

    expect(screen.getAllByText('AIRA').length).toBeGreaterThan(0);
    expect(screen.getAllByText('Dashboard').length).toBeGreaterThan(0);
    expect(screen.getAllByText('Portfolio').length).toBeGreaterThan(0);
    expect(screen.getAllByText('Watchlist').length).toBeGreaterThan(0);
    expect(screen.getAllByText('Alerts').length).toBeGreaterThan(0);
    expect(screen.getAllByText('Intelligence').length).toBeGreaterThan(0);
    expect(screen.getAllByText('Research').length).toBeGreaterThan(0);
    expect(screen.getAllByText('Notifications').length).toBeGreaterThan(0);
    expect(screen.getAllByText('Settings').length).toBeGreaterThan(0);
  });

  it('renders navbar user profile and triggers sign out', () => {
    render(
      <BrowserRouter>
        <AppLayout />
      </BrowserRouter>
    );

    expect(screen.getByText(/AI Core Active/i)).toBeInTheDocument();
    expect(screen.getByText('Run AI Analysis')).toBeInTheDocument();

    // Click user dropdown in navbar
    const userBtns = screen.getAllByText('Alex Vance');
    fireEvent.click(userBtns[userBtns.length - 1]);

    expect(screen.getByText('Account Settings')).toBeInTheDocument();
    expect(screen.getByText('Sign Out')).toBeInTheDocument();

    fireEvent.click(screen.getByText('Sign Out'));
    expect(mockLogout).toHaveBeenCalled();
  });
});
