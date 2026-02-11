import React, { useState } from 'react';
import styles from './styles.module.css';

interface HardwareOption {
  name: string;
  specs: Array<{ label: string; value: string }>;
  pricing?: string;
  pros?: string[];
  cons?: string[];
}

interface HardwareTabsProps {
  tabs?: Array<{ title: string; content: HardwareOption }>;
}

const defaultTabs: Array<{ title: string; content: HardwareOption }> = [
  {
    title: 'Workstation',
    content: {
      name: 'Development Workstation',
      specs: [
        { label: 'CPU', value: 'Intel i7/i9 or AMD Ryzen 7/9' },
        { label: 'RAM', value: '32GB+ DDR4/DDR5' },
        { label: 'GPU', value: 'NVIDIA RTX 3080/4080+' },
        { label: 'Storage', value: '1TB NVMe SSD' },
        { label: 'OS', value: 'Ubuntu 22.04 LTS' },
        { label: 'Software', value: 'ROS 2 Humble, Gazebo, Isaac Sim' },
      ],
      pricing: '$1500 - $3000',
    },
  },
  {
    title: 'Edge Kit',
    content: {
      name: 'Jetson Edge AI Kit',
      specs: [
        { label: 'Platform', value: 'NVIDIA Jetson Orin Nano' },
        { label: 'CPU Cores', value: '8x ARM cores' },
        { label: 'GPU', value: '40 NVIDIA CUDA cores' },
        { label: 'RAM', value: '8GB LPDDR5' },
        { label: 'Storage', value: '128GB NVMe + microSD' },
        { label: 'Power', value: '5-15W typical' },
      ],
      pricing: '$199 - $249',
    },
  },
  {
    title: 'Robot Lab',
    content: {
      name: 'Humanoid Robot Lab',
      specs: [
        { label: 'Robot', value: 'Boston Dynamics Spot or equivalent' },
        { label: 'Controllers', value: 'Multiple Jetson Orin Xavier' },
        { label: 'Sensors', value: 'LiDAR, RGB-D, IMU, GPS' },
        { label: 'Network', value: 'Dedicated Wi-Fi 6+ Network' },
        { label: 'Safety', value: 'Emergency stop systems' },
        { label: 'Maintenance', value: 'Annual support contract' },
      ],
      pricing: '$250K+ (Annual lease: $50K)' ,
      pros: [
        'Real-world robotics experience',
        'Hands-on hardware control',
        'Advanced sensor integration',
        'Production-ready deployment',
      ],
      cons: [
        'Significant investment required',
        'Requires physical space',
        'Maintenance overhead',
        'Limited availability',
      ],
    },
  },
  {
    title: 'Cloud Option',
    content: {
      name: 'AWS EC2 + RoboMaker',
      specs: [
        { label: 'Instance Type', value: 'p3.2xlarge or g4dn.12xlarge' },
        { label: 'GPUs', value: '8x V100 or 4x A100' },
        { label: 'vCPU', value: '96 vCPU' },
        { label: 'RAM', value: '488GB' },
        { label: 'Service', value: 'AWS RoboMaker + Gazebo' },
        { label: 'Billing', value: 'Pay-as-you-go' },
      ],
      pricing: '$2-5 per hour (GPU compute)',
      pros: [
        'No hardware to purchase',
        'Scalable resources',
        'Built-in simulation',
        'Global accessibility',
      ],
      cons: [
        'Ongoing monthly costs',
        'Network latency',
        'Dependency on cloud provider',
        'Data egress charges',
      ],
    },
  },
];

export const HardwareTabs: React.FC<HardwareTabsProps> = ({ tabs = defaultTabs }) => {
  const [activeTab, setActiveTab] = useState(0);

  return (
    <section className={styles.section}>
      <div className={styles.container}>
        <div className={styles.header}>
          <h2 className={styles.title}>Hardware Requirements</h2>
          <p className={styles.subtitle}>Choose the setup that fits your learning path</p>
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
            <div className={styles.hardwareCard}>
              <div className={styles.cardHeader}>
                <h3 className={styles.hardwareName}>{tabs[activeTab].content.name}</h3>
                {tabs[activeTab].content.pricing && (
                  <span className={styles.pricing}>{tabs[activeTab].content.pricing}</span>
                )}
              </div>

              <div className={styles.specsTable}>
                <table>
                  <tbody>
                    {tabs[activeTab].content.specs.map((spec, index) => (
                      <tr key={index}>
                        <td className={styles.specLabel}>{spec.label}</td>
                        <td className={styles.specValue}>{spec.value}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {tabs[activeTab].content.pros && tabs[activeTab].content.cons && (
                <div className={styles.prosConsContainer}>
                  <div className={styles.prosList}>
                    <h4 className={styles.prosConsTitle}>Advantages</h4>
                    <ul>
                      {tabs[activeTab].content.pros.map((pro, index) => (
                        <li key={index}>
                          <span className={styles.prosIcon}>✓</span>
                          {pro}
                        </li>
                      ))}
                    </ul>
                  </div>

                  <div className={styles.consList}>
                    <h4 className={styles.prosConsTitle}>Considerations</h4>
                    <ul>
                      {tabs[activeTab].content.cons.map((con, index) => (
                        <li key={index}>
                          <span className={styles.consIcon}>⚠</span>
                          {con}
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default HardwareTabs;
