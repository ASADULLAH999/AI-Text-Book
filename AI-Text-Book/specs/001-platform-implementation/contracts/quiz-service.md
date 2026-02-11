# Contract: Quiz Service

**Created**: 2026-01-17 | **Feature**: 001-platform-implementation

---

## Overview

The Quiz Service manages quiz loading, question selection with pool rotation (Clarification Q1), answer validation, and scoring. All quiz data lives in static JSON files (content layer) with attempts stored in localStorage (user layer).

---

## Interface

### Service Methods

#### `loadQuiz(module_id: string): Promise<Quiz>`

Load quiz definition from JSON file.

```typescript
function loadQuiz(module_id: string): Promise<Quiz>

// Parameters:
// - module_id (string): Module identifier (e.g., "module-1-ros2")

// Returns: Promise<Quiz>
// - Resolves with Quiz object containing 15 questions
// - Rejects if quiz file not found or JSON invalid

// Errors:
// - "Quiz not found" (file doesn't exist)
// - "Invalid JSON" (malformed quiz.json)
// - "Network error" (file fetch failed)

// Example:
const quiz = await quizService.loadQuiz('module-1-ros2')
console.log(quiz.title)  // "ROS 2 Fundamentals Quiz"
console.log(quiz.questions.length)  // 15
```

#### `selectQuestions(quiz: Quiz, attemptNumber: number): QuizQuestion[]`

Select 10 questions from pool of 15 with rotation per retake (Q1 Clarification).

```typescript
function selectQuestions(quiz: Quiz, attemptNumber: number): QuizQuestion[]

// Parameters:
// - quiz (Quiz): Quiz object with 15 questions
// - attemptNumber (number): Which attempt (1st, 2nd, 3rd, etc.)

// Returns: QuizQuestion[] (array of 10 questions)
// - Different questions selected per attempt (pool rotation)
// - Deterministic selection (same attempt # always gets same questions)
// - No duplicates within single attempt

// Algorithm:
// 1. Seed random number generator with attemptNumber
// 2. Shuffle all 15 questions using Fisher-Yates
// 3. Select first 10 shuffled questions
// 4. Different seed per attempt = different pool per retake

// Example:
const quiz = await quizService.loadQuiz('module-1-ros2')
const questions1 = quizService.selectQuestions(quiz, 1)  // First attempt
const questions2 = quizService.selectQuestions(quiz, 2)  // Second attempt
// questions1 and questions2 have different questions (different pools)
```

#### `scoreQuiz(attempt: QuizAttempt, selectedQuestions: QuizQuestion[]): number`

Calculate score and validate answers.

```typescript
function scoreQuiz(attempt: QuizAttempt, selectedQuestions: QuizQuestion[]): number

// Parameters:
// - attempt (QuizAttempt): User's answers and metadata
// - selectedQuestions (QuizQuestion[]): The 10 questions user answered

// Returns: number (percentage score 0-100)

// Algorithm:
// 1. For each selected question:
//    - Get user's answer from attempt.answers[question_id]
//    - Compare to question.correct_answer
//    - Increment score if match
// 2. Calculate percentage: (correct_count / 10) * 100
// 3. Round to nearest integer

// Example:
const attempt: QuizAttempt = {
  answers: {
    'q1': 'B',
    'q2': 'A',
    'q3': 'C',
    // ... 7 more answers
  },
  // ... other fields
}
const score = quizService.scoreQuiz(attempt, selectedQuestions)
console.log(score)  // 80 (8 out of 10 correct)
```

#### `validateAnswer(answer: string, question: QuizQuestion): boolean`

Validate if answer is one of the valid options.

```typescript
function validateAnswer(answer: string, question: QuizQuestion): boolean

// Parameters:
// - answer (string): User's selected answer (A, B, C, D)
// - question (QuizQuestion): The question being answered

// Returns: boolean
// - true if answer is valid option (A, B, C, D or True, False)
// - false if answer is invalid or missing

// Example:
const question = {...}  // Multiple-choice question with A, B, C, D
console.log(validateAnswer('B', question))  // true
console.log(validateAnswer('E', question))  // false
console.log(validateAnswer('', question))   // false
```

#### `isPassingScore(score: number): boolean`

Check if score meets passing threshold.

```typescript
function isPassingScore(score: number): boolean

// Parameters:
// - score (number): Quiz score (0-100)

// Returns: boolean
// - true if score >= 70
// - false if score < 70

// Example:
console.log(isPassingScore(80))  // true
console.log(isPassingScore(65))  // false
```

