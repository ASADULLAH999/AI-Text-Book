import { supabase } from '../lib/supabase';
import { User, AuthSession } from '../types/auth';

/**
 * AuthService - Manages Email/Password authentication using Supabase
 */
class AuthService {
  private readonly AUTH_SESSION_KEY = 'ai_textbook_auth_session';

  /**
   * Sign up with email and password
   */
  async signUp(email: string, password: string, name?: string): Promise<{ user: User | null; error: any }> {
    try {
      console.log('Attempting signup for:', email);
      const { data, error } = await supabase.auth.signUp({
        email,
        password,
        options: {
          data: {
            name: name || email.split('@')[0],
          },
        },
      });

      if (error) {
        console.error('Supabase signup error:', error);
        return { user: null, error };
      }

      if (data.user) {
        const user: User = {
          id: data.user.id,
          username: data.user.email?.split('@')[0] || 'user',
          name: name || data.user.user_metadata?.name || data.user.email?.split('@')[0] || 'User',
          email: data.user.email || '',
          created_at: new Date(data.user.created_at).getTime(),
          last_login: Date.now(),
        };

        // Store session if confirmed
        if (data.session) {
          console.log('Signup successful, storing session');
          this.storeSession({
            user,
            access_token: data.session.access_token,
            refresh_token: data.session.refresh_token,
            expires_at: new Date(data.session.expires_at || 0).getTime(),
            created_at: Date.now(),
          });
        } else {
          console.warn('Signup successful but no session returned - email confirmation may be required');
        }

        return { user, error: null };
      }

      return { user: null, error: 'No user data returned' };
    } catch (error) {
      console.error('Sign up error:', error);
      return { user: null, error };
    }
  }

  /**
   * Sign in with email and password
   */
  async signIn(email: string, password: string): Promise<{ user: User | null; error: any }> {
    try {
      console.log('Attempting signin for:', email);
      const { data, error } = await supabase.auth.signInWithPassword({
        email,
        password,
      });

      if (error) {
        console.error('Supabase signin error:', error);
        return { user: null, error };
      }

      if (data.user && data.session) {
        const user: User = {
          id: data.user.id,
          username: data.user.email?.split('@')[0] || 'user',
          name: data.user.user_metadata?.name || data.user.email?.split('@')[0] || 'User',
          email: data.user.email || '',
          created_at: new Date(data.user.created_at).getTime(),
          last_login: Date.now(),
        };

        console.log('Signin successful, storing session');
        this.storeSession({
          user,
          access_token: data.session.access_token,
          refresh_token: data.session.refresh_token,
          expires_at: new Date(data.session.expires_at || 0).getTime(),
          created_at: Date.now(),
        });

        return { user, error: null };
      }

      return { user: null, error: 'No user data returned' };
    } catch (error) {
      console.error('Sign in error:', error);
      return { user: null, error };
    }
  }

  /**
   * Sign out
   */
  async signOut(): Promise<void> {
    try {
      await supabase.auth.signOut();
      this.clearSession();
    } catch (error) {
      console.error('Sign out error:', error);
      this.clearSession();
    }
  }

  /**
   * Handle OAuth callback (kept for potential future use, but not used in email/password flow)
   */
  async handleCallback(code: string, state: string): Promise<void> {
    // This method is not used in email/password authentication
    // Kept for compatibility with potential future OAuth implementations
    console.warn('handleCallback called, but this is for OAuth, not email/password auth');
    throw new Error('OAuth callback not supported in email/password flow');
  }

  /**
   * Get current session from localStorage or cookies
   */
  getCurrentSession(): AuthSession | null {
    try {
      // Try localStorage first
      if (typeof window !== 'undefined') {
        const sessionStr = localStorage.getItem(this.AUTH_SESSION_KEY);
        if (sessionStr) {
          const session: AuthSession = JSON.parse(sessionStr);

          // Check if session is expired
          if (session.expires_at && Date.now() > session.expires_at) {
            this.clearSession();
            return null;
          }

          return session;
        }
      }

      // Fall back to cookies
      return this.getSessionFromCookie();
    } catch (error) {
      console.error('Error getting session:', error);
      return null;
    }
  }

  /**
   * Get current user
   */
  getCurrentUser(): User | null {
    const session = this.getCurrentSession();
    return session?.user || null;
  }

  /**
   * Check if user is authenticated
   */
  isAuthenticated(): boolean {
    return this.getCurrentSession() !== null;
  }

  /**
   * Refresh token
   */
  async refreshToken(): Promise<string> {
    try {
      const { data, error } = await supabase.auth.refreshSession();

      if (error || !data.session) {
        throw new Error('Failed to refresh token');
      }

      const session = this.getCurrentSession();
      if (session) {
        session.access_token = data.session.access_token;
        session.refresh_token = data.session.refresh_token || session.refresh_token;
        session.expires_at = new Date(data.session.expires_at || 0).getTime();
        this.storeSession(session);
      }

      return data.session.access_token;
    } catch (error) {
      console.error('Token refresh error:', error);
      this.clearSession();
      throw error;
    }
  }

  /**
   * Logout (alias for signOut)
   */
  logout(): void {
    this.signOut();
  }

  /**
   * Store session in both localStorage and cookies for SSR support
   */
  private storeSession(session: AuthSession): void {
    if (typeof window === 'undefined') return;

    // Store in localStorage
    try {
      localStorage.setItem(this.AUTH_SESSION_KEY, JSON.stringify(session));
    } catch (e) {
      console.error('Failed to store in localStorage:', e);
    }

    // Store in cookies for SSR/production support
    try {
      const expires = new Date(session.expires_at);
      const isSecure = window.location.protocol === 'https:';
      const cookieOptions = [
        `${this.AUTH_SESSION_KEY}=${encodeURIComponent(JSON.stringify(session))}`,
        `expires=${expires.toUTCString()}`,
        'path=/',
        'SameSite=Lax', // Changed from Strict to Lax for better production compatibility
        isSecure ? 'Secure' : '', // Add Secure flag for HTTPS
      ].filter(Boolean).join('; ');

      document.cookie = cookieOptions;
      console.log('Session stored successfully in cookies and localStorage');
    } catch (e) {
      console.error('Failed to store in cookies:', e);
    }
  }

  /**
   * Clear session from both localStorage and cookies
   */
  private clearSession(): void {
    if (typeof window === 'undefined') return;

    // Clear localStorage
    try {
      localStorage.removeItem(this.AUTH_SESSION_KEY);
    } catch (e) {
      console.error('Failed to clear localStorage:', e);
    }

    // Clear cookies
    try {
      document.cookie = `${this.AUTH_SESSION_KEY}=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;`;
    } catch (e) {
      console.error('Failed to clear cookies:', e);
    }
  }

  /**
   * Get session from cookies (for SSR)
   */
  private getSessionFromCookie(): AuthSession | null {
    if (typeof document === 'undefined') return null;

    try {
      const cookies = document.cookie.split(';');
      for (const cookie of cookies) {
        const [name, value] = cookie.trim().split('=');
        if (name === this.AUTH_SESSION_KEY) {
          return JSON.parse(decodeURIComponent(value));
        }
      }
    } catch (e) {
      console.error('Failed to get session from cookie:', e);
    }

    return null;
  }
}

export const authService = new AuthService();
