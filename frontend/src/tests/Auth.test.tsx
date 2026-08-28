import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { AuthProvider } from '../context/AuthContext';
import { ToastProvider } from '../context/ToastContext';
import { Login } from '../pages/Login';
import { api } from '../lib/api';

vi.mock('../lib/api', () => ({
  api: {
    auth: {
      login: vi.fn(),
      register: vi.fn(),
      getMe: vi.fn(),
    },
  },
}));

describe('AuthContext and Login Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
  });

  it('renders login form properly with inputs and submit button', () => {
    render(
      <BrowserRouter>
        <ToastProvider>
          <AuthProvider>
            <Login />
          </AuthProvider>
        </ToastProvider>
      </BrowserRouter>
    );

    expect(screen.getByLabelText(/email address/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /sign in to platform/i })).toBeInTheDocument();
  });

  it('submits login payload and persists token to localStorage', async () => {
    const mockUser = {
      id: 1,
      email: 'investor@aira.internal',
      is_active: true,
      alerts_enabled: true,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      profile: {
        id: 1,
        display_name: 'Test Investor',
        investment_focus: 'Tech',
        risk_preference: 'moderate',
        investment_horizon: 'long_term',
      },
    };

    (api.auth.login as any).mockResolvedValueOnce({
      access_token: 'mock-jwt-token-123',
      token_type: 'Bearer',
      user: mockUser,
    });

    render(
      <BrowserRouter>
        <ToastProvider>
          <AuthProvider>
            <Login />
          </AuthProvider>
        </ToastProvider>
      </BrowserRouter>
    );

    fireEvent.change(screen.getByLabelText(/email address/i), {
      target: { value: 'investor@aira.internal' },
    });
    fireEvent.change(screen.getByLabelText(/password/i), {
      target: { value: 'Secret123!' },
    });

    fireEvent.click(screen.getByRole('button', { name: /sign in to platform/i }));

    await waitFor(() => {
      expect(api.auth.login).toHaveBeenCalledWith({
        email: 'investor@aira.internal',
        password: 'Secret123!',
      });
      expect(localStorage.getItem('aira_auth_token')).toBe('mock-jwt-token-123');
    });
  });
});
