import React from 'react';
import { useAppState } from '../../context/AppStateContext';
import styles from './styles.module.css';

export const Navbar: React.FC = () => {
  const { state } = useAppState();

  return (
    <nav className={styles.navbar}>
      <div className={styles.container}>
        {/* Logo */}
        <div className={styles.logo}>
          <span className={styles.logoText}>Physical AI</span>
        </div>

        {/* Navigation Links */}
        <div className={styles.navLinks}>
          <a href="/docs/module-1-ros2/" className={styles.link}>
            Docs
          </a>
          <a href="#" className={styles.link}>
            Modules
          </a>
          <a href="#" className={styles.link}>
            Resources
          </a>
        </div>

        {/* Right Section - Search, Language */}
        <div className={styles.rightSection}>
          {/* Search Placeholder */}
          <button className={styles.searchButton} aria-label="Search" title="Search (Cmd+K)">
            <span>🔍</span>
          </button>

          {/* Language Selector Placeholder */}
          <select className={styles.languageSelect} defaultValue={state.language} aria-label="Select language">
            <option value="en">EN</option>
            <option value="ur">اردو</option>
            <option value="ar">العربية</option>
            <option value="zh">中文</option>
            <option value="es">Español</option>
          </select>

        </div>
      </div>
    </nav>
  );
};
