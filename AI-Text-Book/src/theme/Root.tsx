import React from 'react';
import OriginalRoot from '@theme-original/Root';
import CookieConsent from '../components/CookieConsent';

export default function Root({ children }: { children: React.ReactNode }) {
  return (
    <OriginalRoot>
      {children}
      <CookieConsent />
    </OriginalRoot>
  );
}
