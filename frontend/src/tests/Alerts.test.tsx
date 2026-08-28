import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { ToastProvider } from '../context/ToastContext';
import { Alerts } from '../pages/Alerts';
import { api } from '../lib/api';

vi.mock('../lib/api', () => ({
  api: {
    alerts: {
      list: vi.fn(),
      check: vi.fn(),
      markAsRead: vi.fn(),
      dismiss: vi.fn(),
    },
  },
}));

describe('Alerts Page Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders alerts stream and severity indicators', async () => {
    const mockAlerts = [
      {
        id: 101,
        user_id: 1,
        symbol: 'TSLA',
        alert_type: 'price_move' as const,
        severity: 'critical' as const,
        title: 'TSLA Price Plunge -8.4%',
        message: 'Security TSLA experienced a sudden drop exceeding the 8% risk threshold.',
        is_read: false,
        is_dismissed: false,
        context_data: { threshold: 8.0, current_drop: 8.4 },
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      },
    ];

    (api.alerts.list as any).mockResolvedValueOnce({
      alerts: mockAlerts,
      count: 1,
      total: 1,
      page: 1,
      limit: 20,
    });

    render(
      <BrowserRouter>
        <ToastProvider>
          <Alerts />
        </ToastProvider>
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('Alert Telemetry')).toBeInTheDocument();
      expect(screen.getByText('TSLA Price Plunge -8.4%')).toBeInTheDocument();
      expect(screen.getAllByText('TSLA').length).toBeGreaterThan(0);
      expect(screen.getAllByText(/Critical/i).length).toBeGreaterThan(0);
    });
  });
});
