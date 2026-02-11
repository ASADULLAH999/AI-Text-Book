# Phase 1 Data Model: Entities, Schema & Validation

**Created**: 2026-01-17 | **Feature**: 001-platform-implementation | **Reference**: [plan.md](./plan.md)

---

## Overview

This document defines the 9 core entities for the Physical AI textbook platform. All data lives in localStorage (MVP) or server database (Phase 2). TypeScript interfaces provided for frontend implementation.

---

## Entity 1: User

**Purpose**: Represent authenticated user identity from GitHub OAuth.

### Schema

```typescript
interface User {
  // GitHub OAuth data
  github_id: string;              // GitHub user ID (unique)
  username: string;               // GitHub username
  email?: string;                 // GitHub email (optional)
  avatar_url: string;             // GitHub avatar URL

  // Session management
  access_token: string;           // GitHub OAuth access token
  refresh_token: string;          // GitHub OAuth refresh token
  token_expires_at: number;       // Unix timestamp (milliseconds)

  // Timestamps
  created_at: number;             // First login timestamp
  last_login: number;             // Last login timestamp

  // Optional: Phase 2 upgrades
  display_name?: string;          // User-set display name
  bio?: string;                   // User profile bio
  language_preference?: string;   // Preferred locale (en, ur, ar, zh, es)
  theme_preference?: "light" | "dark"; // UI theme
}
```

### localStorage Storage Location

```typescript
localStorage.getItem("auth")
// Returns:
{
  "github_id": "123456789",
  "username": "studentname",
  "email": "student@example.com",
  "avatar_url": "https://avatars.githubusercontent.com/u/123456789",
  "access_token": "gho_16C7e42F292c6912E7710c838347Ae178B4a",
  "refresh_token": "ghr_1B4a2e77838347a7E420314A7E2D5F30f29e38D8A",
  "token_expires_at": 1642425600000,
  "created_at": 1642339200000,
  "last_login": 1642422000000
}
```

### Validation Rules

- ✅ `github_id`: String, non-empty, unique per browser
- ✅ `username`: String, 1-39 characters (GitHub username rules)
- ✅ `email`: String, valid email format (optional)
- ✅ `avatar_url`: Valid HTTPS URL
- ✅ `access_token`: Non-empty string; validate length > 20
- ✅ `refresh_token`: Non-empty string; validate length > 20
- ✅ `token_expires_at`: Number > current timestamp (future)
- ✅ `created_at`, `last_login`: Number, valid Unix timestamp (past)

### Lifecycle

```
GitHub OAuth Flow:
  1. User clicks "Login with GitHub"
  2. Redirect to GitHub OAuth endpoint
  3. GitHub redirects to /auth/github/callback with code
  4. Frontend exchanges code for tokens (via GitHub OAuth)
  5. Store User object in localStorage
  6. Migrate sessionStorage → localStorage
  7. Display user avatar + username in header

Token Refresh Flow (Clarification Q2):
  1. Before API call, check if token_expires_at < now + 5min
  2. If yes, silently refresh using refresh_token
  3. Update access_token + token_expires_at
  4. Proceed with API call
  5. If refresh fails, prompt user to re-login

Logout Flow:
  1. User clicks logout button
  2. Clear localStorage["auth"]
  3. Clear user-specific data (progress, quizzes)
  4. Redirect to homepage
  5. Display "Logged out" confirmation
```

---

## Entity 2: Module

**Purpose**: Represent a learning module (e.g., "ROS 2 Fundamentals").

### Schema

```typescript
interface Module {
  id: string;                    // Unique identifier (e.g., "module-1-ros2")
  title: string;                 // Display title
  description: string;           // 1-2 sentence summary
  order: number;                 // Sort order (1-4)
  icon: string;                  // Icon name from Lucide Icons
  color: string;                 // Accent color (hex or tailwind class)
  topics: string[];              // Array of topic IDs (references)
  quiz_id: string;               // Reference to Quiz entity
  created_at: number;            // Creation timestamp
}
```

