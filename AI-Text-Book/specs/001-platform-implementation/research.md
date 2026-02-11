# Phase 0 Research: Technology Decisions & Risk Analysis

**Created**: 2026-01-17 | **Feature**: 001-platform-implementation

---

## Executive Summary

This document captures technology decisions, risk analysis, and foundational research for the Physical AI & Humanoid Robotics Interactive Textbook platform. All clarifications from the specification have been resolved (0 NEEDS CLARIFICATION markers remain). The platform is architecturally sound for MVP implementation using static site generation + client-side interactivity.

---

## Technology Decisions

### Framework Choice: Docusaurus 3.x + React 18.x

**Decision**: Use Docusaurus 3.x (static site generator) + React 18.x (interactive components) for frontend-only MVP.

**Options Considered**:
1. **Docusaurus 3.x + React 18.x** (SELECTED)
2. Next.js 14 + Node.js backend
3. Gatsby 5 + GraphQL backend
4. SvelteKit + serverless functions
5. Static Jekyll + vanilla JavaScript

**Rationale**:
- ✅ Docusaurus optimized for technical documentation (perfect fit for textbook)
- ✅ Built-in i18n support (5 locales without extra library complexity)
- ✅ Static generation → GitHub Pages deployment (zero ops, no backend server)
- ✅ React for interactive components (quizzes, progress, auth) while keeping static content fast
- ✅ Mature ecosystem (90k+ GitHub stars, widespread adoption)
- ✅ Bundle size minimal (Docusaurus core: 80KB gzip)
- ❌ **Trade-off**: No persistent backend in MVP (localStorage only; Phase 2 upgrade path clear)
- ❌ **Trade-off**: Real-time collaboration not supported (acceptable for learning platform)

**Trade-offs Accepted**:
- localStorage limit (~5-10MB per domain) acceptable for 4 modules + quiz state + progress + cookies
- No real-time sync (students work independently; Phase 2 backend enables forums/collaboration)
- No user administration UI (admin features Phase 2; content lives in git for MVP)

**Reversibility**: High — Phase 2 can migrate to Next.js backend while keeping Docusaurus frontend

---

### Authentication: GitHub OAuth 2.0

**Decision**: Use GitHub OAuth 2.0 for user authentication (login button, session management, token refresh).

**Options Considered**:
1. **GitHub OAuth 2.0** (SELECTED)
2. Email/password with bcrypt
3. Auth0/Cognito service
4. No authentication (anonymous only)
5. JWT-based custom auth

**Rationale**:
- ✅ Zero backend infrastructure required (GitHub handles OAuth server)
- ✅ Target audience (CS/robotics students) likely has GitHub accounts
- ✅ No password storage or email verification burden
- ✅ Session stored in localStorage (fits MVP architecture)
- ✅ Refresh token lifecycle well-documented (Clarification Q2 resolved)
- ✅ Eliminates GDPR email collection concerns (GitHub owns user data)
- ❌ **Trade-off**: Users must have GitHub account (acceptable for technical audience)
- ❌ **Trade-off**: Cannot customize user profiles without backend (Phase 2)

**Implementation Details** (from Clarification Q2):
- Store `access_token` + `refresh_token` + `expires_at` in localStorage
- Before API call, check token expiry; if expired, silently attempt refresh
- If refresh fails, prompt user to re-login (handled gracefully)
- OAuth redirect URI: `https://<domain>/auth/github/callback`
- Client ID stored in `.env` (public); secrets in GitHub Actions secrets

**Risk**: GitHub OAuth service outage → users cannot login. Mitigation: Display status banner; provide manual fallback authentication (one-time code via email) in Phase 2.

---

### State Management: localStorage + React Context

**Decision**: Use localStorage for all persistence (auth, quiz state, progress, preferences) + React Context API for app state.

**Options Considered**:
1. **localStorage + React Context** (SELECTED)
2. Redux + Redux Persist
3. MobX + localStorage sync
4. Zustand + custom persistence
5. Server-side sessions (requires backend)

