import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { ToastProvider } from '../context/ToastContext';
import { Watchlist } from '../pages/Watchlist';
import { api } from '../lib/api';

vi.mock('../lib/api', () => ({
  api: {
    watchlist: {
      list: vi.fn(),
      get: vi.fn(),
      create: vi.fn(),
      update: vi.fn(),
      delete: vi.fn(),
    },
  },
}));

describe('Watchlist Page Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders watchlist items, priority tabs, and quotes correctly', async () => {
    const mockItems = [
      {
        id: 1,
        user_id: 1,
        symbol: 'NVDA',
        company_name: 'NVIDIA Corporation',
        priority: 'high' as const,
        notes: 'Monitor Blackwell ramp and gross margins',
        current_price: 135.5,
        price_change_24h_percent: 3.2,
        quote_available: true,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      },
      {
        id: 2,
        user_id: 1,
        symbol: 'AMD',
        company_name: 'Advanced Micro Devices',
        priority: 'normal' as const,
        notes: 'MI300X enterprise traction',
        current_price: 145.0,
        price_change_24h_percent: -1.5,
        quote_available: true,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      },
    ];

    (api.watchlist.list as any).mockResolvedValue({ items: mockItems, count: 2 });

    render(
      <BrowserRouter>
        <ToastProvider>
          <Watchlist />
        </ToastProvider>
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('Watchlist Intelligence')).toBeInTheDocument();
      expect(screen.getByText('NVDA')).toBeInTheDocument();
      expect(screen.getByText('AMD')).toBeInTheDocument();
      expect(screen.getByText('NVIDIA Corporation')).toBeInTheDocument();
      expect(screen.getByText(/\$135\.50/i)).toBeInTheDocument();
    });
  });

  it('handles empty watchlist state gracefully', async () => {
    (api.watchlist.list as any).mockResolvedValueOnce({ items: [], count: 0 });

    render(
      <BrowserRouter>
        <ToastProvider>
          <Watchlist />
        </ToastProvider>
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('Watchlist is Empty')).toBeInTheDocument();
    });
  });

  it('opens add ticker modal and submits new item', async () => {
    (api.watchlist.list as any).mockResolvedValue({ items: [], count: 0 });
    (api.watchlist.create as any).mockResolvedValueOnce({
      item: { id: 3, symbol: 'TSLA', priority: 'high', notes: 'Robotaxi catalysts' },
    });

    render(
      <BrowserRouter>
        <ToastProvider>
          <Watchlist />
        </ToastProvider>
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('Add Ticker')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText('Add Ticker'));
    expect(screen.getAllByText('Add to Watchlist').length).toBeGreaterThan(0);

    const input = screen.getByPlaceholderText(/e\.g\. AMD, TSLA, PLTR/i);
    fireEvent.change(input, { target: { value: 'TSLA' } });

    fireEvent.click(screen.getByRole('button', { name: 'Add to Watchlist' }));

    await waitFor(() => {
      expect(api.watchlist.create).toHaveBeenCalledWith(
        expect.objectContaining({ symbol: 'TSLA' })
      );
    });
  });
});
