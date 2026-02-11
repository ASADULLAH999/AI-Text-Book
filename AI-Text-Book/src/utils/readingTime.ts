import { ReadingTimeData } from '../types/progress';

const WORDS_PER_MINUTE = 200;
const CODE_BLOCK_ADJUSTMENT = 0.5; // Code blocks count for 50% of words

/**
 * Calculate reading time from markdown content
 * @param markdown - Markdown content string
 * @param contentId - Unique identifier for this content
 * @returns ReadingTimeData with estimated time and metadata
 */
export function calculateReadingTime(markdown: string, contentId: string): ReadingTimeData {
  if (!markdown) {
    return {
      content_id: contentId,
      estimated_minutes: 0,
      word_count: 0,
      calculated_at: Date.now(),
    };
  }

  // Remove frontmatter
  let content = markdown.replace(/^---[\s\S]*?---\n/, '');

  // Extract and process code blocks separately
  const codeBlockRegex = /```[\s\S]*?```/g;
  const codeBlocks = content.match(codeBlockRegex) || [];

  // Remove code blocks temporarily to count non-code words
  content = content.replace(codeBlockRegex, '');

  // Count words (split on whitespace)
  const textWords = content.trim().split(/\s+/).length;

  // Count words in code blocks (with adjustment factor)
  let codeWords = 0;
  codeBlocks.forEach((block) => {
    const words = block.split(/\s+/).length;
    codeWords += words * CODE_BLOCK_ADJUSTMENT;
  });

  // Calculate total word count
  const totalWords = textWords + Math.ceil(codeWords);

  // Calculate reading time (minimum 1 minute)
  const estimatedMinutes = Math.max(1, Math.ceil(totalWords / WORDS_PER_MINUTE));

  return {
    content_id: contentId,
    estimated_minutes: estimatedMinutes,
    word_count: totalWords,
    calculated_at: Date.now(),
  };
}

/**
 * Format reading time for display
 * @param minutes - Number of minutes
 * @returns Formatted string (e.g., "5 min read", "1 min read")
 */
export function formatReadingTime(minutes: number): string {
  if (minutes < 1) {
    return 'Less than 1 min read';
  }
  if (minutes === 1) {
    return '1 min read';
  }
  return `${minutes} min read`;
}

/**
 * Calculate reading speed for a given section based on content and time
 * @param wordCount - Total words in section
 * @param timeSpentMs - Time spent reading in milliseconds
 * @returns Reading speed in words per minute
 */
export function calculateReadingSpeed(wordCount: number, timeSpentMs: number): number {
  if (timeSpentMs === 0 || wordCount === 0) {
    return 0;
  }
  const minutes = timeSpentMs / (1000 * 60);
  return Math.round(wordCount / minutes);
}

/**
 * Extract reading time from markdown frontmatter if present
 * @param markdown - Markdown content with frontmatter
 * @returns Reading time in minutes or null if not found
 */
export function extractReadingTimeFromFrontmatter(markdown: string): number | null {
  const frontmatterRegex = /^---\n([\s\S]*?)\n---/;
  const match = markdown.match(frontmatterRegex);

  if (!match) {
    return null;
  }

  const frontmatter = match[1];
  const readingTimeMatch = frontmatter.match(/readingTime:\s*(\d+)/);

  if (readingTimeMatch) {
    return parseInt(readingTimeMatch[1], 10);
  }

  return null;
}

/**
 * Get reading time with caching
 * @param markdown - Markdown content
 * @param contentId - Content identifier
 * @param useCache - Whether to use cached value if available
 * @returns ReadingTimeData
 */
export function getReadingTime(
  markdown: string,
  contentId: string,
  useCache = true
): ReadingTimeData {
  if (useCache) {
    // Check frontmatter first
    const frontmatterTime = extractReadingTimeFromFrontmatter(markdown);
    if (frontmatterTime !== null) {
      return {
        content_id: contentId,
        estimated_minutes: frontmatterTime,
        word_count: 0,
        calculated_at: Date.now(),
      };
    }

    // Check localStorage cache
    const cached = localStorage.getItem(`reading_time_${contentId}`);
    if (cached) {
      try {
        return JSON.parse(cached);
      } catch (err) {
        console.warn('Failed to parse cached reading time:', err);
      }
    }
  }

  // Calculate and cache
  const data = calculateReadingTime(markdown, contentId);

  try {
    localStorage.setItem(`reading_time_${contentId}`, JSON.stringify(data));
  } catch (err) {
    console.warn('Failed to cache reading time:', err);
  }

  return data;
}

/**
 * Clear reading time cache
 */
export function clearReadingTimeCache(): void {
  const keys = Object.keys(localStorage);
  keys.forEach((key) => {
    if (key.startsWith('reading_time_')) {
      localStorage.removeItem(key);
    }
  });
}
