import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { ToastProvider } from '../context/ToastContext';
import { Notifications } from '../pages/Notifications';
import { api } from '../lib/api';

vi.mock('../lib/api', () => ({
  api: {
    notifications: {
      getPreferences: vi.fn(),
      updatePreferences: vi.fn(),
      listEndpoints: vi.fn(),
      createEndpoint: vi.fn(),
      deleteEndpoint: vi.fn(),
      listDeliveries: vi.fn(),
    },
  },
}));

describe('Notifications Page Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders notification channel preferences and webhook endpoints', async () => {
    const mockPreferences = {
      id: 1,
      user_id: 1,
      in_app_enabled: true,
      email_enabled: true,
      webhook_enabled: false,
      minimum_severity: 'warning',
      alert_types: ['price_move', 'portfolio_gain_loss'],
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };

    const mockEndpoints = [
      {
        id: 1,
        user_id: 1,
        endpoint_url: 'https://webhook.site/aira-alerts',
        channel: 'webhook',
        is_enabled: true,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      },
    ];

    const mockDeliveries = [
      {
        id: 1,
        alert_id: 42,
        user_id: 1,
        channel: 'in_app' as const,
        status: 'delivered' as const,
        attempt_count: 1,
        created_at: new Date().toISOString(),
      },
    ];

    (api.notifications.getPreferences as any).mockResolvedValueOnce({ preferences: mockPreferences });
    (api.notifications.listEndpoints as any).mockResolvedValueOnce({ endpoints: mockEndpoints });
    (api.notifications.listDeliveries as any).mockResolvedValueOnce({ deliveries: mockDeliveries });

    render(
      <BrowserRouter>
        <ToastProvider>
          <Notifications />
        </ToastProvider>
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('In-App Notification Stream')).toBeInTheDocument();
      expect(screen.getByText('https://webhook.site/aira-alerts')).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /save notification preferences/i })).toBeInTheDocument();
    });
  });
});
