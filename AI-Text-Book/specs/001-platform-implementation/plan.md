# Implementation Plan: Physical AI & Humanoid Robotics Interactive Textbook Platform

**Branch**: `001-platform-implementation` | **Date**: 2026-01-17 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/001-platform-implementation/spec.md` with 84 functional requirements, 5 user stories (P1/P2), and 9 key entities.

---

## Summary

Build a comprehensive, multi-language interactive textbook platform using Docusaurus 3.x and React 18.x for teaching Physical AI and Humanoid Robotics. The platform combines static site generation for content delivery with client-side interactivity for quizzes, progress tracking, and authentication. MVP scope includes 4 core modules, GitHub OAuth authentication, 10-question quizzes per module, reading progress tracking, and GDPR-compliant cookie management. Phase 2 (future) will add backend services for persistent data, certificates, and advanced analytics.

---

## Technical Context

**Language/Version**: TypeScript 5.x, React 18.x, Node.js 18+
**Primary Dependencies**: Docusaurus 3.x, Tailwind CSS, Lucide Icons, i18n-js, Algolia/local search
**Storage**: localStorage (MVP), GitHub Pages (hosting), Phase 2 → PostgreSQL + backend
**Testing**: Jest (unit tests, 80%+ coverage), React Testing Library (component tests), Playwright (E2E)
**Target Platform**: Web browsers (desktop + mobile, 320px+), GitHub Pages static hosting
**Project Type**: Single monorepo (frontend-only for MVP; backend optional Phase 2)
**Performance Goals**: LCP < 2.5s, CLS < 0.1, Lighthouse ≥ 90, quiz load < 1s
**Constraints**:
- No backend required for MVP (localStorage for all persistence)
- GitHub Pages deployment (static site generation)
- GDPR compliance with cookie consent
- 100% JavaScript/TypeScript (no server-side rendering required)
**Scale/Scope**:
- 4 modules × 3-4 topics each = ~12-16 content pages
- 80 KB bundle size target (Docusaurus + React)
- 10,000+ concurrent users supported by GitHub Pages CDN
- 10 questions per module × 4 modules = 40 quizzes total

---

## Constitution Check

**Gate: Must pass before Phase 0 research**

✅ **Educational Excellence**: Platform structure aligns with 6,000-7,000 word content requirement, progressive learning (foundations→intermediate→advanced), and includes quiz system for knowledge validation.

✅ **Token-Friendly Architecture**: Section-by-section content generation strategy, static Markdown files cached on GitHub Pages, Docusaurus structure eliminates need for full-page LLM regeneration.

✅ **User-Centric Design**: Multi-language support (5 locales), search functionality, authentication (GitHub OAuth), reading progress tracking, GDPR consent, responsive design (320px+).

**No Constitution violations identified. Proceeding with Phase 0 research.**

---

## Project Structure

### Documentation (this feature)

```text
specs/001-platform-implementation/
├── spec.md                    # Feature specification (84 FRs, 5 user stories)
├── plan.md                    # This file (Phase 0-1 planning)
├── research.md                # Phase 0 output: Technology decisions, risk analysis
├── data-model.md              # Phase 1 output: Entities, localStorage schema
├── quickstart.md              # Phase 1 output: Local dev setup & deployment
├── contracts/                 # Phase 1 output: API/component contracts
│   ├── content-api.md         # Content loading interface
│   ├── quiz-api.md            # Quiz service interface
│   ├── auth-service.md        # GitHub OAuth flow
│   ├── progress-service.md    # Progress tracking
│   └── i18n-service.md        # Multi-language support
└── checklists/
    └── requirements.md        # Quality validation (40/40 items PASS)
```

### Source Code (repository root)

```text
docs/                          # Docusaurus content directory
├── index.md                   # Homepage (6 sections: hero, modules, why-it-matters, timeline, curriculum, hardware)
├── module-1-ros2/
│   ├── index.md
│   ├── topic-1-intro.md
│   ├── topic-2-nodes.md
│   └── quiz.json              # 10 questions + answers
├── module-2-control/
├── module-3-perception/
└── module-4-hardware/

