import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { ToastProvider } from '../context/ToastContext';
import { Settings } from '../pages/Settings';
import { api } from '../lib/api';
import * as AuthContextModule from '../context/AuthContext';

vi.mock('../lib/api', () => ({
  api: {
    profile: {
      get: vi.fn(),
      update: vi.fn(),
    },
  },
}));

describe('Settings Page Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.spyOn(AuthContextModule, 'useAuth').mockReturnValue({
      user: { id: 1, email: 'investor@aira.internal', name: 'Alex Vance', risk_tolerance: 'moderate', alerts_enabled: true } as any,
      token: 'jwt_token',
      isAuthenticated: true,
      isLoading: false,
      login: vi.fn(),
      register: vi.fn(),
      logout: vi.fn(),
      refreshUser: vi.fn(),
    });
  });

  it('renders profile parameters and updates preferences', async () => {
    (api.profile.get as any).mockResolvedValueOnce({
      profile: {
        id: 1,
        user_id: 1,
        display_name: 'Alex Vance',
        investment_focus: 'AI Infrastructure and Semiconductor Alpha',
        risk_preference: 'moderate',
        investment_horizon: 'long_term',
      },
    });

    (api.profile.update as any).mockResolvedValueOnce({
      profile: {
        id: 1,
        user_id: 1,
        display_name: 'Alex Vance Updated',
        investment_focus: 'AI Infrastructure and Semiconductor Alpha',
        risk_preference: 'aggressive',
        investment_horizon: 'long_term',
      },
    });

    render(
      <BrowserRouter>
        <ToastProvider>
          <Settings />
        </ToastProvider>
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('Investor Profile & Preferences')).toBeInTheDocument();
      expect(screen.getByDisplayValue('Alex Vance')).toBeInTheDocument();
      expect(screen.getByDisplayValue('AI Infrastructure and Semiconductor Alpha')).toBeInTheDocument();
    });

    // Modify display name
    const nameInput = screen.getByDisplayValue('Alex Vance');
    fireEvent.change(nameInput, { target: { value: 'Alex Vance Updated' } });

    // Submit form
    fireEvent.click(screen.getByRole('button', { name: 'Save Profile Settings' }));

    await waitFor(() => {
      expect(api.profile.update).toHaveBeenCalledWith(
        expect.objectContaining({
          display_name: 'Alex Vance Updated',
        })
      );
    });
  });
});
