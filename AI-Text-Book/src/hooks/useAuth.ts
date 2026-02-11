import { useEffect, useState, useCallback } from 'react'
import { supabase } from '../lib/supabase'
import type { Session, User as SupabaseUser, AuthChangeEvent } from '@supabase/supabase-js'

// Extended User type with additional properties
export interface User extends SupabaseUser {
  name?: string;
  username?: string;
  avatar_url?: string;
}

export function useAuth() {
  const [user, setUser] = useState<User | null>(null)
  const [session, setSession] = useState<Session | null>(null)
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false)
  const [isLoading, setIsLoading] = useState<boolean>(true)

  useEffect(() => {
    supabase.auth.getSession().then(({ data }) => {
      setSession(data.session)
      // Extend user with additional properties
      const extendedUser = data.session?.user ? {
        ...data.session.user,
        name: data.session.user.user_metadata?.name || data.session.user.email?.split('@')[0],
        username: data.session.user.email?.split('@')[0] || 'user',
        avatar_url: data.session.user.user_metadata?.avatar_url,
      } as User : null
      setUser(extendedUser)
      setIsAuthenticated(!!data.session)
      setIsLoading(false)
    })

    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange(
      (event: AuthChangeEvent, session: Session | null) => {
        console.log('AUTH CHANGED:', event)

        setSession(session)
        // Extend user with additional properties
        const extendedUser = session?.user ? {
          ...session.user,
          name: session.user.user_metadata?.name || session.user.email?.split('@')[0],
          username: session.user.email?.split('@')[0] || 'user',
          avatar_url: session.user.user_metadata?.avatar_url,
        } as User : null
        setUser(extendedUser)
        setIsAuthenticated(!!session)
        setIsLoading(false)
      }
    )

    return () => subscription.unsubscribe()
  }, [])

  const signIn = useCallback(async (email: string, password: string) => {
    const { error } = await supabase.auth.signInWithPassword({
      email,
      password,
    })

    if (error) return { success: false, error: error.message }
    return { success: true }
  }, [])

  const signUp = useCallback(async (email: string, password: string, name?: string) => {
    const { error } = await supabase.auth.signUp({
      email,
      password,
      options: {
        data: {
          name: name || email.split('@')[0],
        },
      },
    })

    if (error) return { success: false, error: error.message }
    return { success: true }
  }, [])

  const logout = useCallback(async () => {
    await supabase.auth.signOut()
  }, [])

  return {
    user,
    session,
    isAuthenticated,
    isLoading,
    signIn,
    signUp,
    logout,
  }
}










// import { useCallback, useEffect, useState } from 'react';
// import { AuthState } from '../types/auth';
// import { authService } from '../services/auth-service';

// /**
//  * useAuth - Manage authentication state with Email/Password
//  */
// export function useAuth(): AuthState & {
//   signIn: (email: string, password: string) => Promise<{ success: boolean; error?: string }>;
//   signUp: (email: string, password: string, name?: string) => Promise<{ success: boolean; error?: string }>;
//   logout: () => void;
//   refreshToken: () => Promise<string>;
// } {
//   const [state, setState] = useState<AuthState>({
//     user: null,
//     session: null,
//     is_authenticated: false,
//     is_loading: true,
//     error: null,
//   });

//   // Initialize from localStorage on mount (client-side only)
//   useEffect(() => {
//     // Skip during SSR
//     if (typeof window === 'undefined') {
//       setState((prev) => ({ ...prev, is_loading: false }));
//       return;
//     }

//     try {
//       const session = authService.getCurrentSession();
//       const user = authService.getCurrentUser();

//       console.log('🔐 Auth initialized:', {
//         hasSession: !!session,
//         hasUser: !!user,
//         sessionExpiry: session?.expires_at,
//         now: Date.now(),
//         isValid: session ? session.expires_at > Date.now() : false
//       });

//       setState({
//         user,
//         session,
//         is_authenticated: !!session,
//         is_loading: false,
//         error: null,
//       });
//     } catch (error) {
//       console.error('❌ Auth initialization error:', error);
//       setState((prev) => ({
//         ...prev,
//         is_loading: false,
//         error: error instanceof Error ? error.message : 'Failed to load session',
//       }));
//     }
//   }, []);

//   const signIn = useCallback(async (email: string, password: string) => {
//     setState((prev) => ({ ...prev, is_loading: true, error: null }));

//     const { user, error } = await authService.signIn(email, password);

//     if (error) {
//       console.error('❌ SignIn failed:', error);
//       setState((prev) => ({
//         ...prev,
//         is_loading: false,
//         error: error.message || 'Sign in failed',
//       }));
//       return { success: false, error: error.message || 'Sign in failed' };
//     }

//     const session = authService.getCurrentSession();
//     console.log('✅ SignIn successful:', { user, hasSession: !!session });

//     setState({
//       user,
//       session,
//       is_authenticated: true,
//       is_loading: false,
//       error: null,
//     });

//     return { success: true };
//   }, []);

//   const signUp = useCallback(async (email: string, password: string, name?: string) => {
//     setState((prev) => ({ ...prev, is_loading: true, error: null }));

//     const { user, error } = await authService.signUp(email, password, name);

//     if (error) {
//       setState((prev) => ({
//         ...prev,
//         is_loading: false,
//         error: error.message || 'Sign up failed',
//       }));
//       return { success: false, error: error.message || 'Sign up failed' };
//     }

//     const session = authService.getCurrentSession();
//     setState({
//       user,
//       session,
//       is_authenticated: true,
//       is_loading: false,
//       error: null,
//     });

//     return { success: true };
//   }, []);

//   const logout = useCallback(() => {
//     authService.logout();
//     setState({
//       user: null,
//       session: null,
//       is_authenticated: false,
//       is_loading: false,
//       error: null,
//     });
//   }, []);

//   const refreshToken = useCallback(async () => {
//     try {
//       const token = await authService.refreshToken();
//       const session = authService.getCurrentSession();
//       const user = authService.getCurrentUser();

//       setState({
//         user,
//         session,
//         is_authenticated: !!session,
//         is_loading: false,
//         error: null,
//       });

//       return token;
//     } catch (error) {
//       setState((prev) => ({
//         ...prev,
//         error: error instanceof Error ? error.message : 'Token refresh failed',
//       }));
//       throw error;
//     }
//   }, []);

//   return { ...state, signIn, signUp, logout, refreshToken };
// }