src/
├── components/
│   ├── ModuleCard.tsx         # Reusable module card component
│   ├── TimeLine.tsx           # Project timeline visualization
│   ├── HardwareTabs.tsx       # Hardware showcase with tabs
│   ├── ReadingTime.tsx        # Reading time display
│   ├── Quiz.tsx               # Quiz question renderer
│   ├── QuizResults.tsx        # Results display with explanations
│   ├── SearchModal.tsx        # Global search interface (Cmd/Ctrl+K)
│   ├── CookieConsent.tsx      # GDPR cookie banner
│   ├── LanguageSelector.tsx   # Multi-language switcher
│   ├── Header.tsx             # Navigation with auth button
│   ├── AuthButton.tsx         # GitHub OAuth login button
│   ├── ProgressBar.tsx        # Reading/quiz progress indicator
│   └── [library components]/  # Button, Card, Form, etc. (Lucide icons)
├── services/
│   ├── auth-service.ts        # GitHub OAuth flow (login, token refresh, logout)
│   ├── quiz-service.ts        # Load questions, validate answers, score quiz
│   ├── progress-service.ts    # Track reading time, quiz completion, persist to localStorage
│   ├── i18n-service.ts        # Language switching, content translation lookup
│   ├── search-service.ts      # Full-text search (local implementation for MVP)
│   ├── cookie-service.ts      # Cookie consent preferences, GDPR compliance
│   └── content-service.ts     # Load markdown, parse front matter (reading time, metadata)
├── hooks/
│   ├── useAuth.ts             # Manage authentication state
│   ├── useProgress.ts         # Manage user progress state
│   ├── useLanguage.ts         # Manage language preference state
│   ├── useReadingTime.ts      # Calculate/track reading time during scroll
│   └── useLocalStorage.ts     # Persist data to localStorage
├── utils/
│   ├── constants.ts           # Colors, timings, breakpoints
│   ├── time-formatter.ts      # Format reading time (min/sec display)
│   └── validators.ts          # Quiz answer validation, data sanitization
├── styles/
│   ├── globals.css            # Global styles, CSS variables (colors, fonts)
│   ├── animations.css         # Keyframe definitions (glass-morphism, neural-grid)
│   └── responsive.css         # Mobile/tablet/desktop breakpoints
└── pages/
    └── [Docusaurus-managed via mdx]

tests/
├── unit/
│   ├── quiz-service.test.ts   # Quiz scoring, question selection logic
│   ├── progress-service.test.ts # Reading time calculation, persistence
│   ├── i18n-service.test.ts   # Translation lookup, RTL detection
│   ├── auth-service.test.ts   # Token refresh, logout behavior
│   └── components/
│       ├── Quiz.test.tsx      # Quiz rendering, answer selection, submission
│       ├── CookieConsent.test.tsx # Banner display, preference storage
│       └── SearchModal.test.tsx # Search input, result filtering, navigation
├── integration/
│   ├── homepage-flow.test.ts  # Hero → Module → Quiz flow
│   ├── auth-flow.test.ts      # OAuth login → authenticated state → quiz access
│   ├── i18n-flow.test.ts      # Language switch → URL change → content translation
│   └── progress-flow.test.ts  # Reading → Progress update → Persistence
└── e2e/
    ├── homepage.spec.ts       # Homepage load, hero animation, module navigation
    ├── quiz-flow.spec.ts      # Login → Quiz → Results → Progress update
    ├── search.spec.ts         # Search activation, result filtering, navigation
    └── cookie-consent.spec.ts # Banner → Customize → Save → Persistence

static/
├── images/
│   ├── modules/               # Module icons (4 modules)
│   ├── hardware/              # Hardware component images
│   └── diagrams/              # Technical diagrams (ROS architecture, etc.)
└── videos/
    └── tutorials/             # Optional: embedded tutorial videos

