export type AlertSeverity = 'info' | 'warning' | 'critical';
export type AlertType = 'price_move' | 'portfolio_gain_loss' | 'watchlist_move' | 'data_quality';

export interface Alert {
  id: number;
  user_id: number;
  symbol: string;
  alert_type: AlertType;
  severity: AlertSeverity;
  title: string;
  message: string;
  is_read: boolean;
  is_dismissed: boolean;
  context_data?: Record<string, unknown> | null;
  created_at: string;
  updated_at: string;
}

export interface AlertsListResponse {
  alerts: Alert[];
  count: number;
  total: number;
  page: number;
  limit: number;
}

export interface AlertCheckResponse {
  created_count: number;
  alerts: Alert[];
}
