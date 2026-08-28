export interface MonitoringRunSummary {
  id: number;
  status: string;
  started_at: string | null;
  completed_at: string | null;
  duration_seconds: number | null;
  users_processed?: number;
  alerts_created?: number;
  notifications_dispatched?: number;
}

export interface MonitoringStatusResponse {
  monitoring_enabled: boolean;
  latest_run: MonitoringRunSummary | null;
}
