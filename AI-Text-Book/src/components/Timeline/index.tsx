import React, { useState } from 'react';
import styles from './styles.module.css';

interface TimelineItem {
  id: string;
  title: string;
  description: string;
  content: string;
  phase?: string;
}

interface TimelineProps {
  items?: TimelineItem[];
}

const defaultItems: TimelineItem[] = [
  {
    id: 'phase-1',
    title: 'Project Setup & Infrastructure',
    description: 'Week 1-2',
    content: 'Initialize repository, configure development environment, set up design system with CSS variables and animations.',
    phase: '1',
  },
  {
    id: 'phase-2',
    title: 'Foundational Systems',
    description: 'Week 2-3',
    content: 'Implement global state management, create header/footer components, build reading time system, and storage services.',
    phase: '2',
  },
  {
    id: 'phase-3',
    title: 'Homepage Development',
    description: 'Week 3-5',
    content: 'Create hero section with animations, module cards, curriculum guidance, and hardware requirements displays.',
    phase: '3',
  },
  {
    id: 'phase-4',
    title: 'Authentication & Quiz System',
    description: 'Week 5-7',
    content: 'Implement GitHub OAuth, build interactive quiz system with scoring, and progress tracking functionality.',
    phase: '4',
  },
  {
    id: 'phase-5',
    title: 'Multi-Language Support',
    description: 'Week 7-8',
    content: 'Configure i18n, implement RTL layout, and translate content to 5 languages including Arabic and Urdu.',
    phase: '5',
  },
  {
    id: 'phase-6',
    title: 'Search & Cookie Consent',
    description: 'Week 8-9',
    content: 'Integrate search functionality, implement GDPR-compliant cookie consent system with preferences.',
    phase: '6',
  },
  {
    id: 'phase-7',
    title: 'Testing, Optimization & Deployment',
    description: 'Week 9-10',
    content: 'Comprehensive testing, performance optimization to Lighthouse >= 90, accessibility compliance, and production deployment.',
    phase: '7',
  },
];

export const Timeline: React.FC<TimelineProps> = ({ items = defaultItems }) => {
  const [expandedId, setExpandedId] = useState<string | null>(null);

  const toggleExpand = (id: string) => {
    setExpandedId(expandedId === id ? null : id);
  };

  return (
    <section className={styles.section}>
      <div className={styles.container}>
        <div className={styles.header}>
          <h2 className={styles.title}>Development Timeline</h2>
          <p className={styles.subtitle}>7 phases, 10 weeks of structured development</p>
        </div>

        <div className={styles.timeline}>
          <div className={styles.line} />

          {items.map((item, index) => (
            <div key={item.id} className={styles.item} style={{ animationDelay: `${index * 0.1}s` }}>
              <div className={styles.nodeContainer}>
                <div className={`${styles.node} ${expandedId === item.id ? styles.active : ''}`}>
                  <span className={styles.phaseNumber}>{item.phase || index + 1}</span>
                </div>
              </div>

              <div className={styles.content}>
                <div
                  className={styles.contentHeader}
                  onClick={() => toggleExpand(item.id)}
                  role="button"
                  tabIndex={0}
                  onKeyPress={(e) => {
                    if (e.key === 'Enter' || e.key === ' ') {
                      e.preventDefault();
                      toggleExpand(item.id);
                    }
                  }}
                >
                  <div className={styles.titleGroup}>
                    <h3 className={styles.itemTitle}>{item.title}</h3>
                    <span className={styles.description}>{item.description}</span>
                  </div>

                  <div className={`${styles.chevron} ${expandedId === item.id ? styles.chevronActive : ''}`}>
                    <svg width="20" height="20" viewBox="0 0 20 20" fill="none" stroke="currentColor">
                      <polyline points="6 8 10 12 14 8" />
                    </svg>
                  </div>
                </div>

                {expandedId === item.id && (
                  <div className={styles.expandedContent}>
                    <p>{item.content}</p>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default Timeline;