### File-Based Storage (Markdown)

```
docs/module-1-ros2/
├── index.md                     # Module overview (front matter has Module data)
├── topic-1-intro.md             # Topic 1 content
├── topic-2-nodes.md             # Topic 2 content
├── quiz.json                    # Quiz object with 15 questions

Front matter in index.md:
---
id: module-1-ros2
title: ROS 2 Fundamentals
description: Understand Robot Operating System 2 core concepts, nodes, and messaging
order: 1
icon: Package
color: cyan-500
topics:
  - intro
  - nodes
  - messaging
quiz_id: quiz-module-1
---
```

### Validation Rules

- ✅ `id`: Kebab-case, globally unique (e.g., "module-1-ros2")
- ✅ `title`: String, 2-100 characters
- ✅ `description`: String, 10-200 characters
- ✅ `order`: Integer, 1-4 (only 4 modules in MVP)
- ✅ `icon`: Valid Lucide icon name
- ✅ `color`: Valid tailwind class (e.g., "cyan-500")
- ✅ `topics`: Array of strings, non-empty, unique
- ✅ `quiz_id`: References valid Quiz entity

### Lifecycle

- ✅ Created during content setup (not user-created)
- ✅ Loaded from Docusaurus front matter
- ✅ Read-only (no user modifications)
- ✅ Deleted only by admin (Phase 2)

---

## Entity 3: Content Page

**Purpose**: Represent a single content page within a module.

### Schema

```typescript
interface ContentPage {
  id: string;                    // Unique identifier (e.g., "module-1-ros2/intro")
  module_id: string;             // Parent module reference
  topic: string;                 // Topic name
  title: string;                 // Page title
  content: string;               // Markdown content (raw)
  reading_time: number;          // Estimated reading time in seconds
  word_count: number;            // Total word count
  sections: Section[];           // Array of major sections (h2+ headings)
  metadata: {
    author?: string;
    tags?: string[];
    difficulty?: "beginner" | "intermediate" | "advanced";
    code_examples: number;       // Count of code blocks
  };
  created_at: number;            // Timestamp
  updated_at: number;            // Last modified timestamp
}

interface Section {
  id: string;                    // e.g., "section-1-intro-to-nodes"
  heading: string;               // h2 or h3 heading text
  word_count: number;            // Words in this section
  level: 2 | 3 | 4;              // Heading level (h2/h3/h4)
}
```

### Markdown File Storage

```
docs/module-1-ros2/topic-1-intro.md
---
id: module-1-ros2/topic-1-intro
module_id: module-1-ros2
topic: intro
title: Introduction to ROS 2
difficulty: beginner
tags: [ros2, nodes, messaging]
---

# Introduction to ROS 2

Content here... 6000-7000 words per page.

## Section 1: What is ROS 2?
...

## Section 2: Architecture Overview
...
```

### Validation Rules

- ✅ `id`: Kebab-case format "module-id/topic-id"
- ✅ `content`: Non-empty markdown string
- ✅ `reading_time`: Calculated as word_count / 200 (avg reading speed)
- ✅ `word_count`: >= 6000 and <= 7000 (per spec)
- ✅ `sections`: Non-empty array, at least 3 major sections
- ✅ `difficulty`: One of beginner/intermediate/advanced
- ✅ `created_at`, `updated_at`: Valid Unix timestamp

### Lifecycle

- ✅ Created by content team (not users)
- ✅ Loaded from Markdown files (Docusaurus)
- ✅ Read-only for users
- ✅ Supports versioning (git history)

---

## Entity 4: Quiz

**Purpose**: Represent a quiz assessment for a module.

### Schema

