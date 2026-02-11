# API Contracts Directory

**Purpose**: Define service interfaces and data contracts for the Physical AI textbook platform.

**Status**: Phase 1 Complete - All contracts ready for implementation

---

## Contracts Included

### 1. [auth-service.md](./auth-service.md)
- **Purpose**: GitHub OAuth 2.0 authentication, token lifecycle, session management
- **Key Methods**: `login()`, `handleCallback()`, `refreshToken()`, `logout()`
- **Clarification**: Q2 (OAuth token expiry handling)
- **Implementation Phase**: Phase 2 (Core Features)
- **Status**: Ready for development

### 2. [quiz-service.md](./quiz-service.md)
- **Purpose**: Quiz loading, question selection with pool rotation, scoring
- **Key Methods**: `loadQuiz()`, `selectQuestions()`, `scoreQuiz()`, `saveAttempt()`
- **Clarification**: Q1 (Quiz retake with different question pools)
- **Implementation Phase**: Phase 3 (Quiz System)
- **Status**: Ready for development

### 3. progress-service.md (TODO - Phase 1)
- **Purpose**: Reading progress tracking (scroll + time), quiz progress, persistence
- **Clarification**: Q3 (Reading progress calculation algorithm)
- **Implementation Phase**: Phase 2 (Core Features)
- **Status**: Contract template created; full spec in progress

### 4. i18n-service.md (TODO - Phase 1)
- **Purpose**: Multi-language support, locale switching, RTL layout
- **Implementation Phase**: Phase 4 (Multi-Language)
- **Status**: Contract template created; full spec in progress

### 5. search-service.md (TODO - Phase 1)
- **Purpose**: Full-text search, local indexing, result ranking
- **Implementation Phase**: Phase 4 (Search)
- **Status**: Contract template created; full spec in progress

### 6. cookie-service.md (TODO - Phase 1)
- **Purpose**: GDPR cookie consent, preferences management
- **Clarification**: Q4 (Anonymous user progress storage)
- **Implementation Phase**: Phase 5 (Compliance)
- **Status**: Contract template created; full spec in progress

### 7. content-service.md (TODO - Phase 1)
- **Purpose**: Load markdown files, parse front matter, extract reading time
- **Implementation Phase**: Phase 2 (Core Features)
- **Status**: Contract template created; full spec in progress

---

## Service Dependency Graph

```
Header Component
  └─ auth-service
       ├─ GitHub OAuth API
       └─ localStorage (auth data)

Quiz Component
  ├─ quiz-service
  │  ├─ JSON quiz files (/docs/)
  │  └─ localStorage (attempt data)
  └─ auth-service (requires login)

Progress Tracking
  ├─ progress-service
  │  ├─ content-service (read time calculation)
  │  └─ localStorage (progress data)
  └─ auth-service (user ID)

Multi-Language
  ├─ i18n-service
  │  └─ Docusaurus i18n config
  └─ localStorage (language preference)

Search
  ├─ search-service
  │  ├─ content-service (indexing)
  │  └─ localStorage (search index cache)

Cookie Management
  ├─ cookie-service
  │  └─ localStorage (consent data)
```

---

## Implementation Roadmap

### Phase 2: Core Features (Week 3-4)
- [ ] Implement auth-service (login, token refresh, logout)
- [ ] Implement content-service (markdown loading, front matter parsing)
- [ ] Implement progress-service (reading time calculation)
- [ ] Create Header component with auth button

### Phase 3: Quiz System (Week 5-6)
- [ ] Implement quiz-service (question loading, pool rotation, scoring)
- [ ] Create Quiz component (question rendering, answer selection)
- [ ] Create QuizResults component (score display, explanations)
- [ ] Create all quiz content (60 questions across 4 modules)

### Phase 4: Multi-Language & Search (Week 7-8)
- [ ] Implement i18n-service (locale switching, RTL layout)
- [ ] Implement search-service (full-text search, result ranking)
- [ ] Create LanguageSelector component
- [ ] Create SearchModal component
- [ ] Translate all UI strings (4 languages)

### Phase 5: Compliance (Week 9-10)
- [ ] Implement cookie-service (consent banner, preferences)
- [ ] Create CookieConsent component
- [ ] Run accessibility audit (WCAG AA)
- [ ] Optimize performance (Lighthouse >= 90)

### Phase 6: Deployment (Week 11)
- [ ] Set up GitHub Actions CI/CD
- [ ] Configure GitHub Pages
- [ ] Create monitoring + alerting
- [ ] Deploy to production

---

## Testing Strategy

### Unit Tests (80%+ coverage)
- Test all service methods with mocked dependencies
- Validate error handling for each error case
- Test edge cases (empty arrays, null values, etc.)

### Integration Tests
- Test service interactions (auth → progress → quiz)
- Test localStorage persistence and retrieval
- Test OAuth flow (mock GitHub API)

### E2E Tests
- Full user journeys (User Stories 1-5)
- Cross-browser compatibility
- Mobile responsiveness (320px+)
- Accessibility (keyboard navigation, screen readers)

---

## Contract Development Process

For each service:

1. **Read contract** (e.g., `auth-service.md`)
2. **Implement methods** (`src/services/auth-service.ts`)
3. **Create React hook** (`src/hooks/useAuth.ts`)
4. **Write unit tests** (`tests/unit/auth-service.test.ts`)
5. **Write integration tests** (`tests/integration/auth-flow.test.ts`)
6. **Integrate with components** (Header, Quiz, etc.)
7. **Test end-to-end** (Playwright tests)
8. **Document usage** (in component comments)

---

## Clarifications Referenced

| Clarification | Service | Impact |
|--------------|---------|--------|
| Q1: Question Pool Rotation | quiz-service | Different questions on each retake |
| Q2: OAuth Token Refresh | auth-service | Silent refresh with graceful fallback |
| Q3: Reading Progress | progress-service | Scroll + 30s time threshold algorithm |
| Q4: Anonymous Storage | cookie-service, progress-service | sessionStorage per session, localStorage after login |

---

## Key Design Decisions

1. **localStorage-only for MVP**: Simplifies architecture, enables offline support
2. **GitHub OAuth only**: Zero backend infrastructure, targets CS/robotics students
3. **Deterministic question rotation**: Same attempt number gets same question pool
4. **Client-side scoring**: 100% accuracy with local validation
5. **Service-oriented architecture**: Easy to migrate to backend in Phase 2

---

## Success Criteria

- [ ] All contracts documented and approved
- [ ] All services implemented (80%+ test coverage)
- [ ] All components developed and integrated
- [ ] All user stories pass E2E tests
- [ ] Performance: Lighthouse >= 90 (all categories)
- [ ] Accessibility: WCAG AA compliance
- [ ] Deployment: GitHub Pages + CI/CD

---

**Directory Status**: Phase 1 Planning Complete | **Next Step**: Begin Phase 2 Implementation
