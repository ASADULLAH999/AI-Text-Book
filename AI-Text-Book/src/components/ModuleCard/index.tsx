import React, { useRef, useState } from 'react';
import styles from './styles.module.css';

interface ModuleCardProps {
  id: string;
  title: string;
  description: string;
  icon: React.ReactNode;
  color: string;
  index?: number;
  onClick?: () => void;
}

export const ModuleCard: React.FC<ModuleCardProps> = ({ id, title, description, icon, color, index = 0, onClick }) => {
  const cardRef = useRef<HTMLDivElement>(null);
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });

  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!cardRef.current) return;

    const rect = cardRef.current.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    setMousePosition({ x, y });

    // Create glow effect
    cardRef.current.style.setProperty('--mouse-x', `${x}px`);
    cardRef.current.style.setProperty('--mouse-y', `${y}px`);
  };

  const handleMouseLeave = () => {
    setMousePosition({ x: 0, y: 0 });
  };

  return (
    <div
      ref={cardRef}
      className={styles.card}
      style={{ animationDelay: `${index * 0.1}s` }}
      onClick={onClick}
      data-color={color}
    >
      <div className={styles.glassEffect} onMouseMove={handleMouseMove} onMouseLeave={handleMouseLeave}>
        <div className={styles.gradient} />

        <div className={styles.icon}>{icon}</div>

        <h3 className={styles.title}>{title}</h3>

        <p className={styles.description}>{description}</p>

        <div className={styles.arrow}>
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <line x1="5" y1="12" x2="19" y2="12" />
            <polyline points="12 5 19 12 12 19" />
          </svg>
        </div>
      </div>

      <div className={styles.shimmer} />
    </div>
  );
};

export default ModuleCard;
