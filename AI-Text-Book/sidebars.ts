import type {SidebarsConfig} from '@docusaurus/plugin-content-docs';

const sidebars: SidebarsConfig = {
  tutorialSidebar: [
    {
      type: 'category',
      label: 'Module 1: ROS 2 & Robotics Fundamentals',
      items: [
        'module-1-ros2/index',
        'module-1-ros2/introduction',
        'module-1-ros2/core-concepts',
        'module-1-ros2/code-examples',
        'module-1-ros2/hands-on-tutorial',
        'module-1-ros2/best-practices',
        'module-1-ros2/quiz',
        'module-1-ros2/summary',
      ],
    },
    {
      type: 'category',
      label: 'Module 2: Digital Twins & Simulation',
      items: [
        'module-2-simulation/index',
        'module-2-simulation/introduction',
        'module-2-simulation/core-concepts',
        'module-2-simulation/code-examples',
        'module-2-simulation/hands-on-tutorial',
        'module-2-simulation/best-practices',
        'module-2-simulation/quiz',
        'module-2-simulation/summary',
      ],
    },
    {
      type: 'category',
      label: 'Module 3: NVIDIA Isaac Sim',
      items: [
        'module-3-isaac/index',
        'module-3-isaac/introduction',
        'module-3-isaac/core-concepts',
        'module-3-isaac/code-examples',
        'module-3-isaac/hands-on-tutorial',
        'module-3-isaac/best-practices',
        'module-3-isaac/quiz',
        'module-3-isaac/summary',
      ],
    },
    {
      type: 'category',
      label: 'Module 4: Voice to Action & Capstone',
      items: [
        'module-4-voice/index',
        'module-4-voice/introduction',
        'module-4-voice/core-concepts',
        'module-4-voice/code-examples',
        'module-4-voice/hands-on-tutorial',
        'module-4-voice/best-practices',
        'module-4-voice/quiz',
        'module-4-voice/summary',
      ],
    },
  ],
};

export default sidebars;
