import React, { useMemo } from 'react';
import { formatReadingTime, getReadingTime } from '@utils/readingTime';
import styles from './styles.module.css';

interface ReadingTimeProps {
  markdown: string;
  contentId: string;
  showIcon?: boolean;
  className?: string;
}

/**
 * ReadingTime Component - Displays estimated reading time
 * Calculates based on word count and code block analysis
 */
export const ReadingTime: React.FC<ReadingTimeProps> = ({
  markdown,
  contentId,
  showIcon = true,
  className = '',
}) => {
  const readingData = useMemo(() => {
    return getReadingTime(markdown, contentId);
  }, [markdown, contentId]);

  const displayTime = formatReadingTime(readingData.estimated_minutes);

  return (
    <div className={`${styles.readingTime} ${className}`}>
      {showIcon && <span className={styles.icon}>⏱</span>}
      <span className={styles.text}>{displayTime}</span>
      {readingData.word_count > 0 && (
        <span className={styles.wordCount} title={`${readingData.word_count} words`}>
          ({readingData.word_count.toLocaleString()} words)
        </span>
      )}
    </div>
  );
};

export default ReadingTime;
