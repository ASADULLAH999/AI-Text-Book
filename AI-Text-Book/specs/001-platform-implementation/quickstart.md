# Phase 1 Quickstart: Local Development & Deployment

**Created**: 2026-01-17 | **Feature**: 001-platform-implementation

---

## Quick Links

- **Specification**: [spec.md](./spec.md)
- **Implementation Plan**: [plan.md](./plan.md)
- **Research & Tech Decisions**: [research.md](./research.md)
- **Data Model**: [data-model.md](./data-model.md)
- **API Contracts**: [contracts/](./contracts/) (generated in Phase 1)

---

## Local Development Setup

### Prerequisites

- **Node.js**: 18+ (verify with `node --version`)
- **npm**: 9+ (verify with `npm --version`)
- **Git**: For version control
- **GitHub Account**: For OAuth testing
- **Text Editor**: VS Code recommended

### Step 1: Clone & Install

```bash
# Clone repository
git clone https://github.com/[org]/physical-ai-textbook.git
cd physical-ai-textbook

# Create feature branch
git checkout -b 001-platform-implementation

# Install dependencies
npm install

# Install dev dependencies
npm install --save-dev jest @testing-library/react playwright
```

### Step 2: Environment Setup

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your values:
# GITHUB_OAUTH_CLIENT_ID=<your-client-id>
# GITHUB_OAUTH_CLIENT_SECRET=<your-client-secret>
# NODE_ENV=development
```

#### Getting GitHub OAuth Credentials

1. **Create OAuth App** in GitHub:
   - Go to Settings → Developer settings → OAuth Apps
   - Click "New OAuth App"
   - Fill in:
     - Application name: "Physical AI Textbook (Dev)"
     - Homepage URL: `http://localhost:3000`
     - Authorization callback URL: `http://localhost:3000/auth/github/callback`
   - Note the **Client ID** and **Client Secret**

2. **Add to .env**:
   ```bash
   GITHUB_OAUTH_CLIENT_ID=<Client ID>
   GITHUB_OAUTH_CLIENT_SECRET=<Client Secret>
   ```

### Step 3: Start Development Server

```bash
# Start Docusaurus dev server with hot reload
npm start

# Expected output:
# ℹ️ Starting the development server...
# ℹ️ Docusaurus website is running at: http://localhost:3000

# Open http://localhost:3000 in your browser
```

### Step 4: Verify Installation

- [ ] Homepage loads (6 sections visible)
- [ ] Hero section displays animated grid
- [ ] Module cards render in responsive grid
- [ ] Navigation links work (start reading, login button visible)
- [ ] No errors in browser console

---

## Development Workflow

### Hot Reload & File Watching

Docusaurus automatically reloads when you modify:

```
docs/
├── index.md              # Homepage changes → auto reload
├── module-1-ros2/
│   ├── index.md          # Module changes → auto reload
│   ├── topic-1-intro.md  # Content changes → auto reload
│   └── quiz.json         # Quiz changes → auto reload

src/
├── components/
│   ├── Quiz.tsx          # Component changes → auto reload
│   └── Header.tsx        # → auto reload
└── services/
    └── quiz-service.ts   # Service changes → manual restart needed*

*Services require `npm start` restart due to Node.js module cache
```

### Code Organization

```
src/
├── components/              # React components
│   ├── ModuleCard.tsx      # Reusable components
│   ├── Quiz.tsx            # Feature components
│   └── index.ts            # Re-exports
├── services/                # Business logic
│   ├── auth-service.ts     # Auth + token refresh
│   ├── quiz-service.ts     # Quiz loading + scoring
│   ├── progress-service.ts # Reading + quiz tracking
│   ├── i18n-service.ts     # Language switching
│   ├── search-service.ts   # Full-text search
│   └── cookie-service.ts   # Cookie consent
├── hooks/                   # React hooks
│   ├── useAuth.ts          # Auth state
│   ├── useProgress.ts      # Progress state
│   ├── useLanguage.ts      # Language state
│   └── useLocalStorage.ts  # Persistence
├── utils/                   # Utilities
│   ├── constants.ts        # Colors, timings
│   ├── validators.ts       # Validation functions
│   └── time-formatter.ts   # Time display
├── styles/                  # CSS
│   ├── globals.css         # Global + variables
│   ├── animations.css      # Keyframes
│   └── responsive.css      # Breakpoints
└── types/                   # TypeScript interfaces
    └── entities.ts         # Data model types
```

### Git Workflow

```bash
# Create feature branch
git checkout -b 001-platform-implementation

# Make changes
vim src/components/Quiz.tsx
vim docs/module-1-ros2/index.md

# Stage changes
git add .

# Commit with meaningful message
git commit -m "feat: implement Quiz component with score calculation"

# Push to remote
git push origin 001-platform-implementation

# Create pull request on GitHub
# Add description of changes
# Request review
# After approval, merge to main
```

---

## Running Tests

### Unit Tests