docusaurus.config.js           # Docusaurus configuration (i18n, plugins, favicon, etc.)
package.json                   # Dependencies (React, Docusaurus, Tailwind, testing libs)
.env.example                   # Environment template (GitHub OAuth client ID)
```

**Structure Decision**: Single monorepo with Docusaurus frontend-only architecture. Phase 2 will extract backend services into separate `/backend` directory when persistent database is needed. This minimizes complexity for MVP while maintaining clear separation of concerns.

---

## Complexity Tracking

No Constitution violations requiring justification. Architecture decisions align with all 3 principles:

| Decision | Alignment |
|----------|-----------|
| Frontend-only MVP | Token-Friendly: Simplifies generation/caching; Educational Excellence: Fast content delivery |
| localStorage for MVP | User-Centric: No account creation friction; compliance-ready (GDPR) |
| 5-language from start | User-Centric: Inclusive global design; built into Docusaurus i18n |
| GitHub OAuth only | User-Centric: No password management; compliance-ready; minimizes backend |

---

## Implementation Phases

### Phase 0: Research & Foundational Setup (1 week)

**Deliverables**:
- `research.md` - Technology decisions, risk analysis, threat model
- Environment setup: `.env`, GitHub OAuth app registration
- Initial Docusaurus project scaffold

**Tasks**:
- [ ] Resolve any NEEDS CLARIFICATION markers in spec (0 remaining)
- [ ] Document GitHub OAuth token refresh strategy (from clarification)
- [ ] Document quiz question pool rotation strategy (from clarification)
- [ ] Document scroll+time progress calculation algorithm (from clarification)
- [ ] Document session-based localStorage strategy (from clarification)
- [ ] Create GitHub OAuth app and document client ID/secret handling
- [ ] Set up local Node.js + Docusaurus project scaffold
- [ ] Initialize git branches for parallel work (auth, quiz, i18n, search)
- [ ] Create development environment checklist

---

### Phase 1: Architecture & Data Modeling (2 weeks)

**Deliverables**:
- `data-model.md` - Entity definitions, localStorage schema, validation rules
- `quickstart.md` - Local development setup, hot reload, testing workflow
- `contracts/` - API signatures for all services (auth, quiz, progress, i18n, search)
- Component library stubs (all components created with prop interfaces)

**Tasks**:
- [ ] Design localStorage schema for users, quizzes, progress, cookies, language preferences
- [ ] Define TypeScript interfaces for all 9 entities
- [ ] Create API contracts for all 5 services (auth, quiz, progress, i18n, search)
- [ ] Set up monorepo structure (src/, tests/, docs/, static/)
- [ ] Create all component skeletons with prop validation
- [ ] Create service skeletons with type signatures
- [ ] Write design decisions document (routing strategy, state management, styling approach)
- [ ] Create testing strategy document (unit vs. integration vs. E2E ratios)

---

### Phase 2: Implementation Sprint 1 - Core Features (2-3 weeks)

**Deliverables**:
- Homepage (6 sections) with responsive grid
- Authentication service (GitHub OAuth + token refresh)
- Reader progress tracking (scroll + time calculation)
- Module navigation (routing to /docs/module-*/index.md)

**User Stories Covered**: User Story 1 (homepage), User Story 2 (auth) - partial

**Tasks**:
- [ ] Implement Header component with auth button
- [ ] Implement Homepage with hero, modules, curriculum sections
- [ ] Implement GitHub OAuth flow (login button → OAuth redirect → session storage)
- [ ] Implement silent token refresh (background refresh + fallback to re-login)
- [ ] Implement reading time display (extract from front matter)
- [ ] Implement reading progress tracking (scroll detection + 30s time threshold)
- [ ] Implement ProgressBar component (visual indicator of reading completion)
- [ ] Implement Module navigation (render 4 module cards, navigate to /docs/module-*/index.md)
- [ ] Unit tests: Auth service (80%+ coverage)
- [ ] Unit tests: Progress service (80%+ coverage)
- [ ] E2E test: Homepage load → Module navigation

---

### Phase 3: Implementation Sprint 2 - Quiz System (2-3 weeks)

**Deliverables**:
- Quiz service with question randomization (different pool per retake)
- Quiz component with 10-question flow
- Results display with per-question explanations
- Progress update after quiz submission

**User Stories Covered**: User Story 2 (quiz + results) - complete

**Tasks**:
- [ ] Create quiz.json data structure for all 40 quizzes (4 modules × 10 questions)
- [ ] Implement QuizService.loadQuestions() with question pool rotation
- [ ] Implement QuizService.scoreQuiz() with 70% passing threshold
- [ ] Implement Quiz component (question renderer, answer selection, progress bar)
- [ ] Implement QuizResults component (score, pass/fail, explanations)
- [ ] Implement quiz persistence to localStorage
- [ ] Implement quiz retake tracking (different question pool)
- [ ] Unit tests: Quiz service (80%+ coverage)
- [ ] Unit tests: Quiz component (80%+ coverage)
- [ ] E2E test: Complete quiz flow (start → answer → submit → results → persist)
- [ ] Create quiz content: 40 questions with multiple-choice answers + explanations

---

### Phase 4: Implementation Sprint 3 - Multi-Language & Search (2-3 weeks)

**Deliverables**:
- Language switching (5 locales: en, ur, ar, zh, es)
- RTL layout switching
- Search modal with Cmd/Ctrl+K activation
- Content translation lookup

**User Stories Covered**: User Story 3 (i18n), User Story 4 (search)

**Tasks**:
- [ ] Set up Docusaurus i18n configuration (5 locales)
- [ ] Implement LanguageSelector component
- [ ] Implement RTL layout detection and CSS switching
- [ ] Translate all UI strings (4 languages + English)
- [ ] Implement SearchService with local full-text search
- [ ] Implement SearchModal component (activation, input, results, navigation)
- [ ] Add search result ranking/grouping by module
- [ ] Unit tests: i18n service (80%+ coverage)
- [ ] Unit tests: Search service (80%+ coverage)
- [ ] E2E test: Language switch → RTL layout verification
- [ ] E2E test: Search activation → result filtering → navigation
- [ ] Create content translations (4 languages × ~12 pages)

---

### Phase 5: Compliance & Polish (1-2 weeks)

**Deliverables**:
- GDPR cookie consent banner and preferences modal
- Accessibility audit (WCAG AA compliance)
- Performance optimization (LCP < 2.5s, CLS < 0.1, Lighthouse ≥ 90)
- Mobile responsiveness (320px+)

**User Stories Covered**: User Story 5 (cookies) - complete

**Tasks**:
- [ ] Implement CookieConsent banner
- [ ] Implement cookie preferences modal (3 categories: Essential, Analytics, Preferences)
- [ ] Implement cookie persistence and localStorage management
- [ ] Run accessibility audit (WCAG AA)
- [ ] Fix accessibility issues (color contrast, ARIA labels, keyboard nav)
- [ ] Optimize bundle size (code splitting, lazy loading)
- [ ] Optimize images (WebP, srcset for responsive)
- [ ] Test performance on slow networks (throttle to 3G)
- [ ] Test responsive design (320px, 768px, 1024px breakpoints)
- [ ] E2E test: Cookie banner flow (accept → customize → save → persist)
- [ ] Lighthouse audit (target ≥ 90 on all categories)
- [ ] Unit tests: CookieConsent component (80%+ coverage)

---

### Phase 6: Deployment & Launch (1 week)

**Deliverables**:
- GitHub Actions CI/CD pipeline
- GitHub Pages deployment configuration
- Production environment documentation
- Launch checklist (SEO, analytics, monitoring)

**Tasks**:
- [ ] Create GitHub Actions workflow (lint → test → build → deploy)
- [ ] Configure GitHub Pages for custom domain (if applicable)
- [ ] Set up environment variables (GitHub OAuth secrets)
- [ ] Create deployment documentation
- [ ] Create rollback procedure documentation
- [ ] Set up Sentry/error monitoring (optional)
- [ ] Create analytics tracking (privacy-compliant)
- [ ] Create SEO metadata (meta tags, sitemap)
- [ ] Final E2E regression test suite
- [ ] Performance monitoring setup (Web Vitals)

---

## Risk Analysis

| Risk | Blast Radius | Mitigation |
|------|--------------|-----------|
| **GitHub OAuth token expiry** | User locked out mid-session | Silent refresh before expiry; graceful re-login prompt; documented in FR-015/FR-016 |
| **localStorage quota exceeded** | Quiz/progress data loss | Clear old quizzes on submission; limit to last 5 attempts per module; implement cleanup service |
| **RTL layout bugs** | Poor UX for Arabic/Urdu users | Comprehensive RTL testing matrix; dedicated CSS modules for RTL; early user testing |
| **Performance degradation on slow networks** | Users abandon (LCP > 2.5s) | Aggressive code splitting; preload critical assets; skeleton screens during load |
| **Quiz question pool imbalance** | Users perceive lack of variety | Rotate pool every retake; validate distribution of difficulty; document in clarifications |
| **i18n content staleness** | Translated pages out of sync with English | Document single-source-of-truth (English); establish translation workflow; automated checks |

---

## Success Criteria Validation

After Phase 6 completion, platform must meet:

- ✅ **Performance**: LCP < 2.5s, CLS < 0.1, Lighthouse ≥ 90 (all categories)
- ✅ **Functionality**: All 84 FRs implemented; 100% quiz scoring accuracy; all routes accessible
- ✅ **User Experience**: Quizzes complete in < 10 minutes; 5 user stories fully validated
- ✅ **Accessibility**: WCAG AA compliance; screen reader tested; keyboard navigation verified
- ✅ **Quality**: 80%+ unit test coverage; all integration tests green; E2E regression suite automated
- ✅ **Deployment**: GitHub Actions CI/CD pipeline; zero-downtime deployments; rollback capability

---

## Next Steps

1. **Phase 0 Research**: Run to generate `research.md` with technology decisions and threat model
2. **Phase 0 Setup**: Initialize Docusaurus project, GitHub OAuth app, development environment
3. **Phase 1 Design**: Create data-model.md, contracts/, and component stubs
4. **Phase 2-6 Implementation**: Follow sprint schedule above, with weekly progress checkpoints

**Command to proceed**: `/sp.tasks` (after Phase 1 completes, generates detailed tasks.md with test cases)