```typescript
interface Quiz {
  id: string;                    // Unique identifier (e.g., "quiz-module-1")
  module_id: string;             // Parent module reference
  title: string;                 // Display title (e.g., "ROS 2 Fundamentals Quiz")
  description: string;           // Quiz summary
  questions: QuizQuestion[];     // Array of 15 questions (show 10 per attempt)
  passing_score: number;         // 70% required to pass
  time_limit: number;            // In seconds (600 = 10 minutes)
  attempt_limit?: number;        // Max retakes (optional; default unlimited)
  created_at: number;            // Timestamp

  // Metadata
  metadata: {
    difficulty_distribution: {
      easy: number;              // Count of easy questions
      medium: number;            // Count of medium questions
      hard: number;              // Count of hard questions
    };
    estimated_time: number;      // Average completion time in seconds
  };
}
```

### File-Based Storage (JSON)

```json
{
  "id": "quiz-module-1",
  "module_id": "module-1-ros2",
  "title": "ROS 2 Fundamentals Quiz",
  "description": "Test your knowledge of ROS 2 core concepts",
  "passing_score": 70,
  "time_limit": 600,
  "questions": [...],  // See QuizQuestion entity below
  "metadata": {
    "difficulty_distribution": {
      "easy": 5,
      "medium": 7,
      "hard": 3
    },
    "estimated_time": 480
  }
}
```

### Validation Rules

- ✅ `id`: Kebab-case, globally unique
- ✅ `questions`: Array of 15 questions (exactly 15, to allow pool rotation per Q1)
- ✅ `passing_score`: Integer 0-100 (70% specified)
- ✅ `time_limit`: Integer > 0, typically 600-1200 seconds
- ✅ `difficulty_distribution`: Sum must equal 15; each >= 0

### Lifecycle (from Clarification Q1)

```
Quiz Attempt Flow:
  1. User clicks "Take Quiz" on module page
  2. Load Quiz object + randomly select 10 of 15 questions
  3. Store selected question IDs in localStorage (prevent re-selection on refresh)
  4. Display Question 1 of 10
  5. User answers 10 questions
  6. Submit quiz

Retake Flow:
  1. User clicks "Retake Quiz"
  2. Load Quiz object + randomly select 10 NEW questions (different from previous attempt)
  3. Clear previous answers from localStorage
  4. Start new attempt
  5. Store result + update quiz_attempts count in User Progress
```

---

## Entity 5: Quiz Question

**Purpose**: Represent a single quiz question.

### Schema

```typescript
interface QuizQuestion {
  id: string;                    // Unique identifier (e.g., "q-module1-001")
  quiz_id: string;               // Parent quiz reference

  // Question content
  question_text: string;         // Question prompt (1-200 characters)
  question_type: "multiple-choice" | "true-false"; // Question type

  // Options
  options: {
    label: string;               // A, B, C, D (or True/False)
    text: string;                // Option text
  }[];

  // Correct answer
  correct_answer: string;        // Label of correct option (A, B, C, D)

  // Feedback
  explanation: string;           // Explanation of correct answer (why correct)
  option_explanations?: {        // Why each option is wrong/right
    [key: string]: string;
  };

  // Metadata
  difficulty: "easy" | "medium" | "hard";
  tags: string[];                // Topics covered (e.g., ["nodes", "messaging"])
  created_at: number;            // Timestamp
}
```

### JSON Storage Example

```json
{
  "id": "q-module1-001",
  "quiz_id": "quiz-module-1",
  "question_text": "What is the primary role of nodes in ROS 2?",
  "question_type": "multiple-choice",
  "options": [
    { "label": "A", "text": "To manage package distribution" },
    { "label": "B", "text": "To execute independent processes that communicate via topics/services" },
    { "label": "C", "text": "To store persistent data" },
    { "label": "D", "text": "To compile C++ code" }
  ],
  "correct_answer": "B",
  "explanation": "Nodes are the fundamental ROS 2 process units. Each node is an independent executable that communicates with other nodes through topics (pub/sub) or services (request/reply). This architecture enables modular, scalable robotics applications.",
  "option_explanations": {
    "A": "That's the role of repositories/package managers, not nodes.",
    "B": "Correct! Nodes are independent processes that form the computational graph.",
    "C": "Databases handle persistence; nodes are computational units.",
    "D": "Compilation is build-time; nodes run at runtime."
  },
  "difficulty": "easy",
  "tags": ["nodes", "architecture"],
  "created_at": 1642339200000
}
```

