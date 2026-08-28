export type WatchlistPriority = 'low' | 'normal' | 'high';

export interface WatchlistItem {
  id: number;
  user_id: number;
  symbol: string;
  company_name?: string;
  current_price?: number;
  price_change_24h_percent?: number | null;
  quote_available?: boolean;
  notes?: string | null;
  priority: WatchlistPriority;
  created_at: string;
  updated_at: string;
}

export interface WatchlistCreatePayload {
  symbol: string;
  notes?: string;
  priority?: WatchlistPriority;
}

export interface WatchlistUpdatePayload {
  notes?: string;
  priority?: WatchlistPriority;
}
