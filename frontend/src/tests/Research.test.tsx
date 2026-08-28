import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { ToastProvider } from '../context/ToastContext';
import { Research } from '../pages/Research';
import { api } from '../lib/api';

vi.mock('../lib/api', () => ({
  api: {
    research: {
      search: vi.fn(),
      analyze: vi.fn(),
      getHistory: vi.fn(),
      getReport: vi.fn(),
      deleteReport: vi.fn(),
      getCompanyProfile: vi.fn(),
      getQuote: vi.fn(),
      getMetrics: vi.fn(),
      getNews: vi.fn(),
    },
  },
}));

describe('Research Page Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders research page, historical reports and searches security', async () => {
    const mockHistory = [
      {
        id: 1,
        symbol: 'NVDA',
        company: 'NVIDIA Corporation',
        query: 'Datacenter moat evaluation',
        summary: 'Dominant GPU architecture and CUDA ecosystem advantages.',
        created_at: new Date().toISOString(),
      },
    ];

    (api.research.getHistory as any).mockResolvedValue({ history: mockHistory, count: 1 });
    (api.research.getReport as any).mockResolvedValue({
      report: {
        id: 1,
        symbol: 'NVDA',
        company: 'NVIDIA Corporation',
        query: 'Datacenter moat evaluation',
        summary: 'Dominant GPU architecture and CUDA ecosystem advantages.',
        risks: ['Margin compression'],
        opportunities: ['Software enterprise growth'],
        sources: [],
        created_at: new Date().toISOString(),
      },
    });
    (api.research.search as any).mockResolvedValue({
      results: [{ symbol: 'NVDA', name: 'NVIDIA Corporation', exchange: 'NASDAQ' }],
      count: 1,
    });
    (api.research.getCompanyProfile as any).mockResolvedValue({
      profile: { symbol: 'NVDA', name: 'NVIDIA Corporation', sector: 'Technology', industry: 'Semiconductors', description: 'Pioneered GPU-accelerated computing.' },
    });
    (api.research.getQuote as any).mockResolvedValue({
      quote: { symbol: 'NVDA', current_price: 130.0, day_change_percent: 2.5, day_high: 132.0, day_low: 128.0, volume: 45000000 },
    });
    (api.research.getMetrics as any).mockResolvedValue({
      metrics: { symbol: 'NVDA', pe_ratio: 42.5, forward_pe: 31.2, price_to_book: 25.0, beta: 1.65, dividend_yield: 0.02, eps: 3.1 },
    });
    (api.research.getNews as any).mockResolvedValue({
      news: [{ title: 'NVIDIA Expands AI Enterprise Platform', publisher: 'Reuters', link: 'https://reuters.com/news', publish_time: '2 hours ago' }],
      count: 1,
    });

    render(
      <BrowserRouter>
        <ToastProvider>
          <Research />
        </ToastProvider>
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('Autonomous Equity Research')).toBeInTheDocument();
      expect(screen.getAllByText(/Dominant GPU architecture/i).length).toBeGreaterThan(0);
    });

    // Perform security search
    const searchInput = screen.getByPlaceholderText(/Search ticker or company name/i);
    fireEvent.change(searchInput, { target: { value: 'NVDA' } });
    fireEvent.submit(searchInput.closest('form')!);

    await waitFor(() => {
      expect(api.research.search).toHaveBeenCalledWith('NVDA');
    });
  });

  it('triggers autonomous deep research analysis', async () => {
    (api.research.getHistory as any).mockResolvedValue({ history: [], count: 0 });
    (api.research.analyze as any).mockResolvedValueOnce({
      report: {
        id: 10,
        symbol: 'AAPL',
        company: 'Apple Inc.',
        query: 'Ecosystem lock-in',
        summary: 'Services segment growth provides high-margin recurring cash flow.',
        fundamentals: 'Robust balance sheet with strong free cash flow generation.',
        valuation: 'Trading at reasonable premium given capital returns.',
        risks: ['Antitrust regulatory pressure', 'Lengthening smartphone upgrade cycle'],
        opportunities: ['Services expansion', 'Spatial computing ramp'],
        sources: [{ symbol: 'AAPL', provider: 'YFinance', source_type: 'Financials' }],
        created_at: new Date().toISOString(),
      },
    });

    render(
      <BrowserRouter>
        <ToastProvider>
          <Research />
        </ToastProvider>
      </BrowserRouter>
    );

    const searchInput = screen.getByPlaceholderText(/Search ticker or company name/i);
    fireEvent.change(searchInput, { target: { value: 'AAPL' } });

    fireEvent.click(screen.getByRole('button', { name: 'Run Autonomous Research' }));

    await waitFor(() => {
      expect(api.research.analyze).toHaveBeenCalledWith(
        expect.objectContaining({ symbol: 'AAPL' })
      );
      expect(screen.getByText(/Services segment growth provides high-margin/i)).toBeInTheDocument();
      expect(screen.getByText(/Antitrust regulatory pressure/i)).toBeInTheDocument();
    });
  });
});