### Validation Rules

- ✅ `id`: Unique within quiz
- ✅ `question_text`: 10-200 characters, no HTML/scripts
- ✅ `options`: Multiple-choice: 4 options; true-false: 2 options
- ✅ `correct_answer`: Must match one of option labels
- ✅ `explanation`: 50-500 characters, clear and educational
- ✅ `difficulty`: One of easy/medium/hard
- ✅ `tags`: Non-empty array, relevant to module content

### Question Pool Rotation (Q1 Clarification)

```typescript
// When loading quiz:
function selectQuestionsForAttempt(quiz: Quiz, attemptNumber: number): QuizQuestion[] {
  // Get all 15 questions
  const allQuestions = quiz.questions;

  // Shuffle using Fisher-Yates with seed based on attempt number
  const shuffled = shuffleWithSeed(allQuestions, attemptNumber);

  // Select first 10
  return shuffled.slice(0, 10);
}

// Different pool per retake:
// - First attempt: seed=1 → questions [q1, q3, q5, q8, q2, q12, q4, q14, q7, q11]
// - Second attempt: seed=2 → questions [q6, q9, q13, q15, q1, q5, q10, q3, q12, q2]
// - Different 10 questions selected each time
```

---

## Entity 6: Quiz Attempt

**Purpose**: Record a user's attempt to complete a quiz.

### Schema

```typescript
interface QuizAttempt {
  id: string;                    // Unique identifier (UUID)
  user_id: string;               // GitHub user ID (reference)
  quiz_id: string;               // Quiz reference
  module_id: string;             // Module reference (denormalized for query)

  // Question pool
  selected_question_ids: string[]; // Array of 10 question IDs selected for this attempt

  // User answers
  answers: {
    [questionId: string]: string; // Map of question_id → user's selected answer (A, B, C, D)
  };

  // Scoring
  score: number;                 // Percentage (0-100)
  passed: boolean;               // score >= 70?
  correct_count: number;         // Number of correct answers (out of 10)

  // Timing
  started_at: number;            // When user started quiz
  submitted_at: number;          // When user submitted quiz
  duration: number;              // Duration in seconds (submitted_at - started_at)

  // Metadata
  attempt_number: number;        // 1st attempt, 2nd attempt, etc.
  browser_user_agent: string;    // For analytics (Phase 2)

  // Optional: Explanations shown to user (for learning)
  explanations_shown: boolean;   // Did user view explanations after submit?
}
```

### localStorage Storage Location

```typescript
localStorage.getItem("quizzes")
// Returns:
{
  "module-1-ros2": {
    "attempts": [
      {
        "id": "uuid-1234-5678",
        "user_id": "123456789",
        "quiz_id": "quiz-module-1",
        "module_id": "module-1-ros2",
        "selected_question_ids": ["q-module1-001", "q-module1-003", ...],
        "answers": {
          "q-module1-001": "B",
          "q-module1-003": "A",
          ...
        },
        "score": 80,
        "passed": true,
        "correct_count": 8,
        "started_at": 1642422000000,
        "submitted_at": 1642422480000,
        "duration": 480,
        "attempt_number": 1
      },
      { ... },  // 2nd attempt (different question pool)
      { ... }   // 3rd attempt, etc.
    ],
    "last_score": 80,
    "best_score": 85,
    "total_attempts": 3,
    "passed_attempts": 2
  }
}
```

### Validation Rules