#### `getQuizAttempts(module_id: string, user_id: string): QuizAttempt[]`

Retrieve all quiz attempts for a module from localStorage.

```typescript
function getQuizAttempts(module_id: string, user_id: string): QuizAttempt[]

// Parameters:
// - module_id (string): Module identifier (e.g., "module-1-ros2")
// - user_id (string): GitHub user ID

// Returns: QuizAttempt[] (array of attempts, oldest to newest)
// - Empty array if no attempts yet

// Example:
const attempts = quizService.getQuizAttempts('module-1-ros2', '123456789')
console.log(attempts.length)  // 3 (user took quiz 3 times)
console.log(attempts[0].attempt_number)  // 1
console.log(attempts[2].score)  // Latest score
```

#### `saveAttempt(module_id: string, user_id: string, attempt: QuizAttempt): void`

Save quiz attempt to localStorage.

```typescript
function saveAttempt(module_id: string, user_id: string, attempt: QuizAttempt): void

// Parameters:
// - module_id (string): Module identifier
// - user_id (string): GitHub user ID
// - attempt (QuizAttempt): Completed attempt with answers, score, etc.

// Returns: void

// Side effects:
// - Appends attempt to localStorage["quizzes"][module_id].attempts[]
// - Updates last_score, best_score, total_attempts
// - Persists to localStorage

// Example:
const attempt: QuizAttempt = {
  id: 'uuid-123',
  user_id: '123456789',
  quiz_id: 'quiz-module-1',
  answers: { 'q1': 'B', 'q2': 'A', ... },
  score: 80,
  passed: true,
  // ... other fields
}
quizService.saveAttempt('module-1-ros2', '123456789', attempt)
// Attempt is now in localStorage
```

#### `getLatestScore(module_id: string, user_id: string): number | null`

Get most recent quiz score for a module.

```typescript
function getLatestScore(module_id: string, user_id: string): number | null

// Parameters:
// - module_id (string): Module identifier
// - user_id (string): GitHub user ID

// Returns: number (0-100) or null if no attempts

// Example:
const score = quizService.getLatestScore('module-1-ros2', '123456789')
console.log(score)  // 80
```

#### `getBestScore(module_id: string, user_id: string): number | null`

Get highest quiz score for a module across all attempts.

```typescript
function getBestScore(module_id: string, user_id: string): number | null

// Parameters:
// - module_id (string): Module identifier
// - user_id (string): GitHub user ID

// Returns: number (0-100) or null if no attempts

// Example:
const bestScore = quizService.getBestScore('module-1-ros2', '123456789')
console.log(bestScore)  // 85 (best score from 3 attempts)
```

---

## Data Structures

### Quiz Object (from quiz.json)

```typescript
interface Quiz {
  id: string;                    // "quiz-module-1"
  module_id: string;             // "module-1-ros2"
  title: string;                 // "ROS 2 Fundamentals Quiz"
  description: string;           // "Test your knowledge..."
  questions: QuizQuestion[];     // Array of 15 questions
  passing_score: number;         // 70 (70% required to pass)
  time_limit: number;            // 600 (10 minutes in seconds)
  metadata: {
    difficulty_distribution: {
      easy: number;              // 5
      medium: number;            // 7
      hard: number;              // 3
    };
    estimated_time: number;      // 480 (seconds)
  };
}
```

### QuizQuestion Object

```typescript
interface QuizQuestion {
  id: string;                    // "q-module1-001"
  quiz_id: string;               // "quiz-module-1"
  question_text: string;         // "What is the primary role of nodes?"
  question_type: "multiple-choice" | "true-false";
  options: {
    label: string;               // "A", "B", "C", "D"
    text: string;                // "Option text here"
  }[];
  correct_answer: string;        // "B"
  explanation: string;           // Full explanation of correct answer
  option_explanations?: {        // Why each option is right/wrong
    A: string;
    B: string;
    C: string;
    D: string;
  };
  difficulty: "easy" | "medium" | "hard";
  tags: string[];                // ["nodes", "architecture"]
}
```

### QuizAttempt Object

```typescript
interface QuizAttempt {
  id: string;                    // UUID
  user_id: string;               // GitHub user ID
  quiz_id: string;               // "quiz-module-1"
  module_id: string;             // "module-1-ros2"
  selected_question_ids: string[]; // 10 question IDs
  answers: {
    [question_id: string]: string; // Map of q_id → answer (A/B/C/D)
  };
  score: number;                 // 0-100
  passed: boolean;               // true if score >= 70
  correct_count: number;         // 0-10
  started_at: number;            // Unix timestamp
  submitted_at: number;          // Unix timestamp
  duration: number;              // Seconds taken
  attempt_number: number;        // 1, 2, 3, etc.
}
```

