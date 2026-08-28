import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { ToastProvider } from '../context/ToastContext';
import { Portfolio } from '../pages/Portfolio';
import { api } from '../lib/api';

vi.mock('../lib/api', () => ({
  api: {
    portfolio: {
      listHoldings: vi.fn(),
      getHolding: vi.fn(),
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

  it('renders portfolio summary metrics and holdings table', async () => {
    const mockHoldings = [
      {
        id: 1,
        user_id: 1,
        symbol: 'NVDA',
        company_name: 'NVIDIA Corporation',
        quantity: 100,
        average_cost: 110.0,
        current_price: 130.0,
        market_value: 13000.0,
        unrealized_gain_loss: 2000.0,
        unrealized_gain_loss_percent: 18.18,
        portfolio_weight_percent: 100.0,
        notes: 'AI core holding',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      },
    ];

    const mockSnapshot = {
      user_id: 1,
      total_cost_basis: 11000.0,
      total_market_value: 13000.0,
      unrealized_gain_loss: 2000.0,
      unrealized_gain_loss_percent: 18.18,
      holdings_count: 1,
      holdings: mockHoldings,
      as_of: new Date().toISOString(),
    };

    (api.portfolio.listHoldings as any).mockResolvedValue({ holdings: mockHoldings, count: 1 });
    (api.portfolio.getSnapshot as any).mockResolvedValue({ snapshot: mockSnapshot });

    render(
      <BrowserRouter>
        <ToastProvider>
          <Portfolio />
        </ToastProvider>
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('Portfolio Management')).toBeInTheDocument();
      expect(screen.getAllByText('NVDA').length).toBeGreaterThan(0);
      expect(screen.getAllByText(/\$13,000\.00/i).length).toBeGreaterThan(0);
      expect(screen.getAllByText(/\+18\.18%/i).length).toBeGreaterThan(0);
    });
  });

  it('opens add position modal and creates a holding', async () => {
    (api.portfolio.listHoldings as any).mockResolvedValue({ holdings: [], count: 0 });
    (api.portfolio.getSnapshot as any).mockResolvedValue({
      snapshot: {
        user_id: 1,
        total_cost_basis: 0,
        total_market_value: 0,
        unrealized_gain_loss: 0,
        unrealized_gain_loss_percent: 0,
        holdings_count: 0,
        holdings: [],
        as_of: new Date().toISOString(),
      },
    });
    (api.portfolio.createHolding as any).mockResolvedValueOnce({
      holding: { id: 2, symbol: 'MSFT', quantity: 50, average_cost: 400.0 },
    });

    render(
      <BrowserRouter>
        <ToastProvider>
          <Portfolio />
        </ToastProvider>
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('Add Position')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText('Add Position'));
    expect(screen.getByText('Add Portfolio Position')).toBeInTheDocument();

    fireEvent.change(screen.getByPlaceholderText(/e\.g\. NVDA, AAPL, MSFT/i), { target: { value: 'MSFT' } });
    fireEvent.change(screen.getByPlaceholderText('10.5'), { target: { value: '50' } });
    fireEvent.change(screen.getByPlaceholderText('120.00'), { target: { value: '400' } });

    const submitBtns = screen.getAllByRole('button', { name: 'Add Position' });
    fireEvent.click(submitBtns[submitBtns.length - 1]);

    await waitFor(() => {
      expect(api.portfolio.createHolding).toHaveBeenCalledWith(
        expect.objectContaining({
          symbol: 'MSFT',
          quantity: 50,
          average_cost: 400,
        })
      );
    });
  });
});