- ✅ `id`: Valid UUID v4
- ✅ `answers`: All keys are valid question IDs from selected_question_ids
- ✅ `score`: Integer 0-100
- ✅ `passed`: Exactly score >= 70
- ✅ `duration`: positive integer (seconds)
- ✅ `attempt_number`: >= 1, sequential
- ✅ `submitted_at` > `started_at`

### Quiz Scoring Algorithm

```typescript
function scoreQuiz(attempt: QuizAttempt, questions: QuizQuestion[]): QuizAttempt {
  let correctCount = 0;

  // Map question ID → question object
  const questionMap = new Map(questions.map(q => [q.id, q]));

  // Score each answer
  for (const [questionId, userAnswer] of Object.entries(attempt.answers)) {
    const question = questionMap.get(questionId);
    if (question && question.correct_answer === userAnswer) {
      correctCount++;
    }
  }

  // Calculate percentage (10 questions total)
  const score = Math.round((correctCount / 10) * 100);

  return {
    ...attempt,
    correct_count: correctCount,
    score,
    passed: score >= 70
  };
}
```

---

## Entity 7: User Progress

**Purpose**: Track reading and quiz progress per module.

### Schema

```typescript
interface UserProgress {
  user_id: string;               // GitHub user ID
  module_id: string;             // Module reference

  // Reading progress (from Clarification Q3)
  reading_time: number;          // Seconds spent reading (30s+ per section)
  reading_progress: number;      // Percentage (0-100) based on scroll + time
  reading_completed_sections: string[]; // Array of section IDs completed
  reading_started_at: number;    // First visit to module
  reading_last_visited: number;  // Last time user visited

  // Quiz progress
  quiz_score: number;            // Latest quiz score (0-100)
  quiz_passed: boolean;          // Passed quiz (score >= 70)?
  quiz_attempts: number;         // Total retakes
  quiz_best_score: number;       // Highest score across attempts
  quiz_first_attempt_at: number; // When user first started quiz
  quiz_last_attempt_at: number;  // When user last submitted quiz

  // Certificate (Phase 2)
  certificate_earned?: boolean;
  certificate_earned_at?: number;

  // Timestamps
  created_at: number;            // First activity in module
  updated_at: number;            // Last activity
}
```

### localStorage Storage Location

```typescript
localStorage.getItem("progress")
// Returns:
{
  "module-1-ros2": {
    "user_id": "123456789",
    "module_id": "module-1-ros2",
    "reading_time": 1250,
    "reading_progress": 75,
    "reading_completed_sections": ["section-1-intro", "section-2-architecture"],
    "reading_started_at": 1642420000000,
    "reading_last_visited": 1642422000000,
    "quiz_score": 80,
    "quiz_passed": true,
    "quiz_attempts": 2,
    "quiz_best_score": 85,
    "quiz_first_attempt_at": 1642421000000,
    "quiz_last_attempt_at": 1642422000000,
    "created_at": 1642420000000,
    "updated_at": 1642422000000
  },
  "module-2-control": { ... },
  "module-3-perception": { ... },
  "module-4-hardware": { ... }
}
```

### Reading Progress Algorithm (Q3 Clarification)

```typescript
function trackReadingProgress(contentPage: ContentPage, section: Section, visible: boolean, visibleTime: number): void {
  if (visible && visibleTime >= 30) {
    // Section read for >= 30 seconds
    progress.reading_time += visibleTime;
    progress.reading_completed_sections.push(section.id);
  }

  // Calculate overall progress
  const totalWords = contentPage.word_count;
  const wordsRead = progress.reading_completed_sections
    .map(sectionId => contentPage.sections.find(s => s.id === sectionId)?.word_count || 0)
    .reduce((a, b) => a + b, 0);

  progress.reading_progress = Math.round((wordsRead / totalWords) * 100);
}
```

### Validation Rules

- ✅ `reading_time`: Non-negative integer (seconds)
- ✅ `reading_progress`: 0-100 (percentage)
- ✅ `quiz_score`: 0-100 or null (if not attempted)
- ✅ `quiz_attempts`: >= 0
- ✅ `quiz_best_score` >= `quiz_score` (best is always highest)
- ✅ `reading_last_visited` >= `reading_started_at`
- ✅ `quiz_last_attempt_at` >= `quiz_first_attempt_at`