```bash
# Run all unit tests
npm test

# Run with coverage
npm test -- --coverage

# Run specific test file
npm test -- src/services/quiz-service.test.ts

# Watch mode (re-run on file changes)
npm test -- --watch
```

### Integration Tests

```bash
# Run integration tests
npm run test:integration

# Integration tests go in tests/integration/
# Example: tests/integration/quiz-flow.test.ts
```

### E2E Tests (Playwright)

```bash
# Run Playwright E2E tests
npm run test:e2e

# Run in headed mode (see browser)
npm run test:e2e -- --headed

# Run specific test
npm run test:e2e -- tests/e2e/homepage.spec.ts

# Debug mode
npm run test:e2e -- --debug
```

### Test Coverage Target

- ✅ Unit tests: 80%+ coverage
- ✅ Integration tests: Critical user flows (auth, quiz, progress)
- ✅ E2E tests: Full user journeys (User Stories 1-5)

---

## Building for Production

### Build Command

```bash
# Build static site (generates output/ directory)
npm run build

# Expected output:
# ✓ Generated clientModules.js, docusaurusAPIMetadata.json
# ✓ Copied static assets
# ✓ Built in 45 seconds
```

### Build Verification

```bash
# Verify build output
ls -la build/

# Preview production build locally
npm run serve

# Visit http://localhost:3000
# Verify all features work (quiz, auth, search, etc.)
```

### Build Size Analysis

```bash
# Analyze bundle size
npm run build -- --stats

# Check specific bundle sizes
# Target: Total bundle < 200KB (gzip)
# - Docusaurus core: ~80KB
# - React: ~45KB
# - Components: ~30KB
# - Styles: ~25KB
```

---

## Deployment to GitHub Pages

### Step 1: Configure GitHub Pages

1. Go to repository Settings → Pages
2. Source: Deploy from branch
3. Branch: `main` | Folder: `/ (root)`
4. Click "Save"
5. Visit `https://[org].github.io/physical-ai-textbook` (takes 1-2 minutes)

### Step 2: Configure docusaurus.config.js

```javascript
module.exports = {
  baseUrl: '/physical-ai-textbook/',  // Required for GitHub Pages
  url: 'https://[org].github.io',
  organizationName: '[org]',
  projectName: 'physical-ai-textbook',
  deploymentBranch: 'gh-pages',
  // ... rest of config
};
```

### Step 3: Deploy

```bash
# Manual deployment (not recommended - use GitHub Actions instead)
npm run deploy

# GitHub Actions (recommended) - automatic on push to main
# See .github/workflows/deploy.yml
```

### Step 4: Verify Deployment

```bash
# Check GitHub Pages deployment
# Go to Settings → Pages → "Your site is live at https://..."

# Test SSL certificate
curl -I https://[org].github.io/physical-ai-textbook

# Verify quiz, auth, search work on production
```

---

## GitHub Actions CI/CD

### Pipeline Configuration

File: `.github/workflows/build-deploy.yml`

```yaml
name: Build and Deploy

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Use Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'

      - name: Install dependencies
        run: npm ci

      - name: Lint
        run: npm run lint

      - name: Run tests
        run: npm test -- --coverage

      - name: Build
        run: npm run build

      - name: Upload coverage
        uses: codecov/codecov-action@v3

  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'
    steps:
      - uses: actions/checkout@v3

      - name: Use Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'

      - name: Install and build
        run: npm ci && npm run build

      - name: Deploy to GitHub Pages
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./build
```

### Deployment Checklist

Before merging to main:
- [ ] All unit tests pass (`npm test`)
- [ ] All E2E tests pass (`npm run test:e2e`)
- [ ] No linting errors (`npm run lint`)
- [ ] Build succeeds locally (`npm run build`)
- [ ] Lighthouse score >= 90 (`npm run lighthouse`)
- [ ] Code review approved
- [ ] No console errors in browser dev tools

---

## Troubleshooting

### Issue: "Cannot find module 'react'"

```bash
# Solution: Reinstall node_modules
rm -rf node_modules package-lock.json
npm install
```

### Issue: Hot reload not working

```bash
# Solution: Clear cache and restart
npm start -- --reset-cache

# Or manually:
rm -rf node_modules/.cache
npm start
```

### Issue: GitHub OAuth callback fails

```bash
# Checklist:
# 1. Verify GITHUB_OAUTH_CLIENT_ID in .env
# 2. Verify GITHUB_OAUTH_CLIENT_SECRET in .env
# 3. Check GitHub OAuth app callback URL matches http://localhost:3000/auth/github/callback
# 4. Ensure .env is loaded (check browser Network tab for auth request)
# 5. Check browser console for error messages
```

### Issue: localStorage data lost

```bash
# Debug: Check localStorage in DevTools
# Open DevTools → Application → Local Storage → http://localhost:3000

# Clear specific key:
localStorage.removeItem('auth')
localStorage.removeItem('progress')

# Clear all:
localStorage.clear()

# Then refresh page and test again
```

### Issue: Quiz questions not loading