**Rationale**:
- ✅ Zero external dependencies (Context built into React)
- ✅ No network requests for state restoration (localStorage is synchronous, offline-capable)
- ✅ GDPR-compliant (user controls all data; clear on browser close per Clarification Q4)
- ✅ Sufficient for MVP feature set (auth, quiz state, 4 modules × 10 questions)
- ✅ Easy migration path to Redux/Zustand in Phase 2
- ❌ **Trade-off**: localStorage limit ~5-10MB (adequate for textbook + quizzes + metadata)
- ❌ **Trade-off**: Not real-time sync across tabs (acceptable; users typically use 1 tab)
- ❌ **Trade-off**: No server-side backup (Phase 2 upgrade)

**Schema** (documented in data-model.md):
```json
{
  "auth": {
    "userId": "github_123456",
    "username": "studentname",
    "avatar": "https://avatars.githubusercontent.com/u/123456",
    "accessToken": "gho_xxx",
    "refreshToken": "ghr_xxx",
    "expiresAt": 1642425600000,
    "lastRefresh": 1642422000000
  },
  "progress": {
    "module-1-ros2": {
      "readingTime": 1250,
      "readingProgress": 0.75,
      "quizScore": 80,
      "quizAttempts": 2
    }
  },
  "quizzes": {
    "module-1-ros2": {
      "lastAnswers": { "q1": "a", "q2": "c" },
      "lastScore": 80,
      "attempts": [...]
    }
  },
  "cookies": {
    "essential": true,
    "analytics": false,
    "preferences": false,
    "lastUpdated": 1642422000000
  },
  "language": "en",
  "theme": "dark"
}
```

---

### Multi-Language Architecture: Docusaurus i18n

**Decision**: Use Docusaurus built-in i18n with 5 locales (en, ur, ar, zh, es); RTL auto-detection.

**Options Considered**:
1. **Docusaurus i18n** (SELECTED)
2. i18n-js library + manual locale routing
3. Crowdin/Lokalise (external translation platform)
4. English-only MVP
5. react-i18next + backend language files

**Rationale**:
- ✅ Docusaurus i18n built-in (no extra npm packages)
- ✅ Automatic URL structure (`/ur/docs/...`, `/ar/docs/...`)
- ✅ RTL layout auto-detection per locale
- ✅ Content stored in separate subdirectories (`/docs`, `/docs_ur`, `/docs_ar`, etc.)
- ✅ Easy to manage translations (markdown files versioned in git)
- ✅ SEO-friendly (hreflang links auto-generated)
- ❌ **Trade-off**: Requires duplicate content (per locale); Phase 2 adds translation workflow
- ❌ **Trade-off**: All 4 languages must be ready for MVP launch (coordinate with content team)

**Locales**:
- **English** (en) - Primary; technical terms in English; code examples English-only
- **Urdu** (ur) - RTL; UI strings translated; technical terms + code remain English
- **Arabic** (ar) - RTL; UI strings translated; technical terms + code remain English
- **Chinese (Simplified)** (zh) - LTR; UI strings translated; technical terms + code remain English
- **Spanish** (es) - LTR; UI strings translated; technical terms + code remain English

**RTL Handling** (from Clarification Q3):
- Docusaurus auto-detects RTL based on locale
- CSS Grid/Flex automatically reverse for RTL
- Lucide icons stay LTR (no mirror for code/technical icons)
- Hero animation (neural grid) stays consistent across all locales

---

### Data Model: 9 Core Entities

**Entity Definitions** (detailed in data-model.md):

1. **User**
   - github_id, username, email, avatar_url, created_at, last_login
   - Storage: localStorage (auth.userId, auth.username, auth.avatar)

2. **Module**
   - id, title, description, topics[], quiz_id, created_at
   - Storage: JSON in /quizzes/module-*.json

3. **Content Page**
   - id, module_id, title, content (markdown), reading_time, metadata
   - Storage: Markdown files in /docs/module-*/

4. **Quiz**
   - id, module_id, questions[], passing_score (70%), time_limit (10 min)
   - Storage: JSON in /quizzes/module-*.json

5. **Quiz Question**
   - id, quiz_id, question_text, options[], correct_answer, explanation
   - Storage: Nested in /quizzes/module-*.json

