import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { AuthProvider } from '../context/AuthContext';
import { ToastProvider } from '../context/ToastContext';
import { Login } from '../pages/Login';
import { Register } from '../pages/Register';
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

describe('AuthContext, Login, and Register Components', () => {
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
      name: 'Alex Vance',
      risk_tolerance: 'moderate',
      alerts_enabled: true,
      created_at: new Date().toISOString(),
    };

    (api.auth.login as any).mockResolvedValueOnce({
      access_token: 'fake_jwt_token_12345',
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

    const emailInput = screen.getByLabelText(/email address/i);
    const passwordInput = screen.getByLabelText(/password/i);
    const submitBtn = screen.getByRole('button', { name: /sign in to platform/i });

    fireEvent.change(emailInput, { target: { value: 'investor@aira.internal' } });
    fireEvent.change(passwordInput, { target: { value: 'SecretPassword123!' } });
    fireEvent.click(submitBtn);

    await waitFor(() => {
      expect(api.auth.login).toHaveBeenCalledWith({
        email: 'investor@aira.internal',
        password: 'SecretPassword123!',
      });
      expect(localStorage.getItem('aira_auth_token')).toBe('fake_jwt_token_12345');
      expect(localStorage.getItem('aira_user')).toContain('investor@aira.internal');
    });
  });

  it('displays error message on failed login attempt', async () => {
    (api.auth.login as any).mockRejectedValueOnce(new Error('Invalid email or password.'));

    render(
      <BrowserRouter>
        <ToastProvider>
          <AuthProvider>
            <Login />
          </AuthProvider>
        </ToastProvider>
      </BrowserRouter>
    );

    fireEvent.change(screen.getByLabelText(/email address/i), { target: { value: 'wrong@aira.internal' } });
    fireEvent.change(screen.getByLabelText(/password/i), { target: { value: 'wrongpass' } });
    fireEvent.click(screen.getByRole('button', { name: /sign in to platform/i }));

    await waitFor(() => {
      expect(screen.getByText('Invalid email or password.')).toBeInTheDocument();
    });
  });

  it('submits registration payload and logs in user', async () => {
    const mockUser = {
      id: 2,
      email: 'newuser@aira.internal',
      name: 'New Investor',
      risk_tolerance: 'moderate',
      alerts_enabled: true,
      created_at: new Date().toISOString(),
    };

    (api.auth.register as any).mockResolvedValueOnce({
      access_token: 'new_user_token_999',
      user: mockUser,
    });

    render(
      <BrowserRouter>
        <ToastProvider>
          <AuthProvider>
            <Register />
          </AuthProvider>
        </ToastProvider>
      </BrowserRouter>
    );

    fireEvent.change(screen.getByLabelText(/full name/i), { target: { value: 'New Investor' } });
    fireEvent.change(screen.getByLabelText(/email address/i), { target: { value: 'newuser@aira.internal' } });
    fireEvent.change(screen.getByLabelText(/password/i), { target: { value: 'SecurePass888!' } });

    fireEvent.click(screen.getByRole('button', { name: /get started free/i }));

    await waitFor(() => {
      expect(api.auth.register).toHaveBeenCalledWith({
        email: 'newuser@aira.internal',
        password: 'SecurePass888!',
        display_name: 'New Investor',
      });
      expect(localStorage.getItem('aira_auth_token')).toBe('new_user_token_999');
    });
  });
});
