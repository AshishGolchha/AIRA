export type NotificationChannel = 'in_app' | 'email' | 'webhook';
export type DeliveryStatus = 'delivered' | 'failed' | 'pending';

export interface NotificationPreference {
  id: number;
  user_id: number;
  in_app_enabled: boolean;
  email_enabled: boolean;
  webhook_enabled: boolean;
  minimum_severity: string;
  alert_types: string[];
  created_at: string;
  updated_at: string;
}

export interface NotificationEndpoint {
  id: number;
  user_id: number;
  endpoint_url: string;
  channel: string;
  is_enabled: boolean;
  has_secret?: boolean;
  created_at: string;
  updated_at: string;
}

export interface NotificationDelivery {
  id: number;
  alert_id: number;
  user_id: number;
  channel: NotificationChannel;
  status: DeliveryStatus;
  attempt_count: number;
  error_message?: string | null;
  delivered_at?: string | null;
  created_at: string;
}

export interface DeliveriesListResponse {
  deliveries: NotificationDelivery[];
  count: number;
  total: number;
  page: number;
  limit: number;
}
