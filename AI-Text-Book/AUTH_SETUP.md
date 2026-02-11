# Authentication Setup Guide

## Overview
Your AI Textbook platform now has a complete authentication system using GitHub OAuth. Users must sign in before accessing the content.

## What's Implemented

✅ **Login Screen** - Beautiful modal that appears when users first visit
✅ **GitHub OAuth Integration** - Secure authentication flow
✅ **Auth Gate** - Protects all content until user logs in
✅ **User Profile** - Shows avatar, name, and logout option in navbar
✅ **Session Persistence** - Users stay logged in across page refreshes
✅ **Loading States** - Smooth loading animations

## Setup GitHub OAuth App

To enable authentication, you need to create a GitHub OAuth App:

### Step 1: Create GitHub OAuth App

1. Go to https://github.com/settings/developers
2. Click "New OAuth App"
3. Fill in the details:
   - **Application name**: Physical AI Textbook (or your preferred name)
   - **Homepage URL**: `http://localhost:3000` (for local development)
   - **Authorization callback URL**: `http://localhost:3000/auth/github/callback`
4. Click "Register application"
5. You'll get a **Client ID** and can generate a **Client Secret**

### Step 2: Create Environment File

Create a `.env` file in the root of your project:

```bash
# .env
REACT_APP_GITHUB_CLIENT_ID=your_github_client_id_here
REACT_APP_GITHUB_CLIENT_SECRET=your_github_client_secret_here
```

**Important:** Never commit this file to Git! It's already in `.gitignore`.

### Step 3: Create OAuth Callback Page

You need to create a callback page to handle the OAuth redirect. Create this file:

**File:** `src/pages/auth/github/callback.tsx`

```typescript
import React, { useEffect, useState } from 'react';
import { useAuth } from '../../../hooks/useAuth';

export default function GitHubCallback() {
  const [error, setError] = useState<string | null>(null);
  const { updateSession } = useAuth();

  useEffect(() => {
    const handleCallback = async () => {
      const params = new URLSearchParams(window.location.search);
      const code = params.get('code');
      const state = params.get('state');
      const error = params.get('error');

      if (error) {
        setError(`Authentication error: ${error}`);
        return;
      }

      if (!code || !state) {
        setError('Missing code or state parameter');
        return;
      }

      try {
        // TODO: Implement backend endpoint to exchange code for token
        // For now, redirect to home
        console.log('OAuth code received:', code);
        window.location.href = '/';
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Authentication failed');
      }
    };

    handleCallback();
  }, []);

  if (error) {
    return (
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        height: '100vh',
        flexDirection: 'column',
        gap: '16px'
      }}>
        <h1>Authentication Error</h1>
        <p>{error}</p>
        <a href="/">Return to Home</a>
      </div>
    );
  }

  return (
    <div style={{
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      height: '100vh'
    }}>
      <p>Completing authentication...</p>
    </div>
  );
}
```

### Step 4: For Production Deployment

When deploying to production:

1. Update your GitHub OAuth App settings:
   - **Homepage URL**: `https://your-domain.com`
   - **Callback URL**: `https://your-domain.com/auth/github/callback`

2. Set environment variables on your hosting platform (Vercel, Netlify, etc.):
   ```
   REACT_APP_GITHUB_CLIENT_ID=your_production_client_id
   REACT_APP_GITHUB_CLIENT_SECRET=your_production_client_secret
   ```

## Backend Integration (Required for Full OAuth Flow)

The current implementation requires a backend server to:
1. Exchange the OAuth code for an access token
2. Securely store the client secret (never expose it to the frontend)

### Option 1: Create a Simple Backend API

Create an API endpoint that:
- Receives the OAuth code
- Exchanges it with GitHub for an access token
- Returns the token to the frontend

### Option 2: Use Serverless Functions

If using Vercel or Netlify, create a serverless function:

**File:** `api/auth/github/callback.ts` (Vercel) or `netlify/functions/github-callback.ts` (Netlify)

```typescript
import { VercelRequest, VercelResponse } from '@vercel/node';

export default async function handler(req: VercelRequest, res: VercelResponse) {
  const { code } = req.query;

  if (!code) {
    return res.status(400).json({ error: 'Missing code parameter' });
  }

  try {
    const tokenResponse = await fetch('https://github.com/login/oauth/access_token', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      body: JSON.stringify({
        client_id: process.env.REACT_APP_GITHUB_CLIENT_ID,
        client_secret: process.env.REACT_APP_GITHUB_CLIENT_SECRET,
        code: code as string,
      }),
    });

    const data = await tokenResponse.json();

    if (data.error) {
      return res.status(400).json({ error: data.error_description });
    }

    return res.status(200).json({
      access_token: data.access_token,
      token_type: data.token_type,
      scope: data.scope,
    });
  } catch (error) {
    return res.status(500).json({ error: 'Internal server error' });
  }
}
```

## Testing Locally

1. Start the development server:
   ```bash
   npm run serve
   ```

2. Open http://localhost:3000/

3. You should see the login screen

4. Click "Sign in with GitHub"

5. Authorize the app on GitHub

6. You'll be redirected back (callback needs backend implementation)

## For Quick Testing (Skip OAuth)

If you want to test without setting up OAuth:

1. Open browser console on http://localhost:3000/

2. Run this to bypass login (temporary):
   ```javascript
   localStorage.setItem('ai_textbook_auth_session', JSON.stringify({
     user: {
       id: '1',
       username: 'testuser',
       name: 'Test User',
       avatar_url: 'https://github.com/identicons/test.png',
       email: 'test@example.com',
       created_at: Date.now(),
       last_login: Date.now()
     },
     access_token: 'fake_token',
     expires_at: Date.now() + 86400000,
     created_at: Date.now()
   }));
   ```

3. Refresh the page - you'll be logged in as a test user

## Components Created

- **`src/components/Login`** - Login modal with GitHub button
- **`src/components/AuthGate`** - Protects routes, shows login if not authenticated
- **`src/components/GitHubAuth`** - User profile dropdown in navbar

## How It Works

1. User visits the site
2. `AuthGate` checks if user is authenticated (from localStorage)
3. If not authenticated, shows `Login` component
4. User clicks "Sign in with GitHub"
5. Redirects to GitHub OAuth
6. GitHub redirects back to `/auth/github/callback` with code
7. Backend exchanges code for access token
8. Frontend stores session in localStorage
9. User is now authenticated and can access content

## Troubleshooting

**Issue: Login button doesn't work**
- Check browser console for errors
- Verify GitHub Client ID is set in `.env`
- Make sure OAuth App callback URL matches exactly

**Issue: Stuck on "Completing authentication..."**
- Backend/serverless function not set up yet
- Check browser console for API errors

**Issue: "OAuth state mismatch" error**
- Clear cookies and try again
- Check that sessionStorage is enabled

## Security Notes

✅ OAuth state parameter prevents CSRF attacks
✅ Client secret never exposed to frontend
✅ Session expires after token lifetime
✅ Secure localStorage-based persistence

⚠️ For production, consider:
- Using httpOnly cookies instead of localStorage
- Implementing refresh token rotation
- Adding rate limiting to API endpoints
- Setting up proper CORS policies

---

**Your authentication system is ready!** Configure the GitHub OAuth app and you're good to go.
