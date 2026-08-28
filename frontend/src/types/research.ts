import { SourceMetadata } from './intelligence';

export interface CompanySearchResult {
  symbol: string;
  name: string;
  exchange?: string;
  type?: string;
}

export interface CompanyProfile {
  symbol: string;
  name: string;
  sector?: string;
  industry?: string;
  description?: string;
  website?: string;
  market_cap?: number;
  currency?: string;
}

export interface MarketQuote {
  symbol: string;
  current_price: number;
  day_high?: number;
  day_low?: number;
  previous_close?: number;
  open?: number;
  volume?: number;
  day_change?: number;
  day_change_percent?: number;
  timestamp?: string;
}

export interface KeyMetrics {
  symbol: string;
  pe_ratio?: number | null;
  forward_pe?: number | null;
  price_to_book?: number | null;
  beta?: number | null;
  dividend_yield?: number | null;
  eps?: number | null;
}

export interface NewsItem {
  title: string;
  publisher?: string;
  link?: string;
  publish_time?: string;
  symbol?: string;
}

export interface ResearchRecord {
  id: number;
  user_id: number;
  symbol: string;
  company: string;
  query?: string | null;
  summary: string;
  fundamentals?: string | null;
  valuation?: string | null;
  market_context?: string | null;
  risks: string[];
  opportunities: string[];
  facts: Record<string, unknown>;
  sources: SourceMetadata[];
  user_context?: string | null;
  created_at: string;
  updated_at?: string | null;
}

export interface ResearchHistoryItem {
  id: number;
  symbol: string;
  company: string;
  query?: string | null;
  summary: string;
  created_at: string;
}

export interface ResearchHistoryResponse {
  history: ResearchHistoryItem[];
  count: number;
  total: number;
  page: number;
  limit: number;
}
