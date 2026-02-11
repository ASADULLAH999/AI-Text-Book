import React from 'react';
import OriginalDocPage from '@theme-original/DocPage';
// import AuthGate from '../components/AuthGate';
// import BrowserOnly from '@docusaurus/BrowserOnly';

export default function DocPage(props: React.ComponentProps<typeof OriginalDocPage>) {
  // Authentication temporarily disabled
  return <OriginalDocPage {...props} />;

  /* Original with auth:
  return (
    <BrowserOnly fallback={<div>Loading...</div>}>
      {() => (
        <AuthGate>
          <OriginalDocPage {...props} />
        </AuthGate>
      )}
    </BrowserOnly>
  );
  */
}