import { Alert } from './alert';
import { HoldingValuation } from './portfolio';
import { ResearchHistoryItem } from './research';
import { WatchlistItem } from './watchlist';

export interface DashboardUserProfile {
  id: number;
  email: string;
  name: string;
  investment_focus: string | null;
  risk_tolerance: string;
  investment_horizon: string;
}

export interface DashboardPortfolio {
  total_market_value: number;
  total_cost_basis: number;
  unrealized_gain_loss: number;
  unrealized_gain_loss_percent: number | null;
  holdings_count: number;
  top_holdings: HoldingValuation[];
}

export interface DashboardWatchlist {
  total_count: number;
  high_priority_count: number;
  normal_priority_count: number;
  low_priority_count: number;
  items: WatchlistItem[];
}

export interface DashboardAlerts {
  unread_count: number;
  critical_count: number;
  warning_count: number;
  info_count: number;
  recent: Alert[];
}

export interface DashboardResearch {
  total_reports: number;
  recent: ResearchHistoryItem[];
}

export interface DashboardNotifications {
  preferences: {
    in_app_enabled: boolean;
    email_enabled: boolean;
    webhook_enabled: boolean;
    minimum_severity: string;
    alert_types: string[];
  };
  enabled_channels: string[];
  pending_retry_count: number;
  failed_delivery_count: number;
  delivered_count: number;
}

export interface DashboardMonitoring {
  system_monitoring_enabled: boolean;
  user_alerts_enabled: boolean;
  latest_run: {
    id: number;
    status: string;
    started_at: string | null;
    completed_at: string | null;
    duration_seconds: number | null;
  } | null;
}

export interface DashboardPortfolioIntelligence {
  available: boolean;
  latest: {
    id: number;
    summary: string;
    symbols_analyzed: string[];
    created_at: string;
  } | null;
  message?: string;
}

export interface DashboardResponse {
  user: DashboardUserProfile;
  portfolio: DashboardPortfolio;
  watchlist: DashboardWatchlist;
  alerts: DashboardAlerts;
  research: DashboardResearch;
  notifications: DashboardNotifications;
  monitoring: DashboardMonitoring;
  portfolio_intelligence: DashboardPortfolioIntelligence;
}

export interface DashboardSummaryResponse {
  portfolio_market_value: number;
  portfolio_gain_loss_percent: number | null;
  holdings_count: number;
  watchlist_count: number;
  unread_alerts_count: number;
  critical_alerts_count: number;
  research_reports_count: number;
  monitoring_enabled: boolean;
}
