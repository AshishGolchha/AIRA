export interface PortfolioHolding {
  id: number;
  user_id: number;
  symbol: string;
  quantity: number;
  average_cost: number;
  cost_basis: number;
  notes?: string | null;
  created_at: string;
  updated_at: string;
}

export interface HoldingValuation {
  id: number;
  symbol: string;
  company_name?: string;
  quantity: number;
  average_cost: number;
  cost_basis: number;
  current_price?: number;
  market_value?: number;
  unrealized_gain_loss?: number;
  unrealized_gain_loss_percent?: number | null;
  weight_percent?: number;
  quote_available?: boolean;
  notes?: string | null;
}

export interface PortfolioSnapshot {
  holdings: HoldingValuation[];
  holdings_count: number;
  total_cost_basis: number;
  total_market_value: number;
  total_unrealized_gain_loss: number;
  total_unrealized_gain_loss_percent: number | null;
  as_of: string;
}

export interface HoldingCreatePayload {
  symbol: string;
  quantity: number;
  average_cost: number;
  notes?: string;
}

export interface HoldingUpdatePayload {
  quantity?: number;
  average_cost?: number;
  notes?: string;
}
