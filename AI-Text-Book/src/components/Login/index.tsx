import React, { useState } from 'react';
import { useAuth } from '../../hooks/useAuth';
import { useHistory } from '@docusaurus/router';
import ExecutionEnvironment from '@docusaurus/ExecutionEnvironment';
import styles from './styles.module.css';

export default function Login() {
  const { signIn, signUp, isLoading } = useAuth();
  const history = useHistory();
  const [mode, setMode] = useState<'signin' | 'signup'>('signin');
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    // Basic validation
    if (mode === 'signup' && !name) {
      setError('Please enter your name');
      setLoading(false);
      return;
    }

    if (!email || !password) {
      setError('Please fill in all fields');
      setLoading(false);
      return;
    }

    if (password.length < 6) {
      setError('Password must be at least 6 characters');
      setLoading(false);
      return;
    }

    try {
      const result = mode === 'signin'
        ? await signIn(email, password)
        : await signUp(email, password, name);

      if (!result.success) {
        setError(result.error || 'Authentication failed');
        console.error('Auth failed:', result.error);
      } else {
        console.log('Auth successful, redirecting...');
        // Success! Redirect to docs with full page reload to ensure state sync
        if (ExecutionEnvironment.canUseDOM) {
          // Use window.location for full page reload to sync auth state
          window.location.href = '/docs/module-1-ros2/';
        }
      }
    } catch (err) {
      console.error('Auth exception:', err);
      setError('An error occurred. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={styles.overlay}>
      <div className={styles.loginCard}>
        <div className={styles.header}>
          <div className={styles.logo}>
            <img src="/img/logo.svg" alt="Physical AI" className={styles.logoImg} />
            <h1 className={styles.title}>Physical AI & Humanoid Robotics</h1>
          </div>
          <p className={styles.subtitle}>
            Learn AI, Robotics, and Computer Vision from the Ground Up
          </p>
        </div>

        <div className={styles.content}>
          <div className={styles.toggleContainer}>
            <button
              className={`${styles.toggleButton} ${mode === 'signin' ? styles.active : ''}`}
              onClick={() => setMode('signin')}
              type="button"
            >
              Sign In
            </button>
            <button
              className={`${styles.toggleButton} ${mode === 'signup' ? styles.active : ''}`}
              onClick={() => setMode('signup')}
              type="button"
            >
              Sign Up
            </button>
          </div>

          <form onSubmit={handleSubmit} className={styles.form}>
            {mode === 'signup' && (
              <div className={styles.inputGroup}>
                <label htmlFor="name" className={styles.label}>Name</label>
                <input
                  id="name"
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className={styles.input}
                  placeholder="Enter your full name"
                  disabled={loading || isLoading}
                  required
                />
              </div>
            )}

            <div className={styles.inputGroup}>
              <label htmlFor="email" className={styles.label}>Email</label>
              <input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className={styles.input}
                placeholder="Enter your email"
                disabled={loading || isLoading}
                required
              />
            </div>

            <div className={styles.inputGroup}>
              <label htmlFor="password" className={styles.label}>Password</label>
              <input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className={styles.input}
                placeholder="Enter your password"
                disabled={loading || isLoading}
                required
              />
            </div>

            {error && (
              <div className={styles.errorMessage}>
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={loading || isLoading}
              className={styles.submitButton}
            >
              {loading || isLoading ? (
                <div className={styles.spinner} />
              ) : (
                mode === 'signin' ? 'Sign In' : 'Create Account'
              )}
            </button>
          </form>

          <div className={styles.features}>
            <div className={styles.feature}>
              <svg className={styles.featureIcon} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
              </svg>
              <span>Track Progress</span>
            </div>
            <div className={styles.feature}>
              <svg className={styles.featureIcon} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span>Take Quizzes</span>
            </div>
            <div className={styles.feature}>
              <svg className={styles.featureIcon} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
              <span>Learn Fast</span>
            </div>
          </div>
        </div>

        <div className={styles.footer}>
          <p className={styles.footerText}>
            Free and open-source learning platform for AI enthusiasts
          </p>
        </div>
      </div>
    </div>
  );
}
