import React from 'react';
import ModuleCard from '../ModuleCard';
import styles from './styles.module.css';

interface Module {
  id: string;
  title: string;
  description: string;
  icon: React.ReactNode;
  color: string;
}

interface ModuleCardsProps {
  modules?: Module[];
  onModuleClick?: (moduleId: string) => void;
}

const defaultModules: Module[] = [
  {
    id: 'module-1',
    title: 'Module 1: ROS 2 Fundamentals',
    description: 'Master Robot Operating System 2 core concepts, nodes, topics, services, and actions for building robotics applications.',
    icon: '🤖',
    color: 'cyan',
  },
  {
    id: 'module-2',
    title: 'Module 2: Digital Twins & Simulation',
    description: 'Learn digital twin concepts, Gazebo simulation environment, and Unity 3D integration for virtual testing.',
    icon: '🌐',
    color: 'blue',
  },
  {
    id: 'module-3',
    title: 'Module 3: NVIDIA Isaac Sim',
    description: 'Advanced robotics simulation with NVIDIA Isaac Sim platform for high-fidelity physics and AI integration.',
    icon: '⚡',
    color: 'purple',
  },
  {
    id: 'module-4',
    title: 'Module 4: Voice to Action & Capstone',
    description: 'Build voice interfaces, integrate large language models, and complete comprehensive capstone projects.',
    icon: '🎤',
    color: 'orange',
  },
];

export const ModuleCards: React.FC<ModuleCardsProps> = ({
  modules = defaultModules,
  onModuleClick,
}) => {
  return (
    <section className={styles.section}>
      <div className={styles.container}>
        <div className={styles.header}>
          <h2 className={styles.title}>Our Learning Modules</h2>
          <p className={styles.subtitle}>
            Structured curriculum from fundamentals to advanced capstone projects
          </p>
        </div>

        <div className={styles.grid}>
          {modules.map((module, index) => (
            <ModuleCard
              key={module.id}
              {...module}
              index={index}
              onClick={() => onModuleClick?.(module.id)}
            />
          ))}
        </div>
      </div>
    </section>
  );
};

export default ModuleCards;