---

## Entity 8: Cookie Preferences

**Purpose**: Store user's GDPR cookie consent choices.

### Schema

```typescript
interface CookiePreferences {
  user_id?: string;              // GitHub user ID (optional; null for anonymous)

  // Consent categories
  essential: boolean;            // Always true (required for site function)
  analytics: boolean;            // Allow Google Analytics / similar
  preferences: boolean;          // Allow personalization (language, theme, etc.)

  // Timestamps
  created_at: number;            // When user first made choice
  updated_at: number;            // Last time user updated preferences

  // Cookie banner state
  banner_dismissed: boolean;     // User clicked "Accept All" or "Reject Non-Essential"

  // Marketing (Phase 2, optional)
  marketing?: boolean;
}
```

### localStorage Storage Location

```typescript
localStorage.getItem("cookies")
// Returns:
{
  "essential": true,
  "analytics": false,
  "preferences": true,
  "created_at": 1642339200000,
  "updated_at": 1642422000000,
  "banner_dismissed": true
}
```

### GDPR Compliance (Q4 Clarification)

```
Banner Display Flow:
  1. User visits site for first time (cookies cleared)
  2. Check localStorage["cookies"]
  3. If not set → display GDPR banner
  4. User clicks:
     a. "Accept All" → essential=true, analytics=true, preferences=true
     b. "Reject Non-Essential" → essential=true, analytics=false, preferences=false
     c. "Customize" → open modal for granular choices
  5. Store CookiePreferences in localStorage
  6. Don't display banner again (until user explicitly resets)

Banner Reset:
  - User clicks "Cookie Settings" in footer
  - Can modify preferences
  - Preferences persist across sessions (localStorage)
  - Clear button: Clear all cookies + localStorage (GDPR right to be forgotten)
```

### Validation Rules

- ✅ `essential`: Always true (required for site to function)
- ✅ `analytics`, `preferences`: Boolean (true/false)
- ✅ `created_at`, `updated_at`: Valid Unix timestamp
- ✅ `banner_dismissed`: Boolean

---

## Entity 9: Language Preference

**Purpose**: Store user's language/locale choice.

### Schema

```typescript
interface LanguagePreference {
  user_id?: string;              // GitHub user ID (optional; null for anonymous)
  preferred_locale: string;      // en, ur, ar, zh, es
  auto_detected: boolean;        // Was locale detected from browser settings?
  created_at: number;            // When preference set
  updated_at: number;            // Last modified
}
```

### localStorage Storage Location

```typescript
localStorage.getItem("language")
// Returns:
{
  "preferred_locale": "ur",
  "auto_detected": false,
  "created_at": 1642420000000,
  "updated_at": 1642422000000
}
```

### Language Switching Flow

```
User Changes Language:
  1. Click language selector (globe icon in header)
  2. Dropdown shows 5 locales with flags
  3. User selects "Urdu"
  4. Update LanguagePreference in localStorage
  5. Update Docusaurus i18n state
  6. URL changes from /docs/... to /ur/docs/...
  7. RTL layout auto-activates
  8. All UI strings translate (from i18n files)
  9. Code examples stay English
  10. Persist preference across sessions

Locale Detection (First Visit):
  1. Check localStorage["language"]
  2. If not set, detect from browser language (navigator.language)
  3. Match browser locale to supported locales (en, ur, ar, zh, es)
  4. If no match, default to English
  5. Auto-detect flag set to true
  6. Store in localStorage
```

### Supported Locales

| Locale | Language | Direction | RTL |
|--------|----------|-----------|-----|
| `en` | English | LTR | No |
| `ur` | Urdu | RTL | Yes |
| `ar` | Arabic | RTL | Yes |
| `zh` | Chinese (Simplified) | LTR | No |
| `es` | Spanish | LTR | No |

