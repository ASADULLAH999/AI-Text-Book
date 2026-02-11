import React from 'react';
import { useAuth } from '../../hooks/useAuth';
import { Redirect, useLocation } from '@docusaurus/router';
import BrowserOnly from '@docusaurus/BrowserOnly';
import styles from './styles.module.css';

interface AuthGateProps {
  children: React.ReactNode;
}

export default function AuthGate({ children }: AuthGateProps) {
  const { isAuthenticated, isLoading, user, session } = useAuth();
  const location = useLocation();

  console.log('🔒 AuthGate check:', {
    path: location.pathname,
    isAuthenticated,
    isLoading,
    hasUser: !!user,
    hasSession: !!session,
  });

  // Use BrowserOnly to avoid SSR issues
  return (
    <BrowserOnly fallback={<div>Loading...</div>}>
      {() => {
        // Show loading spinner while checking authentication
        if (isLoading) {
          console.log('⏳ AuthGate: Loading...');
          return (
            <div className={styles.loadingContainer}>
              <div className={styles.spinner}>
                <div className={styles.spinnerInner} />
              </div>
              <p className={styles.loadingText}>Loading...</p>
            </div>
          );
        }

        // Show login if not authenticated
        if (!isAuthenticated) {
          console.log('❌ AuthGate: Not authenticated, redirecting to login');
          return <Redirect to={`/login?returnTo=${encodeURIComponent(location.pathname)}`} />;
        }

        // Show protected content if authenticated
        console.log('✅ AuthGate: Authenticated, showing content');
        return <>{children}</>;
      }}
    </BrowserOnly>
  );
}