6. **Quiz Attempt**
   - id, user_id, quiz_id, answers{}, score, attempt_number, timestamp, duration
   - Storage: localStorage in progress[module_id].quizAttempts[]

7. **User Progress**
   - id, user_id, module_id, reading_time, reading_progress (%), quiz_score, quiz_attempts, last_updated
   - Storage: localStorage in progress[module_id]

8. **Cookie Preferences**
   - user_id, essential (bool), analytics (bool), preferences (bool), created_at, updated_at
   - Storage: localStorage in cookies{}

9. **Language Preference**
   - user_id, preferred_locale, auto_detected (bool), created_at
   - Storage: localStorage in language field

---

### Quiz Question Pool Strategy

**Decision**: Implement question pool rotation to prevent memorization; different pool on each retake (Clarification Q1 resolved).

**Options Considered**:
1. **Different pool per retake** (SELECTED)
2. Same questions every time
3. Random question order only

**Rationale**:
- ✅ Prevents memorization (pedagogical best practice)
- ✅ Encourages deeper learning (students re-read material for understanding)
- ✅ Supports quiz retakes as learning tool
- ✅ Maintains difficulty equivalence across pools
- ❌ **Trade-off**: Requires larger question bank (10-15 questions per module; show only 10)

**Implementation**:
- Store 15 questions per module in /quizzes/module-*.json
- On quiz load, randomly select 10 unique questions (no duplication within attempt)
- Track selected question IDs in localStorage (prevents re-selection on page refresh)
- Per Clarification Q1: Different pool on each retake; can be same pool if randomly selected

**Quality Assurance**:
- All 15 questions validated for correct answer accuracy (100% required)
- All 15 questions within difficulty band (avoid easy/hard outliers)
- Explanations provided for all options (not just correct answer)
- Regular review of question effectiveness (Phase 2 backend analytics)

---

### Reading Progress Calculation: Scroll + Time Algorithm

**Decision**: Combine scroll detection + 30-second time threshold per section to track reading progress (Clarification Q3 resolved).

**Options Considered**:
1. **Scroll + 30-second time threshold** (SELECTED)
2. Scroll detection only
3. Time-based only (no scrolling requirement)
4. Explicit "Mark as Read" button
5. Keystroke/engagement detection

**Rationale**:
- ✅ Prevents gaming (students cannot just scroll past content quickly)
- ✅ Recognizes different reading speeds (fast readers + slow readers both supported)
- ✅ Non-intrusive (no explicit button clicks required)
- ✅ No privacy concerns (local calculation, no server tracking)
- ✅ Works offline
- ❌ **Trade-off**: Imperfect (users can scroll + wait without actually reading; acceptable for MVP)

**Algorithm**:
```
For each content section (h2 or div.section):
1. Detect when section scrolls into viewport (IntersectionObserver)
2. Start timer when section enters viewport
3. If section remains visible for ≥ 30 seconds:
   - Mark as "read"
   - Add section word count to total reading time
4. Calculate progress as (word count read / total word count)
5. Update progress bar: `max(scroll position, reading time progress)`

Example:
- Total content: 6000 words
- User scrolls through 3000 words → reads only 1500 words (due to timer)
- Reading time: ~8 minutes (1500 / 6000 = 25%)
- Progress bar: 25% (whichever is higher: scroll position or reading time)
```

**Edge Cases Handled**:
- User scrolls too fast → section not counted (timer prevents)
- User leaves page mid-section → no credit (timer resets)
- User resizes window → recalculate visible sections
- User returns to page → restore progress (retrieve from localStorage)

---

### Anonymous User Progress Storage

**Decision**: Use localStorage for session persistence; clear on browser close (Clarification Q4 resolved).

**Options Considered**:
1. **Session localStorage, clear on close** (SELECTED)
2. Persistent localStorage (stay after browser close)
3. No storage for anonymous users (restart on each visit)
4. Server-side session (requires backend)