### Validation Rules

- ✅ `preferred_locale`: One of [en, ur, ar, zh, es]
- ✅ `auto_detected`: Boolean
- ✅ `created_at`, `updated_at`: Valid Unix timestamp

---

## Data Relationships (ER Diagram)

```
┌─────────────────┐
│     User        │
├─────────────────┤
│ github_id (PK)  │◄─────────┐
│ username        │          │
│ access_token    │          │
│ email           │          │
└─────────────────┘          │
                             │ 1:M
                             │
┌──────────────────────┐     │
│   UserProgress       │     │
├──────────────────────┤     │
│ user_id (FK) ────────┼─────┘
│ module_id (FK)       │
│ reading_time         │
│ quiz_score           │
│ quiz_attempts        │
└──────────────────────┘
         │ M:1
         │
    ┌────▼────────────┐
    │     Module      │
    ├─────────────────┤
    │ id (PK)         │
    │ title           │
    │ topics[]        │
    │ quiz_id (FK)    │
    └─────────────────┘
             │ 1:1
             │
    ┌────────▼────────┐
    │      Quiz       │
    ├─────────────────┤
    │ id (PK)         │
    │ questions[]     │◄──────────┐
    │ passing_score   │           │ 1:M
    │ time_limit      │           │
    └─────────────────┘           │
             ▲                    │
             │                    │
             └────────────────────┘
           QuizQuestion

┌──────────────────────┐     ┌──────────────────────┐
│  QuizAttempt         │     │  ContentPage         │
├──────────────────────┤     ├──────────────────────┤
│ id (PK)              │     │ id (PK)              │
│ user_id (FK)         │     │ module_id (FK)       │
│ quiz_id (FK)         │     │ content              │
│ answers{}            │     │ word_count           │
│ score                │     │ reading_time         │
│ passed               │     │ sections[]           │
└──────────────────────┘     └──────────────────────┘

┌──────────────────────┐     ┌──────────────────────┐
│ CookiePreferences    │     │LanguagePreference    │
├──────────────────────┤     ├──────────────────────┤
│ user_id? (optional)  │     │ user_id? (optional)  │
│ essential            │     │ preferred_locale     │
│ analytics            │     │ auto_detected        │
│ preferences          │     │ created_at           │
│ banner_dismissed     │     │ updated_at           │
└──────────────────────┘     └──────────────────────┘
```

---

## localStorage Schema (Complete)

```typescript
interface LocalStorageSchema {
  // Authentication (null if not logged in)
  auth?: User;

  // User progress (one entry per module)
  progress: {
    [module_id: string]: UserProgress;
  };

  // Quiz attempts (one entry per module)
  quizzes: {
    [module_id: string]: {
      attempts: QuizAttempt[];
      last_score: number;
      best_score: number;
      total_attempts: number;
      passed_attempts: number;
    };
  };

  // GDPR consent
  cookies: CookiePreferences;

  // Language preference
  language: LanguagePreference;

  // UI state (transient, can be cleared)
  ui_state?: {
    theme: "light" | "dark";
    sidebar_open: boolean;
    last_visited_module?: string;
  };

  // Metadata
  schema_version: string;      // e.g., "1.0.0"
  last_updated: number;        // Unix timestamp
}
```

### Example localStorage after user activity:

