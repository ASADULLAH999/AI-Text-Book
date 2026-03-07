import React, { lazy, Suspense } from 'react';
import OriginalDocPage from '@theme-original/DocPage';

// T104 — Lazy-load ChatPanel so it doesn't block the initial document render.
// The panel is not critical for first-paint; deferring its bundle reduces TTI.
const ChatPanel = lazy(() => import('@site/src/components/ChatPanel'));

function ChatPanelFallback() {
  return (
    <div
      style={{
        position: 'fixed',
        bottom: 20,
        right: 20,
        zIndex: 9999,
        width: 56,
        height: 56,
        borderRadius: '50%',
        background: 'var(--ifm-color-primary, #3578e5)',
        opacity: 0.4,
      }}
      aria-hidden="true"
    />
  );
}

export default function DocPage(props: Record<string, unknown>) {
  return (
    <>
      <OriginalDocPage {...props} />
      <div style={{ position: 'fixed', bottom: 20, right: 20, zIndex: 9999 }}>
        <Suspense fallback={<ChatPanelFallback />}>
          <ChatPanel />
        </Suspense>
      </div>
    </>
  );
}
