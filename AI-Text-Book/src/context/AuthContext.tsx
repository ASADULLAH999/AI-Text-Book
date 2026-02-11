import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { AuthState, User, AuthSession } from '../types/auth';

interface AuthContextType extends AuthState {
  login: () => void;
  logout: () => void;
  setUser: (user: User | null) => void;
  updateSession: (session: AuthSession | null) => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [state, setState] = useState<AuthState>({
    user: null,
    session: null,
    is_authenticated: false,
    is_loading: true,
    error: null,
  });

  // Initialize from localStorage on mount
  useEffect(() => {
    const loadAuthState = () => {
      try {
        const storedSession = localStorage.getItem('auth_session');
        if (storedSession) {
          const session = JSON.parse(storedSession) as AuthSession;
          // Check if session is still valid
          if (session.expires_at > Date.now()) {
            setState({
              user: session.user,
              session,
              is_authenticated: true,
              is_loading: false,
              error: null,
            });
            return;
          } else {
            // Session expired, clear it
            localStorage.removeItem('auth_session');
          }
        }
      } catch (err) {
        console.error('Failed to load auth state:', err);
      }
      setState((prev) => ({ ...prev, is_loading: false }));
    };

    loadAuthState();
  }, []);

  const login = useCallback(() => {
    // For email/password auth, we don't redirect to external provider
    // This method is kept for interface compatibility
    console.log('Email/password auth does not require external login');
  }, []);

  const logout = useCallback(() => {
    setState({
      user: null,
      session: null,
      is_authenticated: false,
      is_loading: false,
      error: null,
    });
    localStorage.removeItem('auth_session');
  }, []);

  const setUser = useCallback((user: User | null) => {
    setState((prev) => ({
      ...prev,
      user,
      is_authenticated: user !== null,
    }));
  }, []);

  const updateSession = useCallback((session: AuthSession | null) => {
    setState((prev) => ({
      ...prev,
      session,
      user: session?.user || null,
      is_authenticated: session !== null,
    }));
    if (session) {
      localStorage.setItem('auth_session', JSON.stringify(session));
    } else {
      localStorage.removeItem('auth_session');
    }
  }, []);

  const value: AuthContextType = {
    ...state,
    login,
    logout,
    setUser,
    updateSession,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuthContext = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuthContext must be used within AuthProvider');
  }
  return context;
};
