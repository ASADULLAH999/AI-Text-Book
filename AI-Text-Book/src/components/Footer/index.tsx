import React from 'react';
import { useCookieConsent } from '../../hooks/useCookieConsent';
import styles from './styles.module.css';

export const Footer: React.FC = () => {
  const currentYear = new Date().getFullYear();
  const { openPreferencesModal } = useCookieConsent();

  return (
    <footer className={styles.footer}>
      <div className={styles.container}>
        {/* Column 1: Product */}
        <div className={styles.column}>
          <h4 className={styles.columnTitle}>Product</h4>
          <ul className={styles.linkList}>
            <li>
              <a href="/docs/module-1-ros2/" className={styles.link}>
                Documentation
              </a>
            </li>
            <li>
              <a href="#" className={styles.link}>
                Modules
              </a>
            </li>
            <li>
              <a href="#" className={styles.link}>
                Roadmap
              </a>
            </li>
            <li>
              <a href="#" className={styles.link}>
                GitHub
              </a>
            </li>
          </ul>
        </div>

        {/* Column 2: Learning */}
        <div className={styles.column}>
          <h4 className={styles.columnTitle}>Learning</h4>
          <ul className={styles.linkList}>
            <li>
              <a href="#" className={styles.link}>
                Getting Started
              </a>
            </li>
            <li>
              <a href="#" className={styles.link}>
                Tutorial
              </a>
            </li>
            <li>
              <a href="#" className={styles.link}>
                FAQ
              </a>
            </li>
            <li>
              <a href="#" className={styles.link}>
                Community
              </a>
            </li>
          </ul>
        </div>

        {/* Column 3: Legal */}
        <div className={styles.column}>
          <h4 className={styles.columnTitle}>Legal</h4>
          <ul className={styles.linkList}>
            <li>
              <a href="#" className={styles.link}>
                Privacy Policy
              </a>
            </li>
            <li>
              <a href="#" className={styles.link}>
                Terms of Service
              </a>
            </li>
            <li>
              <button
                onClick={openPreferencesModal}
                className={styles.link}
                style={{ background: 'none', border: 'none', cursor: 'pointer', padding: 0 }}
              >
                Cookie Settings
              </button>
            </li>
            <li>
              <a href="#" className={styles.link}>
                License
              </a>
            </li>
          </ul>
        </div>

        {/* Column 4: Social */}
        <div className={styles.column}>
          <h4 className={styles.columnTitle}>Follow Us</h4>
          <div className={styles.socialLinks}>
            <a href="#" className={styles.socialLink} aria-label="GitHub">
              <span>GitHub</span>
            </a>
            <a href="#" className={styles.socialLink} aria-label="Twitter">
              <span>Twitter</span>
            </a>
            <a href="#" className={styles.socialLink} aria-label="Discord">
              <span>Discord</span>
            </a>
            <a href="#" className={styles.socialLink} aria-label="YouTube">
              <span>YouTube</span>
            </a>
          </div>
        </div>
      </div>

      {/* Bottom Section */}
      <div className={styles.bottom}>
        <div className={styles.copyright}>
          <p>
            © {currentYear} Physical AI & Humanoid Robotics Textbook. All rights reserved.
          </p>
        </div>
        <div className={styles.credits}>
          <p>
            Built with <span className={styles.heart}>❤</span> by the Anthropic Education Team
          </p>
        </div>
      </div>
    </footer>
  );
};