**Rationale**:
- ✅ Balances UX (no mid-session loss) with privacy (no persistent tracking)
- ✅ Aligns with GDPR principles (user's browser controls data, not server)
- ✅ Fits MVP architecture (no backend required)
- ✅ Improves learning experience (users can resume quiz within session)
- ✅ Transparent to user (no surprise data collection)
- ❌ **Trade-off**: Progress lost if browser crashes (acceptable; user expected to save progress by login)

**Implementation**:
- Use `sessionStorage` API (not `localStorage`) for anonymous users
- After user logs in, migrate sessionStorage → localStorage
- On browser close (all tabs), sessionStorage auto-clears (browser responsibility)
- Add clear warning: "Your progress will be cleared when you close your browser. Create a free account to save permanently."

**Cookie Consent Impact** (per Clarification Q4):
- localStorage (authenticated users) = "Preferences" category (user explicitly consented)
- sessionStorage (anonymous users) = No consent needed (session-only, no persistent tracking)
- Analytics/third-party tracking = Only if user enabled in cookie preferences (default disabled)

---

## Risk Analysis & Mitigation

### Critical Risks

| **Risk** | **Probability** | **Impact** | **Mitigation** |
|----------|-----------------|-----------|----------------|
| **GitHub OAuth token expires during quiz** | Medium (token ~1 hour lifetime) | User loses quiz progress | Q2 clarification: Silent refresh before expiry; graceful re-login prompt |
| **localStorage quota exceeded** | Low (5-10MB available; ~1MB quiz state) | Quiz/progress data loss | Implement cleanup service; limit quiz history to last 5 attempts |
| **RTL layout breaks on complex components** | Medium (4 RTL locales) | Poor UX for 40% of users | Early user testing; comprehensive RTL CSS testing matrix |
| **Performance degrades on slow 3G networks** | Medium (LCP target 2.5s) | Users abandon (high bounce rate) | Code splitting; preload critical assets; skeleton screens |
| **Translation content out of sync** | High (manual translation workflow) | Localized versions stale | Document single-source-of-truth (English); automated checks |

### Environmental Risks

| **Risk** | **Mitigation** |
|----------|----------------|
| **GitHub Pages CDN outage** | Fallback: Deploy to Vercel/Netlify; maintain DNS provider control |
| **GitHub OAuth API rate limits** | Low risk for MVP scale (10k users = 0.1% of rate limit) |
| **Browser storage disabled by user** | Degrade gracefully; warn user "progress will not save"; still usable |
| **JavaScript disabled** | Docusaurus renders static HTML; quiz requires JS (document trade-off) |

### Mitigation Strategies

**High Priority**:
- ✅ Implement silent token refresh (Q2 clarification)
- ✅ Add localStorage quota monitoring + cleanup
- ✅ Comprehensive cross-browser RTL testing (early phase)
- ✅ Performance monitoring (Lighthouse CI in GitHub Actions)

**Medium Priority**:
- ⚠️ Create rollback procedure (GitHub Actions can revert to previous build)
- ⚠️ Set up error tracking (Sentry for JavaScript errors)
- ⚠️ Document fallback deployment (Vercel if GitHub Pages fails)

**Lower Priority (Phase 2)**:
- ⚠️ Implement backend for persistent storage
- ⚠️ Add real-time sync across devices
- ⚠️ Formal translation management system

---

## Implementation Clarifications Resolved

### ✅ Clarification Q1: Quiz Question Pool on Retake
**Question**: Should students see the same 10 questions on retake or different questions from a pool?
**Resolution**: Different questions on each retake (from a pool of 15).
**Implication**: FR-024 updated; question bank preparation now requires 15 questions per module.

### ✅ Clarification Q2: OAuth Token Expiry Handling
**Question**: How to handle OAuth token expiry during quiz?
**Resolution**: Silently attempt refresh using GitHub OAuth refresh token; prompt login only if refresh fails.
**Implication**: FR-015, FR-016 updated; token lifecycle documented in auth service.

### ✅ Clarification Q3: Reading Progress Calculation
**Question**: How to track reading without intrusive "Mark as Read" buttons?
**Resolution**: Scroll-based + 30-second time threshold per section.
**Implication**: FR-043 updated; progress algorithm documented above; prevents gaming.

### ✅ Clarification Q4: Anonymous User Progress Storage
**Question**: How to store progress for non-authenticated users?
**Resolution**: sessionStorage (clears on browser close); localStorage after login.
**Implication**: FR-045 updated; privacy-first approach aligns with GDPR.

---

## Technology Stack Summary

| Layer | Technology | Rationale |
|-------|-----------|-----------|
| **Generator** | Docusaurus 3.x | SSG for content; built-in i18n; optimized for documentation |
| **Frontend Framework** | React 18.x | Interactive components; hooks for state; TypeScript support |
| **Language** | TypeScript 5.x | Type safety; IDE support; catch errors early |
| **Styling** | Tailwind CSS | Utility-first; responsive; small bundle; dark mode built-in |
| **Icons** | Lucide Icons | Comprehensive; consistent; LTR/RTL friendly |
| **i18n** | Docusaurus i18n | Built-in; automatic RTL; URL structure clean |
| **Authentication** | GitHub OAuth 2.0 | Zero backend; JWT tokens; refresh token support |
| **State** | React Context + localStorage | Minimal dependencies; GDPR-compliant; offline-capable |
| **Testing** | Jest + React Testing Library | Industry standard; great DX; 80%+ coverage target |
| **E2E Testing** | Playwright | Fast; reliable; cross-browser; CI/CD friendly |
| **Hosting** | GitHub Pages | Free; integrated; CDN; automatic HTTPS |
| **CI/CD** | GitHub Actions | Built-in; free for public repos; no separate VM needed |

---

## Next Steps

1. **Phase 0 Setup** (1 week):
   - [ ] Initialize Docusaurus project scaffold
   - [ ] Register GitHub OAuth app (get client ID/secret)
   - [ ] Set up development environment (.env, dependencies)
   - [ ] Create git branches for parallel work

2. **Phase 1 Design** (2 weeks):
   - [ ] Finalize data-model.md (entity schemas, validation)
   - [ ] Create API contracts in /contracts/ directory
   - [ ] Build component library stubs
   - [ ] Document testing strategy

3. **Phase 2+ Implementation**:
   - [ ] Follow sprint schedule in plan.md
   - [ ] Weekly progress checkpoints
   - [ ] Risk monitoring (especially OAuth, localStorage, RTL)

---

## Appendix: Threat Model

**Scope**: Frontend-only MVP; no backend authentication or data storage.

### Attack Surface

| Threat | Likelihood | Impact | Mitigation |
|--------|-----------|--------|-----------|
| **XSS via quiz content injection** | Low (content from git, not user input) | Medium (quiz state compromise) | Sanitize markdown parsing; no user-generated content |
| **CSRF on GitHub OAuth callback** | Low (OAuth state parameter prevents) | High (session hijacking) | Validate OAuth state token; use secure random; HTTPS only |
| **localStorage token theft (XSS)** | Low (no user-generated content) | Medium (quiz cheating) | Standard XSS prevention; token lifetime limited to 1 hour |
| **Clickjacking to trick quiz submit** | Low (form submits locally) | Low (user cheats only self) | X-Frame-Options header; not applicable for static site |
| **Privacy leakage via cookies** | Low (user controls consent) | Medium (tracking without consent) | GDPR banner; granular opt-in; no third-party cookies |
| **Denial of Service (GitHub Pages)** | Low (GitHub manages infrastructure) | High (site unavailable) | Fallback DNS to Vercel; GitHub Pages SLA 99.9% |

### Data Protection

- ✅ All data in localStorage (browser-controlled; user can clear)
- ✅ Token stored in localStorage (not HttpOnly cookie; acceptable for public app)
- ✅ No server-side database (Phase 2 implements security controls)
- ✅ HTTPS enforced (GitHub Pages auto-HTTPS)
- ✅ No email/password (GitHub owns auth; eliminates credential database risk)

### Compliance

- ✅ GDPR: Users control all data; cookie consent; no email collection
- ✅ CCPA: No sale of personal data; privacy policy needed (Phase 2)
- ✅ FERPA: Education data (if applicable); document student privacy (Phase 2)

---

**Document Status**: Approved | **Next Review**: After Phase 1 completion