```json
{
  "auth": {
    "github_id": "123456789",
    "username": "studentname",
    "access_token": "gho_...",
    "refresh_token": "ghr_...",
    "token_expires_at": 1642425600000
  },
  "progress": {
    "module-1-ros2": {
      "reading_progress": 75,
      "quiz_score": 80,
      "quiz_passed": true,
      "quiz_attempts": 2,
      "quiz_best_score": 85
    },
    "module-2-control": {
      "reading_progress": 40,
      "quiz_score": null,
      "quiz_attempts": 0
    }
  },
  "quizzes": {
    "module-1-ros2": {
      "attempts": [
        {
          "id": "uuid-1",
          "selected_question_ids": ["q1", "q3", "q5", ...],
          "answers": { "q1": "B", "q3": "A", ... },
          "score": 80,
          "attempt_number": 1
        },
        {
          "id": "uuid-2",
          "selected_question_ids": ["q2", "q4", "q6", ...],  // Different pool
          "answers": { "q2": "C", "q4": "B", ... },
          "score": 85,
          "attempt_number": 2
        }
      ]
    }
  },
  "cookies": {
    "essential": true,
    "analytics": false,
    "preferences": true,
    "banner_dismissed": true
  },
  "language": {
    "preferred_locale": "en",
    "auto_detected": false
  },
  "ui_state": {
    "theme": "dark",
    "sidebar_open": true,
    "last_visited_module": "module-1-ros2"
  },
  "schema_version": "1.0.0",
  "last_updated": 1642422000000
}
```

---

## Data Migration & Upgrades

### Phase 1 → Phase 2 (Backend Introduction)

```typescript
// Phase 2: Add server persistence
interface Phase2Changes {
  // New fields in User
  user_id: string;              // Server-generated UUID (replaces github_id)
  synced_at: number;            // Last sync timestamp

  // New table: UserAccount (links GitHub → server user)
  UserAccount: {
    user_id: string;
    github_id: string;
    provider: "github";
    linked_at: number;
  };

  // Deprecate localStorage storage, replace with API calls
  // Keep localStorage as cache for offline support
  // Implement sync service: background sync to server
}

// Migration strategy:
// 1. Read from localStorage (Phase 1)
// 2. Migrate to server on first login (Phase 2)
// 3. Keep localStorage as cache with TTL (time-to-live)
// 4. Implement conflict resolution (server wins on conflict)
```

---

## Validation & Constraints

### Data Type Constraints

| Entity | Field | Type | Required | Constraint |
|--------|-------|------|----------|-----------|
| User | github_id | string | ✅ | Non-empty, unique |
| User | access_token | string | ✅ | Length >= 20 |
| Module | id | string | ✅ | Kebab-case, globally unique |
| Module | order | number | ✅ | 1-4 (only 4 modules) |
| QuizQuestion | question_text | string | ✅ | 10-200 characters |
| QuizAttempt | answers | object | ✅ | Keys match question IDs |
| UserProgress | reading_progress | number | ✅ | 0-100 |
| CookiePreferences | essential | boolean | ✅ | Always true |
| LanguagePreference | preferred_locale | string | ✅ | One of [en, ur, ar, zh, es] |

---

## Testing Data (Seeds)

### Sample Quiz Attempt

```typescript
const sampleAttempt: QuizAttempt = {
  id: "test-attempt-001",
  user_id: "123456789",
  quiz_id: "quiz-module-1",
  module_id: "module-1-ros2",
  selected_question_ids: ["q-001", "q-003", "q-005", "q-008", "q-002", "q-012", "q-004", "q-014", "q-007", "q-011"],
  answers: {
    "q-001": "B",
    "q-003": "A",
    "q-005": "C",
    "q-008": "B",
    "q-002": "D",
    "q-012": "A",
    "q-004": "B",
    "q-014": "C",
    "q-007": "B",
    "q-011": "A"
  },
  score: 80,
  passed: true,
  correct_count: 8,
  started_at: Date.now() - 600000,
  submitted_at: Date.now(),
  duration: 480,
  attempt_number: 1
};
```

---

## Next Steps

1. **Implement TypeScript interfaces** (src/types/entities.ts)
2. **Create validation functions** (src/utils/validators.ts)
3. **Build service layers** (src/services/*-service.ts)
4. **Write unit tests** (tests/unit/data-model.test.ts)
5. **Create database migration** (Phase 2: backend schema)

---

**Document Status**: Approved | **Next Review**: End of Phase 1