```bash
# Verify quiz.json exists:
ls -la docs/module-1-ros2/quiz.json

# Verify JSON format:
cat docs/module-1-ros2/quiz.json | npm run json-lint

# Check quiz service logs:
# Open DevTools → Console → search for "quiz-service"
```

### Issue: Build fails with TypeScript errors

```bash
# Check all TypeScript errors
npm run type-check

# Fix errors:
npm run type-check -- --fix

# Or manually fix and rebuild
npm run build
```

---

## Performance Optimization

### Lighthouse Audit

```bash
# Run Lighthouse locally
npm run lighthouse

# Target scores:
# - Performance: >= 90
# - Accessibility: >= 95
# - Best Practices: >= 95
# - SEO: >= 95

# Review report
open lighthouse-report.html
```

### Code Splitting

```javascript
// In React components, use lazy loading for quiz:
const Quiz = React.lazy(() => import('./components/Quiz'));

// Wrap with Suspense:
<Suspense fallback={<QuizSkeleton />}>
  <Quiz />
</Suspense>
```

### Image Optimization

```bash
# Convert images to WebP
npm run optimize-images

# Verify bundle size
npm run build -- --stats
```

---

## Environment Variables

### Development (.env)

```bash
# GitHub OAuth
GITHUB_OAUTH_CLIENT_ID=your_client_id
GITHUB_OAUTH_CLIENT_SECRET=your_client_secret

# Docusaurus
NODE_ENV=development
DOCUSAURUS_HOST=localhost
DOCUSAURUS_PORT=3000

# Features
ENABLE_SEARCH=true
ENABLE_ANALYTICS=false
```

### Production (.env.production)

```bash
# GitHub OAuth
GITHUB_OAUTH_CLIENT_ID=prod_client_id
GITHUB_OAUTH_CLIENT_SECRET=prod_client_secret

# Docusaurus
NODE_ENV=production
DOCUSAURUS_HOST=physical-ai-textbook.com
DOCUSAURUS_PORT=443

# Features
ENABLE_SEARCH=true
ENABLE_ANALYTICS=true
```

---

## Version Control Best Practices

### Branch Naming

```bash
git checkout -b 001-platform-implementation          # Feature branch
git checkout -b fix/quiz-scoring-bug                # Bug fix
git checkout -b docs/update-readme                   # Documentation
git checkout -b refactor/auth-service               # Refactoring
```

### Commit Messages

```bash
# Good commit messages:
git commit -m "feat: implement Quiz component with multiple-choice and scoring"
git commit -m "fix: resolve OAuth token refresh timing issue"
git commit -m "docs: add quickstart guide for local development"
git commit -m "refactor: extract quiz-service into separate module"

# Avoid:
git commit -m "fix stuff"                            # Too vague
git commit -m "update code"                          # No context
git commit -m "asdf"                                 # No meaning
```

### Pull Request Template

```markdown
## Description
Brief description of changes (1-2 sentences)

## Type of Change
- [ ] New feature
- [ ] Bug fix
- [ ] Documentation update
- [ ] Refactoring

## Testing
How was this tested?
- [ ] Unit tests (80%+ coverage)
- [ ] Integration tests
- [ ] E2E tests
- [ ] Manual testing (describe)

## Screenshots (if applicable)
Add screenshot of UI changes

## Checklist
- [ ] Code follows style guide
- [ ] Self-review completed
- [ ] Comments added for complex logic
- [ ] Documentation updated
- [ ] Tests pass locally
- [ ] No new warnings
```

---

## Useful npm Scripts

```bash
# Development
npm start              # Start dev server (http://localhost:3000)
npm test               # Run unit tests
npm run type-check     # Type checking
npm run lint           # Linting

# Building
npm run build          # Production build
npm run serve          # Serve build locally

# Testing
npm run test:unit      # Unit tests only
npm run test:integration  # Integration tests
npm run test:e2e       # End-to-end tests with Playwright
npm run test:coverage  # Coverage report

# Analysis
npm run lighthouse     # Lighthouse audit
npm run analyze        # Bundle analysis
npm run type-check     # Type errors

# Deployment
npm run deploy         # Deploy to GitHub Pages (manual)
npm run clean          # Clean build artifacts
```

---

## Next Steps

1. **Phase 2**: Start implementation using sprint schedule in [plan.md](./plan.md)
2. **Create Components**: Follow component contracts in [contracts/](./contracts/)
3. **Implement Services**: Follow service interfaces in data-model.md
4. **Write Tests**: 80%+ coverage target for all services and components
5. **Deploy**: Merge to main after all tests pass → GitHub Actions auto-deploys

---

## Support & Resources

- **Docusaurus Docs**: https://docusaurus.io
- **React Docs**: https://react.dev
- **TypeScript Docs**: https://www.typescriptlang.org
- **GitHub Actions Docs**: https://docs.github.com/en/actions
- **Playwright Testing**: https://playwright.dev
- **Jest Testing**: https://jestjs.io

---

**Document Status**: Ready for Phase 2 Implementation | **Last Updated**: 2026-01-17
