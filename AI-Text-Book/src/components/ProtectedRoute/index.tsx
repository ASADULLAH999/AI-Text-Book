import React from 'react';
import { useAuth } from '../../hooks/useAuth';
import { Redirect, useLocation } from '@docusaurus/router';
import BrowserOnly from '@docusaurus/BrowserOnly';

interface ProtectedRouteProps {
  children: React.ReactNode;
}

export default function ProtectedRoute({ children }: ProtectedRouteProps) {
  const { isAuthenticated, isLoading } = useAuth();
  const location = useLocation();

  // Wrap in BrowserOnly to avoid SSR issues
  return (
    <BrowserOnly fallback={<div>Loading...</div>}>
      {() => {
        // Show loading spinner while checking authentication
        if (isLoading) {
          return <div>Loading...</div>;
        }

        // Redirect to login if not authenticated
        if (!isAuthenticated) {
          return <Redirect to={`/login?returnTo=${encodeURIComponent(location.pathname)}`} />;
        }

        // Show protected content if authenticated
        return <>{children}</>;
      }}
    </BrowserOnly>
  );
}