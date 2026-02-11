# Contract: Auth Service

**Created**: 2026-01-17 | **Feature**: 001-platform-implementation

---

## Overview

The Auth Service manages GitHub OAuth 2.0 authentication, token lifecycle, session management, and logout flows. This is the single source of truth for user authentication state.

---

## Interface

### Service Methods

#### `login()`

Initiates GitHub OAuth flow.

```typescript
function login(): void

// What it does:
// 1. Generate secure random state token
// 2. Redirect user to GitHub OAuth endpoint
// 3. GitHub redirects to /auth/github/callback with code + state
// 4. Exchange code for access token + refresh token
// 5. Store User object in localStorage
// 6. Redirect to dashboard

// No parameters

// Returns: void (redirect side effect)

// Example:
authService.login()  // User sees GitHub auth dialog
```

#### `handleCallback(code: string, state: string)`

Process OAuth callback after user approves on GitHub.

```typescript
function handleCallback(code: string, state: string): Promise<User>

// Parameters:
// - code (string): Authorization code from GitHub
// - state (string): CSRF token (must match previously generated state)

// Returns: Promise<User>
// - Resolves with User object if successful
// - Rejects with Error if state mismatch or token exchange fails

// Errors:
// - "State mismatch" (state parameter doesn't match)
// - "Token exchange failed" (GitHub API error)
// - "Network error" (connectivity issue)

// Example:
const user = await authService.handleCallback(code, state)
console.log(user.username)  // "studentname"
```

#### `getCurrentUser()`

Get currently authenticated user from localStorage.

```typescript
function getCurrentUser(): User | null

// Returns: User object if logged in, null if not authenticated

// Example:
const user = authService.getCurrentUser()
if (user) {
  console.log(`Welcome, ${user.username}!`)
}
```

#### `isAuthenticated()`

Check if user is currently authenticated.

```typescript
function isAuthenticated(): boolean

// Returns: true if user logged in, false otherwise

// Example:
if (authService.isAuthenticated()) {
  showQuizButton()
} else {
  showLoginPrompt()
}
```

#### `refreshToken()`

Silently refresh access token using refresh token (Clarification Q2).

```typescript
function refreshToken(): Promise<User>

// What it does:
// 1. Check if current token expires in < 5 minutes
// 2. If yes, use refresh_token to get new access_token
// 3. Update localStorage with new token + expiry
// 4. Return updated User object

// Returns: Promise<User> (updated with new tokens)

// Errors:
// - "Refresh failed" (refresh token expired or revoked)
// - "Network error" (connectivity issue)

// Note: This is called silently before API requests
// Only prompts login if refresh fails (not transparent to user)

// Example:
try {
  const user = await authService.refreshToken()
  console.log('Token refreshed')
} catch (error) {
  // Refresh failed - prompt user to re-login
  authService.promptRelogin()
}
```

#### `logout()`

Clear session and log user out.

```typescript
function logout(): void

// What it does:
// 1. Clear localStorage["auth"]
// 2. Clear user-specific data (progress, quizzes)
// 3. Clear session state (Context, Redux, etc.)
// 4. Redirect to homepage
// 5. Display "Logged out" confirmation

// No parameters

// Returns: void

// Side effects:
// - localStorage cleared
// - All user data cleared from memory
// - User redirected to /

// Example:
authService.logout()  // User sees "Logged out" message
```

#### `promptRelogin()`

Show re-login prompt when token refresh fails.

```typescript
function promptRelogin(): void

// What it does:
// 1. Display modal: "Session expired. Please log in again."
// 2. Show "Login with GitHub" button
// 3. If user clicks button, call login() to restart OAuth flow
// 4. If user closes modal, remain on current page (read-only mode)

// Returns: void

// Side effects:
// - Modal displays
// - User can click button to login again

// Example:
authService.promptRelogin()
// User sees modal and clicks "Login with GitHub"
// OAuth flow starts again
```

---

## State Management

### localStorage Schema

```typescript
interface AuthState {
  github_id: string;              // Unique GitHub user ID
  username: string;               // GitHub username
  email?: string;                 // GitHub email (optional)
  avatar_url: string;             // Avatar for header display
  access_token: string;           // OAuth access token (1 hour lifetime)
  refresh_token: string;          // OAuth refresh token (6 months lifetime)
  token_expires_at: number;       // Unix timestamp (ms) when access_token expires
  last_refresh: number;           // Unix timestamp (ms) of last refresh
  created_at: number;             // First login timestamp
  last_login: number;             // Most recent login timestamp
}
```

### Storage Operations

```typescript
// Store user (after successful OAuth exchange)
localStorage.setItem('auth', JSON.stringify(user))

// Retrieve user
const user = JSON.parse(localStorage.getItem('auth') || 'null')

// Clear user (logout)
localStorage.removeItem('auth')

// Check if stored data exists
const isLoggedIn = localStorage.getItem('auth') !== null
```

---

## OAuth Flow Sequence

### Initial Login

```
1. User clicks "Login with GitHub" button
2. authService.login() generates state token
3. Redirect to: https://github.com/login/oauth/authorize
   - client_id: (from .env)
   - redirect_uri: http://localhost:3000/auth/github/callback
   - scope: user:email (read-only access)
   - state: (random token for CSRF prevention)
4. GitHub shows permission prompt
5. User approves
6. Redirect back to: /auth/github/callback?code=xxx&state=yyy
7. authService.handleCallback(code, state) called
8. Backend exchanges code for tokens (using client secret)
9. Store User in localStorage
10. Redirect to dashboard (/docs/module-1-ros2)
11. Display avatar + username in header
```

