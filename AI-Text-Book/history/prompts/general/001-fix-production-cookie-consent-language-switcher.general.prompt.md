---
id: 001
title: Fix production cookie consent and add language switcher
stage: misc
date: 2026-01-23
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: 002-rag-chatbot
user: developer
command: none
labels: ["bug-fix", "enhancement", "production", "i18n", "gdpr", "ssr"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
 - src/theme/Root.tsx
 - docusaurus.config.ts
tests:
 - Manual testing: npm run build && npm run serve
 - Verified language dropdown appears in navbar
 - Verified cookie consent appears in production build
---

## Prompt

User reported two issues with production build (`npm run build && npm run serve`):

1. **Cookie consent not showing**: Cookie consent banner was working in development mode (`npm run start`) but not appearing in production build
2. **Language switcher missing**: Language dropdown was not appearing in the navbar to allow users to switch between English, Urdu, Arabic, Chinese, and Spanish
3. **Search engine confusion**: User observed search worked in production but not in development, causing confusion about expected behavior

User request: "listen i see some thing is missing in my project production level the missing thing is my language change button i want this button on my production level mode and properly all language is working and change language when i change and cookies is also missing my production level server"

## Response snapshot

**Root Cause Analysis:**

1. **Cookie Consent Issue**:
   - CookieConsent component uses `localStorage` (browser-only API)
   - Docusaurus production build performs Server-Side Rendering (SSR)
   - During SSR, `localStorage` doesn't exist, causing component to fail silently

2. **Language Switcher Issue**:
   - Missing `localeDropdown` configuration in navbar items
   - Docusaurus provides built-in locale dropdown but needs explicit configuration

3. **Search Engine Behavior** (educational clarification):
   - `@easyops-cn/docusaurus-search-local` only generates index during build
   - This is expected behavior - search works in production, not in development

**Solutions Applied:**

1. **Fixed Cookie Consent** - `src/theme/Root.tsx`
   ```tsx
   // Before
   <CookieConsent />

   // After
   <BrowserOnly fallback={<div />}>
     {() => <CookieConsent />}
   </BrowserOnly>
   ```
   - Wrapped component in Docusaurus `BrowserOnly` wrapper
   - Ensures localStorage is only accessed in browser, not during SSR

2. **Added Language Dropdown** - `docusaurus.config.ts`
   ```typescript
   items: [
     // ... existing items
     {
       type: 'localeDropdown',
       position: 'right',
     },
     // ... other items
   ]
   ```
   - Added built-in Docusaurus locale dropdown
   - Positioned in top-right navbar
   - Automatically displays all configured locales (en, ur, ar, zh, es)

**Testing:**
- Built production version: `npm run build`
- Served locally: `npm run serve`
- Verified both features working at http://localhost:3000/

## Outcome

- ✅ Impact: Cookie consent now appears in both development and production modes. Language switcher allows users to switch between 5 languages seamlessly.
- 🧪 Tests: Manual testing confirmed both features working in production build
- 📁 Files: Modified 2 files (src/theme/Root.tsx, docusaurus.config.ts)
- 🔁 Next prompts: User may want to test language switching functionality, customize cookie preferences, or add dev-mode search plugin
- 🧠 Reflection: The SSR issue with localStorage is a common pitfall in Docusaurus. BrowserOnly wrapper is the standard solution. Language dropdown was simply a configuration gap.

## Evaluation notes (flywheel)

- Failure modes observed: Initial cookie consent implementation didn't account for SSR. Language configuration was incomplete.
- Graders run and results (PASS/FAIL): Manual verification PASS - both features visible and functional in production
- Prompt variant (if applicable): none
- Next experiment (smallest change to try): Could add dev-friendly search plugin (docusaurus-lunr-search) if user wants search in development mode
