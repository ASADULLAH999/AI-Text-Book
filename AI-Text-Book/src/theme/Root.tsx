import React, { lazy, Suspense, useState } from 'react';
import OriginalRoot from '@theme-original/Root';
import CookieConsent from '../components/CookieConsent';
import { useTextSelection } from '../hooks/useTextSelection';
import SelectionMenu from '../components/TextSelection/SelectionMenu';

const ChatPanel = lazy(() => import('@site/src/components/ChatPanel'));

export default function Root({ children }: { children: React.ReactNode }) {
  const { selection, clearSelection, hasValidSelection } = useTextSelection();
  const [pendingSelection, setPendingSelection] = useState<string | null>(null);

  const handleAskAI = (text: string) => {
    setPendingSelection(text);
    clearSelection();
  };

  const handleSelectionCleared = () => {
    setPendingSelection(null);
  };

  return (
    <OriginalRoot>
      {children}
      <CookieConsent />
      {(hasValidSelection || (selection && !selection.isValid)) && (
        <SelectionMenu
          selection={selection}
          onAskAI={handleAskAI}
          onDismiss={clearSelection}
        />
      )}
      <Suspense fallback={null}>
        <ChatPanel
          pendingSelection={pendingSelection}
          onSelectionCleared={handleSelectionCleared}
        />
      </Suspense>
    </OriginalRoot>
  );
}
