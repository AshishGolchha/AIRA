import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { ToastProvider } from '../context/ToastContext';
import { Portfolio } from '../pages/Portfolio';
import { api } from '../lib/api';

vi.mock('../lib/api', () => ({
  api: {
    portfolio: {
      getSnapshot: vi.fn(),
      createHolding: vi.fn(),
      updateHolding: vi.fn(),
      deleteHolding: vi.fn(),
    },
  },
}));

describe('Portfolio Page Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders portfolio holdings and snapshot metrics accurately', async () => {
    const mockSnapshot = {
      holdings: [
        {
          id: 1,
          symbol: 'AAPL',
          company_name: 'Apple Inc.',
          quantity: 100,
          average_cost: 150,
          cost_basis: 15000,
          current_price: 220,
          market_value: 22000,
          unrealized_gain_loss: 7000,
          unrealized_gain_loss_percent: 46.67,
          weight_percent: 100,
        },
      ],
      holdings_count: 1,
      total_cost_basis: 15000,
      total_market_value: 22000,
      total_unrealized_gain_loss: 7000,
      total_unrealized_gain_loss_percent: 46.67,
      as_of: new Date().toISOString(),
    };

    (api.portfolio.getSnapshot as any).mockResolvedValueOnce({ snapshot: mockSnapshot });

    render(
      <BrowserRouter>
        <ToastProvider>
          <Portfolio />
        </ToastProvider>
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('Portfolio Management')).toBeInTheDocument();
      expect(screen.getByText('Apple Inc.')).toBeInTheDocument();
      expect(screen.getAllByText(/\$22,000\.00/i).length).toBeGreaterThan(0);
      expect(screen.getAllByText('AAPL').length).toBeGreaterThan(0);
    });
  });
});
