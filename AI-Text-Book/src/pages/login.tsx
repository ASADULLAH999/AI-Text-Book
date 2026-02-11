import React, { useEffect } from 'react';
import { useHistory } from '@docusaurus/router';

// AUTHENTICATION DISABLED - Login page redirects to documentation
export default function LoginPage() {
  const history = useHistory();

  useEffect(() => {
    // Redirect to documentation immediately
    history.replace('/docs/module-1-ros2/');
  }, [history]);

  return (
    <div style={{
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      minHeight: '100vh',
      background: 'var(--ifm-background-color)',
    }}>
      <div style={{ textAlign: 'center' }}>
        <p>Redirecting to content...</p>
      </div>
    </div>
  );
}

/* ORIGINAL LOGIN PAGE - DISABLED
import React from 'react';
import Layout from '@theme/Layout';
import Login from '../components/Login';
import BrowserOnly from '@docusaurus/BrowserOnly';

export default function LoginPage() {
  return (
    <Layout title="Login" description="Login to access the AI Textbook content" noFooter>
      <BrowserOnly fallback={
        <div style={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          minHeight: '100vh',
          background: 'var(--ifm-background-color)',
        }}>
          <div style={{ textAlign: 'center' }}>
            <div style={{
              width: '40px',
              height: '40px',
              border: '4px solid #f3f3f3',
              borderTop: '4px solid #3498db',
              borderRadius: '50%',
              animation: 'spin 1s linear infinite',
              margin: '0 auto 1rem',
            }} />
            <p>Loading...</p>
          </div>
        </div>
      }>
        {() => <Login />}
      </BrowserOnly>
    </Layout>
  );
}
*/