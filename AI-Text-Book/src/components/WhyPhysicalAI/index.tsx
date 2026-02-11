import React from 'react';
import styles from './styles.module.css';

interface KeyPoint {
  icon: string;
  title: string;
  description: string;
}

interface WhyPhysicalAIProps {
  keyPoints?: KeyPoint[];
}

const defaultKeyPoints: KeyPoint[] = [
  {
    icon: '🤖',
    title: 'Embodied Intelligence',
    description: 'Learn how physical systems interact with the real world, combining sensors, actuators, and AI for truly intelligent robotics.',
  },
  {
    icon: '🤝',
    title: 'Human-Robot Interaction',
    description: 'Master the principles of safe, intuitive collaboration between humans and robots in shared environments.',
  },
  {
    icon: '🌉',
    title: 'Sim-to-Real Transfer',
    description: 'Develop skills in simulation-based training and transferring learned behaviors to real-world hardware.',
  },
];

export const WhyPhysicalAI: React.FC<WhyPhysicalAIProps> = ({ keyPoints = defaultKeyPoints }) => {
  const handleLearnMore = () => {
    window.location.href = '/docs/module-1-ros2/introduction';
  };

  return (
    <section className={styles.section}>
      <div className={styles.container}>
        <div className={styles.content}>
          {/* Left Column - Text Content */}
          <div className={styles.textColumn}>
            <div className={styles.header}>
              <h2 className={styles.title}>Why Physical AI Matters</h2>
              <p className={styles.subtitle}>
                AI systems need to understand and interact with the physical world to be truly intelligent.
              </p>
            </div>

            <div className={styles.keyPoints}>
              {keyPoints.map((point, index) => (
                <div key={index} className={styles.keyPoint}>
                  <div className={styles.iconBox}>{point.icon}</div>
                  <div className={styles.pointContent}>
                    <h3 className={styles.pointTitle}>{point.title}</h3>
                    <p className={styles.pointDescription}>{point.description}</p>
                  </div>
                </div>
              ))}
            </div>

            <button className={styles.cta} onClick={handleLearnMore}>Learn More About Physical AI</button>
          </div>

          {/* Right Column - Visual */}
          <div className={styles.visualColumn}>
            <div className={styles.illustration}>
              <svg viewBox="0 0 300 400" className={styles.robotSvg}>
                {/* Neural Network Background */}
                <g className={styles.neuralNet}>
                  <circle cx="150" cy="80" r="3" fill="rgba(34, 211, 238, 0.4)" />
                  <circle cx="100" cy="150" r="3" fill="rgba(34, 211, 238, 0.4)" />
                  <circle cx="200" cy="150" r="3" fill="rgba(34, 211, 238, 0.4)" />
                  <circle cx="80" cy="250" r="3" fill="rgba(34, 211, 238, 0.4)" />
                  <circle cx="150" cy="280" r="3" fill="rgba(34, 211, 238, 0.4)" />
                  <circle cx="220" cy="250" r="3" fill="rgba(34, 211, 238, 0.4)" />

                  {/* Connection Lines */}
                  <line x1="150" y1="80" x2="100" y2="150" stroke="rgba(34, 211, 238, 0.2)" strokeWidth="1" />
                  <line x1="150" y1="80" x2="200" y2="150" stroke="rgba(34, 211, 238, 0.2)" strokeWidth="1" />
                  <line x1="100" y1="150" x2="80" y2="250" stroke="rgba(34, 211, 238, 0.2)" strokeWidth="1" />
                  <line x1="200" y1="150" x2="220" y2="250" stroke="rgba(34, 211, 238, 0.2)" strokeWidth="1" />
                  <line x1="100" y1="150" x2="150" y2="280" stroke="rgba(34, 211, 238, 0.2)" strokeWidth="1" />
                  <line x1="200" y1="150" x2="150" y2="280" stroke="rgba(34, 211, 238, 0.2)" strokeWidth="1" />
                </g>

                {/* Humanoid Robot Body */}
                <g className={styles.robot}>
                  {/* Head */}
                  <circle cx="150" cy="60" r="20" fill="url(#robotGradient)" stroke="rgba(34, 211, 238, 0.6)" strokeWidth="2" />

                  {/* Eyes */}
                  <circle cx="145" cy="55" r="3" fill="#22d3ee" className={styles.eye} />
                  <circle cx="155" cy="55" r="3" fill="#22d3ee" className={styles.eye} />

                  {/* Torso */}
                  <rect x="135" y="85" width="30" height="40" rx="5" fill="url(#robotGradient)" stroke="rgba(34, 211, 238, 0.6)" strokeWidth="2" className={styles.torso} />

                  {/* Left Arm */}
                  <g className={styles.arm}>
                    <line x1="135" y1="95" x2="100" y2="110" stroke="rgba(34, 211, 238, 0.7)" strokeWidth="6" strokeLinecap="round" />
                    <circle cx="100" cy="110" r="4" fill="#22d3ee" />
                  </g>

                  {/* Right Arm */}
                  <g className={styles.arm}>
                    <line x1="165" y1="95" x2="200" y2="110" stroke="rgba(34, 211, 238, 0.7)" strokeWidth="6" strokeLinecap="round" />
                    <circle cx="200" cy="110" r="4" fill="#22d3ee" />
                  </g>

                  {/* Left Leg */}
                  <g className={styles.leg}>
                    <line x1="140" y1="125" x2="130" y2="170" stroke="rgba(34, 211, 238, 0.7)" strokeWidth="6" strokeLinecap="round" />
                    <circle cx="130" cy="170" r="5" fill="#22d3ee" />
                  </g>

                  {/* Right Leg */}
                  <g className={styles.leg}>
                    <line x1="160" y1="125" x2="170" y2="170" stroke="rgba(34, 211, 238, 0.7)" strokeWidth="6" strokeLinecap="round" />
                    <circle cx="170" cy="170" r="5" fill="#22d3ee" />
                  </g>
                </g>

                {/* Sensor Indicators */}
                <g className={styles.sensors}>
                  <circle cx="150" cy="320" r="2" fill="rgba(251, 146, 60, 0.6)" className={styles.sensor} />
                  <circle cx="120" cy="310" r="2" fill="rgba(251, 146, 60, 0.6)" className={styles.sensor} />
                  <circle cx="180" cy="310" r="2" fill="rgba(251, 146, 60, 0.6)" className={styles.sensor} />
                </g>

                {/* Gradient Definition */}
                <defs>
                  <linearGradient id="robotGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stopColor="rgba(34, 211, 238, 0.3)" />
                    <stop offset="100%" stopColor="rgba(251, 146, 60, 0.2)" />
                  </linearGradient>
                </defs>
              </svg>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default WhyPhysicalAI;
