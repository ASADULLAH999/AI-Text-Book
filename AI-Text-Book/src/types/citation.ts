/**
 * TypeScript types for citation handling
 * Used for citation linking, scrolling, and UI interactions
 */

import { Source, ConfidenceLevel } from './chat';

/**
 * Citation display props
 */
export interface CitationProps {
  /** Source citation data */
  source: Source;
  /** Click handler for citation interaction */
  onClick?: (chunkId: string) => void;
  /** Whether citation is currently active/highlighted */
  isActive?: boolean;
}

/**
 * Citation location in textbook
 */
export interface CitationLocation {
  /** Chunk ID being referenced */
  chunk_id: string;
  /** Chapter name */
  chapter: string;
  /** Section identifier */
  section: string;
  /** Page number (if available) */
  page_number?: number;
  /** Heading hierarchy */
  heading: string;
  /** DOM element ID for scrolling (if available) */
  element_id?: string;
}

/**
 * Citation badge configuration
 */
export interface CitationBadge {
  /** Badge number/index */
  index: number;
  /** Confidence level for styling */
  confidence_level: ConfidenceLevel;
  /** Whether badge is clickable */
  interactive: boolean;
}

/**
 * Citation preview modal data
 */
export interface CitationPreview {
  /** Source data */
  source: Source;
  /** Full chunk text (if available) */
  full_text?: string;
  /** Whether preview is expanded */
  is_expanded: boolean;
}

/**
 * Scroll-to-source animation options
 */
export interface ScrollToSourceOptions {
  /** Animation duration in milliseconds */
  duration?: number;
  /** Whether to highlight target element */
  highlight?: boolean;
  /** Highlight duration in milliseconds */
  highlight_duration?: number;
  /** Scroll offset from top (pixels) */
  offset?: number;
}

/**
 * Citation validation result
 */
export interface CitationValidation {
  /** Whether citation is valid */
  is_valid: boolean;
  /** Chunk ID being validated */
  chunk_id: string;
  /** Validation error message (if invalid) */
  error?: string;
  /** Whether chunk exists in database */
  chunk_exists: boolean;
  /** Whether chunk supports the cited claim */
  supports_claim: boolean;
}

/**
 * Citation click event handler props
 */
export interface CitationClickEvent {
  /** Chunk ID clicked */
  chunk_id: string;
  /** Source data */
  source: Source;
  /** Event that triggered the click */
  event: React.MouseEvent<HTMLElement>;
}

/**
 * Citation link state
 */
export interface CitationLinkState {
  /** Currently active citation chunk ID */
  active_citation?: string;
  /** Whether citation preview modal is open */
  preview_open: boolean;
  /** Citation being previewed */
  preview_citation?: Source;
  /** Whether scroll animation is in progress */
  scrolling: boolean;
}

/**
 * Map of confidence levels to UI styles
 */
export const CONFIDENCE_STYLES: Record<ConfidenceLevel, {
  color: string;
  bgColor: string;
  borderColor: string;
  icon: string;
}> = {
  [ConfidenceLevel.HIGH]: {
    color: '#10b981',
    bgColor: '#d1fae5',
    borderColor: '#6ee7b7',
    icon: '✓',
  },
  [ConfidenceLevel.MEDIUM]: {
    color: '#f59e0b',
    bgColor: '#fef3c7',
    borderColor: '#fcd34d',
    icon: '~',
  },
  [ConfidenceLevel.LOW]: {
    color: '#ef4444',
    bgColor: '#fee2e2',
    borderColor: '#fca5a5',
    icon: '!',
  },
};

/**
 * Default scroll-to-source options
 */
export const DEFAULT_SCROLL_OPTIONS: ScrollToSourceOptions = {
  duration: 200,
  highlight: true,
  highlight_duration: 2000,
  offset: 80,
};