### Token Refresh (Silent)

```
1. Before API call, check token_expires_at
2. If expires_at < now + 5 min:
   a. Call authService.refreshToken()
   b. Use refresh_token to get new access_token
   c. Update localStorage with new tokens
   d. Proceed with API call
3. If refresh fails:
   a. Call authService.promptRelogin()
   b. Show modal to user
   c. User clicks "Login again"
   d. Start login flow again
```

### Logout

```
1. User clicks "Logout" in header
2. authService.logout() called
3. Clear localStorage["auth"]
4. Clear all user data
5. Redirect to homepage
6. Show "Logged out" confirmation
```

---

## Error Handling

### Error Cases

| Error | Cause | Recovery |
|-------|-------|----------|
| "State mismatch" | CSRF attack detected | Fail silently; user stays on login page |
| "Token exchange failed" | Invalid code or network error | Retry login flow |
| "Refresh failed" | Refresh token expired/revoked | Call promptRelogin() |
| "Network error" | No connectivity | Retry after 5s; show offline banner |
| "Invalid token format" | Corrupted localStorage | Clear and restart login |

### Error Handling Pattern

```typescript
try {
  const user = await authService.handleCallback(code, state)
  // Success - continue
} catch (error) {
  if (error.message === 'State mismatch') {
    // CSRF attack - silent fail
    redirectTo('/login')
  } else if (error.message === 'Token exchange failed') {
    // Retry login
    showErrorModal('Login failed. Please try again.')
  } else {
    // Unknown error
    showErrorModal(error.message)
  }
}
```

---

## Integration Points

### With Header Component

```typescript
// Header displays login button if not authenticated
if (!authService.isAuthenticated()) {
  return <LoginButton onClick={() => authService.login()} />
}

// Header displays user avatar if authenticated
const user = authService.getCurrentUser()
return <UserAvatar src={user.avatar_url} alt={user.username} />
```

### With Quiz Component

```typescript
// Quiz checks authentication before loading
const QuizContainer = () => {
  if (!authService.isAuthenticated()) {
    return <LoginPrompt />
  }

  return <Quiz />
}
```

### With Progress Service

```typescript
// Progress service stores user_id from auth
const userId = authService.getCurrentUser()?.github_id
progressService.saveProgress(userId, progress)
```

### With API Requests (Future)

```typescript
// Before making API call, ensure token is valid
await authService.refreshToken()  // Silent refresh if needed
const user = authService.getCurrentUser()

// Include token in request header
const response = await fetch('/api/user', {
  headers: {
    'Authorization': `Bearer ${user.access_token}`
  }
})
```

---

## TypeScript Types

```typescript
export interface User {
  github_id: string;
  username: string;
  email?: string;
  avatar_url: string;
  access_token: string;
  refresh_token: string;
  token_expires_at: number;
  last_refresh: number;
  created_at: number;
  last_login: number;
}

export interface AuthError extends Error {
  code: 'STATE_MISMATCH' | 'TOKEN_EXCHANGE_FAILED' | 'REFRESH_FAILED' | 'NETWORK_ERROR';
  message: string;
}

export interface AuthService {
  login(): void;
  handleCallback(code: string, state: string): Promise<User>;
  getCurrentUser(): User | null;
  isAuthenticated(): boolean;
  refreshToken(): Promise<User>;
  logout(): void;
  promptRelogin(): void;
}
```

---

## Testing Contract

### Unit Tests

```typescript
describe('AuthService', () => {
  // Happy path
  test('login() redirects to GitHub OAuth endpoint', () => {})
  test('handleCallback() exchanges code for tokens', () => {})
  test('refreshToken() silently refreshes before expiry', () => {})
  test('logout() clears localStorage and redirects', () => {})

  // Error cases
  test('handleCallback() rejects on state mismatch', () => {})
  test('refreshToken() rejects when refresh_token expired', () => {})
  test('getCurrentUser() returns null when not logged in', () => {})

  // Edge cases
  test('isAuthenticated() returns false for expired token', () => {})
  test('refreshToken() called before token expiry avoids refresh', () => {})
  test('logout() can be called multiple times safely', () => {})
})
```

### Integration Tests

```typescript
describe('Auth Flow', () => {
  test('User can login via GitHub OAuth', () => {})
  test('Token refreshes silently before quiz', () => {})
  test('Session persists after page refresh', () => {})
  test('User can logout and login again', () => {})
  test('Quiz blocks non-authenticated users', () => {})
})
```

---

## Implementation Checklist

- [ ] Create `src/services/auth-service.ts` with all methods
- [ ] Create `src/hooks/useAuth.ts` (React hook wrapper)
- [ ] Create `src/types/auth.ts` (TypeScript interfaces)
- [ ] Add environment variables (.env template)
- [ ] Implement OAuth callback handler (/auth/github/callback route)
- [ ] Create login button component
- [ ] Create re-login modal component
- [ ] Add token refresh interceptor (before API calls)
- [ ] Write unit tests (80%+ coverage)
- [ ] Write integration tests (OAuth flow)
- [ ] Document error handling
- [ ] Add to Header component
- [ ] Add to Quiz component

---

**Contract Status**: Ready for Implementation | **Reference**: [data-model.md](../data-model.md#entity-1-user)
