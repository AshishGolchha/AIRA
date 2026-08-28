import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { ToastProvider } from '../context/ToastContext';
import { Dashboard } from '../pages/Dashboard';
import { api } from '../lib/api';

vi.mock('../lib/api', () => ({
  api: {
    dashboard: {
      get: vi.fn(),
    },
  },
}));

describe('Dashboard Page Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders dashboard metrics, holdings, and persisted intelligence', async () => {
    const mockDashboardData = {
      user: {
        id: 1,
        email: 'investor@aira.internal',
        name: 'Alex Vance',
        investment_focus: 'Semiconductors',
        risk_tolerance: 'moderate',
        investment_horizon: 'long_term',
      },
      portfolio: {
        total_market_value: 125000.5,
        total_cost_basis: 100000.0,
        unrealized_gain_loss: 25000.5,
        unrealized_gain_loss_percent: 25.0,
        holdings_count: 2,
        top_holdings: [
          {
            id: 1,
            symbol: 'NVDA',
            company_name: 'NVIDIA Corporation',
            quantity: 500,
            average_cost: 100,
            cost_basis: 50000,
            current_price: 130,
            market_value: 65000,
            unrealized_gain_loss: 15000,
            unrealized_gain_loss_percent: 30.0,
            weight_percent: 52.0,
          },
        ],
      },
      watchlist: {
        total_count: 3,
        high_priority_count: 1,
        normal_priority_count: 2,
        low_priority_count: 0,
        items: [
          {
            id: 1,
            user_id: 1,
            symbol: 'MSFT',
            current_price: 420.5,
            priority: 'high' as const,
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
          },
        ],
      },
      alerts: {
        unread_count: 1,
        critical_count: 0,
        warning_count: 1,
        info_count: 0,
        recent: [
          {
            id: 1,
            user_id: 1,
            symbol: 'NVDA',
            alert_type: 'price_move' as const,
            severity: 'warning' as const,
            title: 'NVDA +5% Move',
            message: 'Price moved up by 5.2% in 24h',
            is_read: false,
            is_dismissed: false,
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
          },
        ],
      },
      research: {
        total_reports: 5,
        recent: [],
      },
      notifications: {
        preferences: {
          in_app_enabled: true,
          email_enabled: true,
          webhook_enabled: false,
          minimum_severity: 'info',
          alert_types: ['price_move'],
        },
        enabled_channels: ['in_app', 'email'],
        pending_retry_count: 0,
        failed_delivery_count: 0,
        delivered_count: 12,
      },
      monitoring: {
        system_monitoring_enabled: true,
        user_alerts_enabled: true,
        latest_run: {
          id: 10,
          status: 'success',
          started_at: new Date().toISOString(),
          completed_at: new Date().toISOString(),
          duration_seconds: 1.45,
        },
      },
      portfolio_intelligence: {
        available: true,
        latest: {
          id: 42,
          summary: 'Portfolio exhibits strong semiconductor exposure with solid cash cushion.',
          symbols_analyzed: ['NVDA', 'MSFT'],
          created_at: new Date().toISOString(),
        },
      },
    };

    (api.dashboard.get as any).mockResolvedValueOnce(mockDashboardData);

    render(
      <BrowserRouter>
        <ToastProvider>
          <Dashboard />
        </ToastProvider>
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText(/Alex Vance/i)).toBeInTheDocument();
      expect(screen.getByText(/\$125,000\.50/i)).toBeInTheDocument();
      expect(screen.getAllByText('NVDA').length).toBeGreaterThan(0);
      expect(screen.getByText(/Portfolio exhibits strong semiconductor exposure/i)).toBeInTheDocument();
    });
  });
});
