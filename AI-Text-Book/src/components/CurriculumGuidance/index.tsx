import React, { useState } from 'react';
import styles from './styles.module.css';

interface TabContent {
  title: string;
  items: string[];
}

interface CurriculumGuidanceProps {
  learningOutcomes?: string[];
  assessments?: Array<{ name: string; percentage: number }>;
  prerequisites?: string[];
}

export const CurriculumGuidance: React.FC<CurriculumGuidanceProps> = ({
  learningOutcomes = [
    'Understand ROS 2 architecture and communication patterns (nodes, topics, services)',
    'Build and program humanoid robots with real-world applications',
    'Design and implement digital twin simulations for robotics systems',
    'Integrate AI and LLM capabilities into robotic systems',
    'Develop complete capstone projects combining all learned concepts',
    'Deploy and test robotic applications in production environments',
  ],
  assessments = [
    { name: 'Module Quizzes', percentage: 30 },
    { name: 'Hands-on Labs', percentage: 40 },
    { name: 'Capstone Project', percentage: 30 },
  ],
  prerequisites = [
    'Basic Python programming knowledge',
    'Familiarity with Linux command line',
    'Understanding of object-oriented programming',
    'Basic understanding of robotics concepts',
  ],
}) => {
  const [activeTab, setActiveTab] = useState(0);

  const tabs: TabContent[] = [
    {
      title: 'Learning Outcomes',
      items: learningOutcomes,
    },
    {
      title: 'Assessments',
      items: assessments.map((a) => `${a.name} - ${a.percentage}%`),
    },
    {
      title: 'Prerequisites',
      items: prerequisites,
    },
  ];

  return (
    <section className={styles.section}>
      <div className={styles.container}>
        <div className={styles.header}>
          <h2 className={styles.title}>Curriculum Guidance</h2>
          <p className={styles.subtitle}>What you'll learn and how you'll be assessed</p>
        </div>

        <div className={styles.content}>
          <div className={styles.tabBar}>
            {tabs.map((tab, index) => (
              <button
                key={index}
                className={`${styles.tab} ${activeTab === index ? styles.tabActive : ''}`}
                onClick={() => setActiveTab(index)}
              >
                {tab.title}
              </button>
            ))}
          </div>

          <div className={styles.tabContent}>
            {activeTab === 0 && (
              <div className={styles.outcomes}>
                <ul className={styles.list}>
                  {tabs[0].items.map((item, index) => (
                    <li key={index} className={styles.listItem}>
                      <span className={styles.icon}>✓</span>
                      <span>{item}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {activeTab === 1 && (
              <div className={styles.assessments}>
                {assessments.map((assessment, index) => (
                  <div key={index} className={styles.assessment}>
                    <div className={styles.assessmentHeader}>
                      <span className={styles.assessmentName}>{assessment.name}</span>
                      <span className={styles.assessmentPercentage}>{assessment.percentage}%</span>
                    </div>
                    <div className={styles.progressBar}>
                      <div className={styles.progressFill} style={{ width: `${assessment.percentage}%` }} />
                    </div>
                  </div>
                ))}
              </div>
            )}

            {activeTab === 2 && (
              <div className={styles.prerequisites}>
                <ul className={styles.list}>
                  {tabs[2].items.map((item, index) => (
                    <li key={index} className={styles.listItem}>
                      <span className={styles.icon}>→</span>
                      <span>{item}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </div>
      </div>
    </section>
  );
};

export default CurriculumGuidance;
