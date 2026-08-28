import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
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

  it('renders intelligence history and loads report detail', async () => {
    const mockHistory = [
      {
        id: 1,
        query: 'Rate risk and concentration',
        summary: 'Portfolio is well-diversified with low fixed-income vulnerability.',
        symbols_analyzed: ['NVDA', 'AAPL'],
        created_at: new Date().toISOString(),
      },
    ];

    const mockReport = {
      id: 1,
      user_id: 1,
      query: 'Rate risk and concentration',
      summary: 'Portfolio is well-diversified with low fixed-income vulnerability.',
      portfolio_overview: 'Holdings allocated across growth tech.',
      portfolio_risks: ['Valuation multiple contraction'],
      portfolio_opportunities: ['Accelerated AI adoption'],
      watchlist_priorities: ['Monitor TSLA margins'],
      recommended_research: ['Evaluate AMD enterprise silicon'],
      sources: [{ symbol: 'NVDA', provider: 'YFinance', source_type: 'Telemetry' }],
      created_at: new Date().toISOString(),
    };

    (api.intelligence.getHistory as any).mockResolvedValue({ history: mockHistory, count: 1 });
    (api.intelligence.getReport as any).mockResolvedValue({ report: mockReport });

    render(
      <BrowserRouter>
        <ToastProvider>
          <Intelligence />
        </ToastProvider>
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('Portfolio & Watchlist Intelligence')).toBeInTheDocument();
      expect(screen.getAllByText(/"Rate risk and concentration"/i).length).toBeGreaterThan(0);
      expect(screen.getAllByText(/Portfolio is well-diversified/i).length).toBeGreaterThan(0);
      expect(screen.getByText(/Valuation multiple contraction/i)).toBeInTheDocument();
    });
  });

  it('generates new intelligence report on form submit', async () => {
    (api.intelligence.getHistory as any).mockResolvedValue({ history: [], count: 0 });
    (api.intelligence.generate as any).mockResolvedValueOnce({
      intelligence: {
        id: 5,
        user_id: 1,
        query: 'Tech sector deep dive',
        summary: 'Solid balance sheets across monitored assets.',
        portfolio_overview: 'Strong capital positioning.',
        portfolio_risks: ['FX headwinds'],
        portfolio_opportunities: ['Cloud margin expansion'],
        watchlist_priorities: [],
        recommended_research: [],
        sources: [],
        created_at: new Date().toISOString(),
      },
    });

    render(
      <BrowserRouter>
        <ToastProvider>
          <Intelligence />
        </ToastProvider>
      </BrowserRouter>
    );

    const input = screen.getByPlaceholderText(/Optional focal query/i);
    fireEvent.change(input, { target: { value: 'Tech sector deep dive' } });

    fireEvent.click(screen.getByRole('button', { name: /Generate New Synthesis/i }));

    await waitFor(() => {
      expect(api.intelligence.generate).toHaveBeenCalledWith({
        query: 'Tech sector deep dive',
      });
      expect(screen.getByText(/Solid balance sheets across monitored assets/i)).toBeInTheDocument();
    });
  });
});
