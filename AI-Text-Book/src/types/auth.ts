export interface User {
  id: string;
  username: string;
  name?: string;
  avatar_url?: string;
  email?: string;
  created_at: number;
  last_login: number;
}

export interface AuthSession {
  access_token: string;
  refresh_token?: string;
  expires_at: number;
  expires_in?: number;
  created_at?: number;
  user: User;
}

export interface AuthState {
  user: User | null;
  session: AuthSession | null;
  is_authenticated: boolean;
  is_loading: boolean;
  isAuthenticated?: boolean;
  isLoading?: boolean;
  error: string | null;
}

export interface GitHubOAuthConfig {
  client_id: string;
  redirect_uri: string;
  scope: string;
  state: string;
}

export interface GitHubTokenResponse {
  access_token: string;
  token_type: string;
  scope: string;
  refresh_token?: string;
  refresh_token_expires_in?: number;
  expires_in?: number;
}

export interface GitHubUser {
  id: number;
  login: string;
  avatar_url: string;
  email?: string;
  name?: string;
}
