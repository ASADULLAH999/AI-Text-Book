import React, { useState, useEffect } from 'react';
import { useCookieConsent } from '../../hooks/useCookieConsent';
import styles from './styles.module.css';

export default function CookieConsent() {
  const {
    showBanner,
    showPreferencesModal,
    preferences,
    acceptAll,
    rejectNonEssential,
    saveCustomPreferences,
    openPreferencesModal,
    closePreferencesModal,
    closeBanner,
  } = useCookieConsent();

  const [analyticsEnabled, setAnalyticsEnabled] = useState(false);
  const [preferencesEnabled, setPreferencesEnabled] = useState(false);

  // Fix: sync toggle state when preferences load from localStorage
  useEffect(() => {
    if (preferences) {
      setAnalyticsEnabled(preferences.analytics ?? false);
      setPreferencesEnabled(preferences.preferences ?? false);
    }
  }, [preferences]);

  const handleCustomize = () => {
    closeBanner();
    openPreferencesModal();
  };

  const handleSaveCustom = () => {
    saveCustomPreferences(analyticsEnabled, preferencesEnabled);
  };

  if (!showBanner && !showPreferencesModal) {
    return null;
  }

  return (
    <>
      {/* GDPR Banner */}
      {showBanner && (
        <div className={styles.banner} role="alertdialog" aria-label="Cookie consent">
          <div className={styles.bannerContent}>
            <div className={styles.bannerText}>
              <h3 className={styles.bannerTitle}>🍪 We Value Your Privacy</h3>
              <p className={styles.bannerDescription}>
                We use cookies to enhance your browsing experience, provide personalized content,
                and analyze our traffic. By clicking "Accept All", you consent to our use of
                cookies.{' '}
                <a href="/privacy-policy" className={styles.privacyLink}>
                  Privacy Policy
                </a>
              </p>
            </div>
            <button
              onClick={rejectNonEssential}
              className={styles.bannerDismiss}
              aria-label="Dismiss cookie banner"
            >
              ✕
            </button>
            <div className={styles.bannerButtons}>
              <button
                onClick={acceptAll}
                className={`${styles.button} ${styles.buttonPrimary}`}
                aria-label="Accept all cookies"
              >
                Accept All
              </button>
              <button
                onClick={rejectNonEssential}
                className={`${styles.button} ${styles.buttonSecondary}`}
                aria-label="Reject non-essential cookies"
              >
                Reject Non-Essential
              </button>
              <button
                onClick={handleCustomize}
                className={`${styles.button} ${styles.buttonOutline}`}
                aria-label="Customize cookie preferences"
              >
                Customize
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Preferences Modal */}
      {showPreferencesModal && (
        <div
          className={styles.modalOverlay}
          onClick={closePreferencesModal}
          role="dialog"
          aria-modal="true"
          aria-labelledby="preferences-modal-title"
        >
          <div className={styles.modal} onClick={(e) => e.stopPropagation()}>
            <div className={styles.modalHeader}>
              <h2 id="preferences-modal-title" className={styles.modalTitle}>
                Cookie Preferences
              </h2>
              <button
                onClick={closePreferencesModal}
                className={styles.closeButton}
                aria-label="Close preferences modal"
              >
                ✕
              </button>
            </div>

            <div className={styles.modalBody}>
              <p className={styles.modalDescription}>
                Manage your cookie preferences below. Essential cookies are required for the site
                to function and cannot be disabled.
              </p>

              {/* Essential Cookies */}
              <div className={styles.cookieCategory}>
                <div className={styles.categoryHeader}>
                  <div>
                    <h3 className={styles.categoryTitle}>Essential Cookies</h3>
                    <p className={styles.categoryDescription}>
                      Required for the website to function properly. These cannot be disabled.
                    </p>
                  </div>
                  <div className={styles.toggle}>
                    <input
                      type="checkbox"
                      id="essential"
                      checked={true}
                      disabled
                      className={styles.toggleInput}
                    />
                    <label htmlFor="essential" className={styles.toggleLabel}>
                      <span className={styles.toggleSwitch} />
                    </label>
                  </div>
                </div>
              </div>

              {/* Analytics Cookies */}
              <div className={styles.cookieCategory}>
                <div className={styles.categoryHeader}>
                  <div>
                    <h3 className={styles.categoryTitle}>Analytics Cookies</h3>
                    <p className={styles.categoryDescription}>
                      Help us understand how visitors interact with our website by collecting and
                      reporting information anonymously.
                    </p>
                  </div>
                  <div className={styles.toggle}>
                    <input
                      type="checkbox"
                      id="analytics"
                      checked={analyticsEnabled}
                      onChange={(e) => setAnalyticsEnabled(e.target.checked)}
                      className={styles.toggleInput}
                    />
                    <label htmlFor="analytics" className={styles.toggleLabel}>
                      <span className={styles.toggleSwitch} />
                    </label>
                  </div>
                </div>
              </div>

              {/* Preferences Cookies */}
              <div className={styles.cookieCategory}>
                <div className={styles.categoryHeader}>
                  <div>
                    <h3 className={styles.categoryTitle}>Preference Cookies</h3>
                    <p className={styles.categoryDescription}>
                      Enable the website to remember information that changes the way the site
                      behaves or looks, like your preferred language or theme.
                    </p>
                  </div>
                  <div className={styles.toggle}>
                    <input
                      type="checkbox"
                      id="preferences"
                      checked={preferencesEnabled}
                      onChange={(e) => setPreferencesEnabled(e.target.checked)}
                      className={styles.toggleInput}
                    />
                    <label htmlFor="preferences" className={styles.toggleLabel}>
                      <span className={styles.toggleSwitch} />
                    </label>
                  </div>
                </div>
              </div>
            </div>

            <div className={styles.modalFooter}>
              <button
                onClick={handleSaveCustom}
                className={`${styles.button} ${styles.buttonPrimary}`}
                aria-label="Save custom cookie preferences"
              >
                Save Preferences
              </button>
              <button
                onClick={closePreferencesModal}
                className={`${styles.button} ${styles.buttonSecondary}`}
                aria-label="Cancel and close modal"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
