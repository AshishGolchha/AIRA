import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { ToastProvider } from '../context/ToastContext';
import { Intelligence } from '../pages/Intelligence';
import { api } from '../lib/api';

vi.mock('../lib/api', () => ({
  api: {
    intelligence: {
      generate: vi.fn(),
      getHistory: vi.fn(),
      getReport: vi.fn(),
      deleteReport: vi.fn(),
    },
  },
}));

describe('Intelligence Page Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders intelligence history and structured report sections', async () => {
    const mockHistory = [
      {
        id: 1,
        query: 'Macro Tech Review',
        summary: 'Portfolio is well balanced with heavy AI beta.',
        symbols_analyzed: ['NVDA', 'AAPL'],
        created_at: new Date().toISOString(),
      },
    ];

    const mockReport = {
      id: 1,
      user_id: 1,
      query: 'Macro Tech Review',
      summary: 'Portfolio is well balanced with heavy AI beta.',
      portfolio_overview: 'Holdings are concentrated in enterprise software and accelerated computing.',
      portfolio_risks: ['Valuation multiple compression risk', 'Hyperscaler capex slowdown'],
      portfolio_opportunities: ['Autonomous robotics demand', 'Edge AI expansion'],
      watchlist_priorities: ['Monitor ASML lithography orders', 'Check AMD server share'],
      recommended_research: ['TSMC yield ramp', 'Arm architectural transitions'],
      portfolio_summary: {},
      facts: {},
      sources: [
        { provider: 'FinancialDataService', symbol: 'NVDA', source_type: 'Quote' },
      ],
      created_at: new Date().toISOString(),
    };

    (api.intelligence.getHistory as any).mockResolvedValueOnce({
      history: mockHistory,
      count: 1,
      total: 1,
      page: 1,
      limit: 20,
    });

    (api.intelligence.getReport as any).mockResolvedValueOnce({ report: mockReport });

    render(
      <BrowserRouter>
        <ToastProvider>
          <Intelligence />
        </ToastProvider>
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('Portfolio & Watchlist Intelligence')).toBeInTheDocument();
      expect(screen.getByText(/Valuation multiple compression risk/i)).toBeInTheDocument();
      expect(screen.getByText(/Autonomous robotics demand/i)).toBeInTheDocument();
      expect(screen.getByText(/Monitor ASML lithography orders/i)).toBeInTheDocument();
      expect(screen.getAllByText(/Macro Tech Review/i).length).toBeGreaterThan(0);
    });
  });
});
