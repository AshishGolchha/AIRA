import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { ToastProvider } from '../context/ToastContext';
import { Alerts } from '../pages/Alerts';
import { api } from '../lib/api';

vi.mock('../lib/api', () => ({
  api: {
    alerts: {
      list: vi.fn(),
      get: vi.fn(),
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

  it('renders alerts and performs mark read & dismiss actions', async () => {
    const mockAlerts = [
      {
        id: 1,
        user_id: 1,
        symbol: 'NVDA',
        alert_type: 'price_move',
        severity: 'critical' as const,
        title: 'NVDA Price Spike Detected',
        message: 'Security gained +6.5% crossing volatility barrier.',
        is_read: false,
        is_dismissed: false,
        context_data: { change_percent: 6.5, volume_ratio: 2.1 },
        created_at: new Date().toISOString(),
      },
    ];

    (api.alerts.list as any).mockResolvedValue({ alerts: mockAlerts, count: 1 });
    (api.alerts.markAsRead as any).mockResolvedValue({ alert: { ...mockAlerts[0], is_read: true } });
    (api.alerts.dismiss as any).mockResolvedValue({ success: true });

    render(
      <BrowserRouter>
        <ToastProvider>
          <Alerts />
        </ToastProvider>
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('Alert Telemetry')).toBeInTheDocument();
      expect(screen.getByText('NVDA')).toBeInTheDocument();
      expect(screen.getByText('NVDA Price Spike Detected')).toBeInTheDocument();
      expect(screen.getByText('Mark Read')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText('Mark Read'));
    await waitFor(() => {
      expect(api.alerts.markAsRead).toHaveBeenCalledWith(1);
    });

    fireEvent.click(screen.getByText('Dismiss'));
    await waitFor(() => {
      expect(api.alerts.dismiss).toHaveBeenCalledWith(1);
    });
  });

  it('triggers manual alert evaluation cycle', async () => {
    (api.alerts.list as any).mockResolvedValue({ alerts: [], count: 0 });
    (api.alerts.check as any).mockResolvedValueOnce({
      evaluated_count: 5,
      created_count: 2,
      alerts: [],
    });

    render(
      <BrowserRouter>
        <ToastProvider>
          <Alerts />
        </ToastProvider>
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getAllByText('Run Alert Evaluation').length).toBeGreaterThan(0);
    });

    fireEvent.click(screen.getAllByText('Run Alert Evaluation')[0]);

    await waitFor(() => {
      expect(api.alerts.check).toHaveBeenCalled();
    });
  });
});
