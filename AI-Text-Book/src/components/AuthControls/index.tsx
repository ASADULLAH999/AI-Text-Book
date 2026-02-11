import React, { useState, useEffect } from 'react';
import { useAuth } from '../../hooks/useAuth';
import Link from '@docusaurus/Link';
import styles from './styles.module.css';

export default function UserAuth() {
  const { user, isAuthenticated, isLoading, logout } = useAuth();
  const [showDropdown, setShowDropdown] = useState(false);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      const target = event.target as HTMLElement;
      if (!target.closest(`.${styles.authContainer}`)) {
        setShowDropdown(false);
      }
    };

    if (showDropdown) {
      document.addEventListener('click', handleClickOutside);
      return () => document.removeEventListener('click', handleClickOutside);
    }
  }, [showDropdown]);

  if (isLoading) {
    return (
      <div className={styles.authContainer}>
        <div className={styles.loading}>Loading...</div>
      </div>
    );
  }

  if (!isAuthenticated || !user) {
    // Show login/signup buttons for non-authenticated users
    return (
      <div className={styles.authButtons}>
        <Link to="/login" className={styles.loginButton}>
          Login
        </Link>
        <Link to="/login" className={styles.signupButton}>
          Sign Up
        </Link>
      </div>
    );
  }

  // Get user initials for avatar
  const getInitials = (name?: string, email?: string) => {
    if (name) {
      return name
        .split(' ')
        .map(n => n[0])
        .join('')
        .toUpperCase()
        .slice(0, 2);
    }
    if (email) {
      return email[0].toUpperCase();
    }
    return 'U';
  };

  const initials = getInitials(user.name, user.email);

  return (
    <div className={styles.authContainer}>
      <div className={styles.userProfile}>
        <button
          onClick={() => setShowDropdown(!showDropdown)}
          className={styles.avatarButton}
          aria-label="User menu"
          aria-expanded={showDropdown}
        >
          {user.avatar_url ? (
            <img
              src={user.avatar_url}
              alt={user.name || user.username}
              className={styles.avatar}
            />
          ) : (
            <div className={styles.avatarPlaceholder}>
              {initials}
            </div>
          )}
        </button>

        {showDropdown && (
          <div className={styles.dropdown}>
            <div className={styles.dropdownHeader}>
              <div className={styles.userName}>{user.name || user.username}</div>
              {user.email && <div className={styles.userEmail}>{user.email}</div>}
            </div>

            <div className={styles.dropdownDivider} />

            <div className={styles.dropdownActions}>
              <button onClick={() => logout()} className={styles.dropdownItem}>
                <svg
                  className={styles.dropdownIcon}
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                >
                  <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
                  <polyline points="16 17 21 12 16 7" />
                  <line x1="21" y1="12" x2="9" y2="12" />
                </svg>
                Sign Out
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
