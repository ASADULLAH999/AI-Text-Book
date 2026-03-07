/**
 * CitationCard Component
 * Displays a citation source with preview
 */

import React, { useState } from 'react';
import { ApiCitation } from '../../services/chatApi';
import CitationPreview from './CitationPreview';
import styles from './styles.module.css';

export interface CitationCardProps {
  /** Citation data */
  citation: ApiCitation;
  /** Citation index/number */
  index: number;
  /** Click handler */
  onClick?: (citation: ApiCitation) => void;
}

/**
 * CitationCard - Card displaying citation source information
 */
export default function CitationCard({
  citation,
  index,
  onClick,
}: CitationCardProps): JSX.Element {
  const [showPreview, setShowPreview] = useState(false);

  /**
   * Get confidence level based on score
   */
  const getConfidenceLevel = (score: number): 'high' | 'medium' | 'low' => {
    if (score >= 0.8) return 'high';
    if (score >= 0.6) return 'medium';
    return 'low';
  };

  /**
   * Get confidence color
   */
  const getConfidenceColor = (level: string): string => {
    switch (level) {
      case 'high':
        return '#10b981'; // green
      case 'medium':
        return '#f59e0b'; // yellow
      case 'low':
        return '#ef4444'; // red
      default:
        return '#6b7280'; // gray
    }
  };

  const confidenceLevel = getConfidenceLevel(citation.score);
  const confidenceColor = getConfidenceColor(confidenceLevel);

  /**
   * Handle citation click
   */
  const handleClick = () => {
    if (onClick) {
      onClick(citation);
    }
  };

  /**
   * Format source location
   */
  const formatSource = (): string => {
    const parts = [citation.source.chapter, citation.source.section];
    if (citation.source.page_number) {
      parts.push(`p. ${citation.source.page_number}`);
    }
    return parts.filter(Boolean).join(' • ');
  };

  return (
    <div className={styles.citationCard}>
      <div
        className={styles.citationHeader}
        onClick={handleClick}
        onMouseEnter={() => setShowPreview(true)}
        onMouseLeave={() => setShowPreview(false)}
      >
        {/* Citation number badge */}
        <div
          className={styles.citationBadge}
          style={{ borderColor: confidenceColor }}
        >
          {index}
        </div>

        {/* Source info */}
        <div className={styles.citationInfo}>
          <div className={styles.citationSource}>{formatSource()}</div>
          {citation.source.heading && (
            <div className={styles.citationHeading}>{citation.source.heading}</div>
          )}
        </div>

        {/* Confidence indicator */}
        <div
          className={styles.confidenceIndicator}
          style={{ backgroundColor: confidenceColor }}
          title={`Confidence: ${Math.round(citation.score * 100)}%`}
        >
          <div
            className={styles.confidenceFill}
            style={{
              width: `${citation.score * 100}%`,
              backgroundColor: confidenceColor,
            }}
          />
        </div>
      </div>

      {/* Preview tooltip (shown on hover) */}
      {showPreview && (
        <CitationPreview
          citation={citation}
          onClose={() => setShowPreview(false)}
        />
      )}
    </div>
  );
}
