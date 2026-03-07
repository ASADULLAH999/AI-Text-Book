import React from 'react';
import OriginalDocItem from '@theme-original/DocItem';

export default function DocItem(props: React.ComponentProps<typeof OriginalDocItem>) {
  return <OriginalDocItem {...props} />;
}