---

## Question Pool Rotation (Q1 Clarification)

### Algorithm

```typescript
function selectQuestions(quiz: Quiz, attemptNumber: number): QuizQuestion[] {
  // Seed random number generator with attemptNumber
  // This ensures same attempt # always gets same questions
  const seed = attemptNumber;

  // Fisher-Yates shuffle with seeded random
  const shuffled = fisherYatesShuffle(quiz.questions, seed);

  // Return first 10 questions
  return shuffled.slice(0, 10);
}

// Example seeding:
// Attempt 1 (seed=1):  questions = [q1, q3, q5, q8, q2, q12, q4, q14, q7, q11]
// Attempt 2 (seed=2):  questions = [q6, q9, q13, q15, q1, q5, q10, q3, q12, q2]
// Attempt 3 (seed=3):  questions = [q4, q7, q2, q11, q14, q1, q8, q5, q3, q15]

// Different pools for each retake ✓
```

### Benefits

- ✅ Prevents memorization (different questions each retake)
- ✅ Encourages deeper learning (students re-read for understanding)
- ✅ Maintains difficulty equivalence (all pools have 5 easy + 7 medium + 3 hard)
- ✅ Deterministic (same attempt # always gets same pool)
- ✅ Scalable (works for any pool size)

---

## Scoring Algorithm

### 100% Accuracy Required

```typescript
function scoreQuiz(attempt: QuizAttempt, selectedQuestions: QuizQuestion[]): number {
  let correctCount = 0;

  // Create lookup map for faster searching
  const questionMap = new Map();
  selectedQuestions.forEach(q => questionMap.set(q.id, q));

  // Check each answer
  for (const [questionId, userAnswer] of Object.entries(attempt.answers)) {
    const question = questionMap.get(questionId);

    if (question && question.correct_answer === userAnswer) {
      correctCount++;
    }
  }

  // Calculate percentage (always 10 questions)
  const score = Math.round((correctCount / 10) * 100);

  // Ensure score is 0-100
  return Math.max(0, Math.min(100, score));
}

// Accuracy validation:
// - 10/10 correct = 100%
// - 9/10 correct = 90%
// - 8/10 correct = 80%
// - 7/10 correct = 70% (PASS)
// - 6/10 correct = 60% (FAIL)
// - 0/10 correct = 0%
```

---

## Error Handling

### Error Cases

| Error | Cause | Recovery |
|-------|-------|----------|
| "Quiz not found" | quiz.json missing for module | Show error: "Quiz unavailable" |
| "Invalid JSON" | Malformed quiz.json | Show error: "Quiz loading failed" |
| "No questions" | Questions array empty | Show error: "Quiz incomplete" |
| "Invalid answer" | User submitted invalid option | Show error: "Invalid selection" |
| "localStorage quota exceeded" | Too much data stored | Clear old attempts; show warning |

### Error Handling Pattern

```typescript
try {
  const quiz = await quizService.loadQuiz(moduleId)
  const questions = quizService.selectQuestions(quiz, attemptNumber)
  // Continue
} catch (error) {
  if (error.message === 'Quiz not found') {
    showErrorModal('Quiz is not available for this module')
  } else if (error.message === 'Invalid JSON') {
    showErrorModal('Quiz data is corrupted. Please contact support.')
  } else {
    showErrorModal('Error loading quiz: ' + error.message)
  }
}
```

---

## Integration Points

### With Quiz Component

```typescript
// 1. Load quiz when component mounts
useEffect(() => {
  quizService.loadQuiz(moduleId).then(quiz => {
    const questions = quizService.selectQuestions(quiz, attemptNumber)
    setQuestions(questions)
  })
}, [moduleId, attemptNumber])

// 2. Validate answer as user selects
const handleAnswerChange = (questionId: string, answer: string) => {
  if (quizService.validateAnswer(answer, question)) {
    setAnswers({ ...answers, [questionId]: answer })
  }
}

// 3. Score and save when user submits
const handleSubmit = () => {
  const score = quizService.scoreQuiz(attempt, selectedQuestions)
  const passed = quizService.isPassingScore(score)
  quizService.saveAttempt(moduleId, userId, {
    ...attempt,
    score,
    passed
  })
  setResults({ score, passed })
}
```

### With Progress Service

```typescript
// After quiz completion, update progress
const score = quizService.getLatestScore(moduleId, userId)
const bestScore = quizService.getBestScore(moduleId, userId)
const attempts = quizService.getQuizAttempts(moduleId, userId).length

progressService.updateProgress(moduleId, userId, {
  quiz_score: score,
  quiz_best_score: bestScore,
  quiz_attempts: attempts
})
```

### With Results Component

```typescript
// Display past attempts
const attempts = quizService.getQuizAttempts(moduleId, userId)
attempts.forEach(attempt => {
  console.log(`Attempt ${attempt.attempt_number}: ${attempt.score}%`)
})
```

---

## TypeScript Types

```typescript
export interface Quiz {
  id: string;
  module_id: string;
  title: string;
  description: string;
  questions: QuizQuestion[];
  passing_score: number;
  time_limit: number;
  metadata: QuizMetadata;
}

export interface QuizQuestion {
  id: string;
  quiz_id: string;
  question_text: string;
  question_type: 'multiple-choice' | 'true-false';
  options: QuizOption[];
  correct_answer: string;
  explanation: string;
  option_explanations?: Record<string, string>;
  difficulty: 'easy' | 'medium' | 'hard';
  tags: string[];
}

export interface QuizAttempt {
  id: string;
  user_id: string;
  quiz_id: string;
  module_id: string;
  selected_question_ids: string[];
  answers: Record<string, string>;
  score: number;
  passed: boolean;
  correct_count: number;
  started_at: number;
  submitted_at: number;
  duration: number;
  attempt_number: number;
}

export interface QuizService {
  loadQuiz(module_id: string): Promise<Quiz>;
  selectQuestions(quiz: Quiz, attemptNumber: number): QuizQuestion[];
  scoreQuiz(attempt: QuizAttempt, selectedQuestions: QuizQuestion[]): number;
  validateAnswer(answer: string, question: QuizQuestion): boolean;
  isPassingScore(score: number): boolean;
  getQuizAttempts(module_id: string, user_id: string): QuizAttempt[];
  saveAttempt(module_id: string, user_id: string, attempt: QuizAttempt): void;
  getLatestScore(module_id: string, user_id: string): number | null;
  getBestScore(module_id: string, user_id: string): number | null;
}
```

---

## Testing Contract

### Unit Tests

```typescript
describe('QuizService', () => {
  // Loading
  test('loadQuiz() returns Quiz with 15 questions', () => {})
  test('loadQuiz() rejects if quiz.json not found', () => {})

  // Question selection (Q1)
  test('selectQuestions() returns 10 questions', () => {})
  test('selectQuestions() returns different questions per attempt', () => {})
  test('selectQuestions() returns same questions for same attempt', () => {})

  // Scoring
  test('scoreQuiz() calculates correct percentage', () => {})
  test('scoreQuiz() returns 100 for all correct', () => {})
  test('scoreQuiz() returns 0 for all incorrect', () => {})

  // Validation
  test('validateAnswer() accepts valid options (A, B, C, D)', () => {})
  test('validateAnswer() rejects invalid options', () => {})
  test('isPassingScore() returns true for score >= 70', () => {})
  test('isPassingScore() returns false for score < 70', () => {})

  // Attempts
  test('saveAttempt() persists to localStorage', () => {})
  test('getQuizAttempts() returns array of attempts', () => {})
  test('getLatestScore() returns most recent score', () => {})
  test('getBestScore() returns highest score', () => {})
})
```

### Integration Tests

```typescript
describe('Quiz Flow', () => {
  test('User can load quiz and see 10 questions', () => {})
  test('User can retake quiz and see different questions', () => {})
  test('User can complete quiz and see results', () => {})
  test('Multiple retakes stored in localStorage', () => {})
  test('Best score tracked across attempts', () => {})
})
```

---

## Implementation Checklist

- [ ] Create `src/services/quiz-service.ts` with all methods
- [ ] Create quiz.json files for all 4 modules (15 questions each)
- [ ] Create `src/components/Quiz.tsx` component
- [ ] Create `src/components/QuizResults.tsx` component
- [ ] Create `src/hooks/useQuiz.ts` (React hook wrapper)
- [ ] Implement question pool rotation algorithm
- [ ] Implement scoring algorithm (100% accuracy)
- [ ] Add localStorage persistence
- [ ] Write unit tests (80%+ coverage)
- [ ] Write integration tests (quiz flow)
- [ ] Create test questions (all 60 questions across modules)
- [ ] Test with multiple retakes
- [ ] Verify localStorage quota handling

---

**Contract Status**: Ready for Implementation | **Reference**: [data-model.md](../data-model.md#entity-4-quiz) | **Clarification**: Q1 (Pool Rotation)
