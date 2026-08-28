export interface SourceMetadata {
  provider: string;
  symbol: string;
  source_type?: string;
  timestamp?: string;
}

export interface PortfolioIntelligenceRecord {
  id: number;
  user_id: number;
  query?: string | null;
  summary: string;
  portfolio_overview: string;
  portfolio_risks: string[];
  portfolio_opportunities: string[];
  watchlist_priorities: string[];
  recommended_research: string[];
  portfolio_summary: Record<string, unknown>;
  user_context?: string | null;
  facts: Record<string, unknown>;
  sources: SourceMetadata[];
  created_at: string;
  updated_at?: string | null;
}

export interface PortfolioIntelligenceSummaryItem {
  id: number;
  query?: string | null;
  summary: string;
  symbols_analyzed: string[];
  created_at: string;
}

export interface IntelligenceHistoryResponse {
  history: PortfolioIntelligenceSummaryItem[];
  count: number;
  total: number;
  page: number;
  limit: number;
}
