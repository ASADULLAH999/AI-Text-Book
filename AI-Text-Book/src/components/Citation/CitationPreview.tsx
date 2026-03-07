/**
 * CitationPreview Component
 * Hover tooltip showing citation preview
 */

import React from 'react';
import { ApiCitation } from '../../services/chatApi';
import styles from './styles.module.css';

export interface CitationPreviewProps {
  /** Citation to preview */
  citation: ApiCitation;
  /** Close handler */
  onClose?: () => void;
}

/**
 * CitationPreview - Tooltip preview of citation content
 */
export default function CitationPreview({
  citation,
  onClose,
}: CitationPreviewProps): JSX.Element {
  /**
   * Format confidence score as percentage
   */
  const formatConfidence = (score: number): string => {
    return `${Math.round(score * 100)}%`;
  };

  return (
    <div className={styles.citationPreview}>
      {/* Preview header */}
      <div className={styles.previewHeader}>
        <div className={styles.previewTitle}>
          <span className={styles.previewIcon}>📖</span>
          <span>Citation Preview</span>
        </div>
        {onClose && (
          <button className={styles.previewClose} onClick={onClose}>
            ×
          </button>
        )}
      </div>

      {/* Source metadata */}
      <div className={styles.previewMeta}>
        <div className={styles.previewMetaItem}>
          <span className={styles.previewLabel}>Chapter:</span>
          <span>{citation.source.chapter}</span>
        </div>
        <div className={styles.previewMetaItem}>
          <span className={styles.previewLabel}>Section:</span>
          <span>{citation.source.section}</span>
        </div>
        {citation.source.heading && (
          <div className={styles.previewMetaItem}>
            <span className={styles.previewLabel}>Heading:</span>
            <span>{citation.source.heading}</span>
          </div>
        )}
        {citation.source.page_number && (
          <div className={styles.previewMetaItem}>
            <span className={styles.previewLabel}>Page:</span>
            <span>{citation.source.page_number}</span>
          </div>
        )}
        <div className={styles.previewMetaItem}>
          <span className={styles.previewLabel}>Relevance:</span>
          <span>{formatConfidence(citation.score)}</span>
        </div>
      </div>

      {/* Preview text */}
      <div className={styles.previewContent}>
        <div className={styles.previewLabel}>Text Preview:</div>
        <div className={styles.previewText}>
          {citation.preview || citation.text.substring(0, 200) + '...'}
        </div>
      </div>

      {/* Footer */}
      <div className={styles.previewFooter}>
        <span className={styles.previewHint}>
          Click to navigate to source
        </span>
      </div>
    </div>
  );
}
