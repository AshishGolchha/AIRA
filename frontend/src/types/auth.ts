export interface UserProfile {
  id?: number;
  user_id?: number;
  display_name: string | null;
  investment_focus: string | null;
  risk_preference: string;
  investment_horizon: string;
  created_at?: string;
  updated_at?: string;
}

export interface User {
  id: number;
  email: string;
  is_active: boolean;
  alerts_enabled: boolean;
  created_at: string;
  updated_at: string;
  profile: UserProfile | null;
}

export interface AuthData {
  access_token: string;
  token_type: string;
  user: User;
}

export interface LoginPayload {
  email: string;
  password: string;
}

export interface RegisterPayload {
  email: string;
  password: string;
  display_name?: string;
}
