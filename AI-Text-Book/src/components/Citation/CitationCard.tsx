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
   * Map Qdrant chapter name → Docusaurus URL path segment.
   * These are the exact chapter strings stored in the vector DB.
   */
  const CHAPTER_SLUG: Record<string, string> = {
    'Module 1 Ros2':       'module-1-ros2',
    'Module 2 Simulation': 'module-2-simulation',
    'Module 3 Isaac':      'module-3-isaac',
    'Module 4 Voice':      'module-4-voice',
  };

  /**
   * Infer the doc page file slug from a section heading string.
   * Section names in Qdrant are H1/H2 headings from within doc pages, not
   * file names, so we match on keywords to identify the right page.
   */
  const inferPageSlug = (section: string): string => {
    const s = section.toLowerCase();
    if (/quiz/.test(s)) return 'quiz';
    if (/summary|key takeaway|complete/.test(s)) return 'summary';
    if (/best practice|professional pattern|production pattern/.test(s)) return 'best-practices';
    if (/example|code example|pattern/.test(s)) return 'code-examples';
    if (/hands.on|tutorial|build your first|step \d|goal/.test(s)) return 'hands-on-tutorial';
    if (/core concept|pillar|theory/.test(s)) return 'core-concepts';
    if (/introduction|why |matter|revolution|challenge/.test(s)) return 'introduction';
    if (/overview|index/.test(s)) return 'index';
    return '';
  };

  /** Convert any string to a URL-safe anchor fragment. */
  const toAnchor = (text: string): string =>
    text.toLowerCase().replace(/\s+/g, '-').replace(/[^\w-]/g, '');

  /**
   * Build a Docusaurus URL from citation source metadata.
   *
   * Examples:
   *   chapter="Module 1 Ros2", section="The Robotics Revolution", heading="Summary"
   *     → /docs/module-1-ros2/introduction#summary
   *   chapter="Module 1 Ros2", section="Goal", heading=null
   *     → /docs/module-1-ros2/hands-on-tutorial
   */
  const buildCitationUrl = (): string => {
    const rawChapter = citation.source.chapter?.trim() || '';
    const rawSection = citation.source.section?.trim() || '';

    const chapterSlug = CHAPTER_SLUG[rawChapter] || rawChapter.toLowerCase().replace(/\s+/g, '-').replace(/[^\w-]/g, '');
    const pageSlug    = inferPageSlug(rawSection);

    const parts = ['/docs', chapterSlug, pageSlug].filter(Boolean);
    let url = parts.join('/');

    // Use heading as anchor (most specific), fall back to section anchor
    const anchorText = citation.source.heading || rawSection;
    if (anchorText) {
      url += `#${toAnchor(anchorText)}`;
    }

    return url;
  };

  /**
   * Handle citation click — navigate to the corresponding doc section.
   */
  const handleClick = () => {
    if (onClick) {
      onClick(citation);
    }
    window.location.href = buildCitationUrl();
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
