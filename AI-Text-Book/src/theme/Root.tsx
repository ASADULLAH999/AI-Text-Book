import React from 'react';
import OriginalRoot from '@theme-original/Root';
import { AuthProvider } from '../context/AuthContext';
import CookieConsent from '../components/CookieConsent';

export default function Root({ children }: { children: React.ReactNode }) {
  return (
    <OriginalRoot>
      <AuthProvider>
        {children}
        <CookieConsent />
      </AuthProvider>
    </OriginalRoot>
  );
}
