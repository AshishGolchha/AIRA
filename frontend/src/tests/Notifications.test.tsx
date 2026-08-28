import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
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
      updateEndpoint: vi.fn(),
      deleteEndpoint: vi.fn(),
      listDeliveries: vi.fn(),
    },
  },
}));

describe('Notifications Page Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders preferences, webhook endpoints, and delivery history', async () => {
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
        channel: 'webhook' as const,
        endpoint_url: 'https://api.internal.com/hooks/aira',
        is_enabled: true,
        created_at: new Date().toISOString(),
      },
    ];

    const mockDeliveries = [
      {
        id: 1,
        user_id: 1,
        alert_id: 10,
        channel: 'in_app' as const,
        status: 'delivered' as const,
        attempt_count: 1,
        error_message: null,
        created_at: new Date().toISOString(),
      },
    ];

    (api.notifications.getPreferences as any).mockResolvedValue({ preferences: mockPreferences });
    (api.notifications.listEndpoints as any).mockResolvedValue({ endpoints: mockEndpoints });
    (api.notifications.listDeliveries as any).mockResolvedValue({ deliveries: mockDeliveries, count: 1 });
    (api.notifications.updatePreferences as any).mockResolvedValue({
      preferences: { ...mockPreferences, email_enabled: false },
    });

    render(
      <BrowserRouter>
        <ToastProvider>
          <Notifications />
        </ToastProvider>
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('Notification Channels & Telemetry')).toBeInTheDocument();
      expect(screen.getByText('https://api.internal.com/hooks/aira')).toBeInTheDocument();
      expect(screen.getByText('#10')).toBeInTheDocument();
    });

    // Save preferences
    fireEvent.click(screen.getByRole('button', { name: /save notification preferences/i }));

    await waitFor(() => {
      expect(api.notifications.updatePreferences).toHaveBeenCalled();
    });
  });

  it('opens modal and creates a webhook endpoint', async () => {
    (api.notifications.getPreferences as any).mockResolvedValue({
      preferences: {
        id: 1,
        user_id: 1,
        in_app_enabled: true,
        email_enabled: true,
        webhook_enabled: true,
        minimum_severity: 'info',
        alert_types: ['price_move'],
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      },
    });
    (api.notifications.listEndpoints as any).mockResolvedValue({ endpoints: [] });
    (api.notifications.listDeliveries as any).mockResolvedValue({ deliveries: [], count: 0 });
    (api.notifications.createEndpoint as any).mockResolvedValueOnce({
      endpoint: { id: 2, endpoint_url: 'https://secure.aira.internal/hook', is_enabled: true },
    });

    render(
      <BrowserRouter>
        <ToastProvider>
          <Notifications />
        </ToastProvider>
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('Add Webhook')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText('Add Webhook'));
    expect(screen.getByText('Configure Webhook Endpoint')).toBeInTheDocument();

    fireEvent.change(screen.getByPlaceholderText('https://api.domain.com/v1/webhook'), {
      target: { value: 'https://secure.aira.internal/hook' },
    });

    fireEvent.click(screen.getByRole('button', { name: 'Register Webhook' }));

    await waitFor(() => {
      expect(api.notifications.createEndpoint).toHaveBeenCalledWith(
        expect.objectContaining({
          endpoint_url: 'https://secure.aira.internal/hook',
        })
      );
    });
  });
});
