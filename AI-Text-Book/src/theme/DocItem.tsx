import React from 'react';
import OriginalDocItem from '@theme-original/DocItem';
// import AuthGate from '../components/AuthGate';
// import BrowserOnly from '@docusaurus/BrowserOnly';

export default function DocItem(props: React.ComponentProps<typeof OriginalDocItem>) {
  // Authentication temporarily disabled
  return <OriginalDocItem {...props} />;

  /* Original with auth:
  return (
    <BrowserOnly fallback={<div>Loading...</div>}>
      {() => (
        <AuthGate>
          <OriginalDocItem {...props} />
        </AuthGate>
      )}
    </BrowserOnly>
  );
  */
}