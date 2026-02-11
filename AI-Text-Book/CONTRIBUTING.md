# Contributing Guide

Thank you for your interest in contributing to the Physical AI & Humanoid Robotics Interactive Textbook! This guide will help you get started.

## Code of Conduct

Be respectful and inclusive. Violations will not be tolerated.

## Getting Started

### 1. Fork and Clone

```bash
git clone https://github.com/YOUR_USERNAME/ai-textbook.git
cd ai-textbook
git remote add upstream https://github.com/anthropics/ai-textbook.git
```

### 2. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or for bug fixes
git checkout -b fix/bug-description
```

### 3. Install Dependencies

```bash
npm install
```

### 4. Set Up Environment

```bash
cp .env.example .env.local
# Add your GitHub OAuth credentials for local testing
```

## Development Workflow

### Running Tests

```bash
# Unit tests
npm run test

# Watch mode
npm run test:watch

# With coverage
npm run test:coverage

# E2E tests
npm run e2e
```

### Code Quality

```bash
# Check linting
npm run lint

# Fix linting issues
npm run lint:fix

# Format code
npm run format

# Type checking
npm run type-check
```

### Before Committing

```bash
# The pre-commit hook will automatically:
# - Run prettier on changed files
# - Run eslint --fix on TypeScript/JavaScript files
# - Prevent commits with errors

# To bypass (not recommended):
git commit --no-verify
```

## Code Style

### TypeScript

- Use strict mode (tsconfig.json configured)
- Prefer explicit types over `any`
- Use descriptive variable names
- Keep functions small and focused (< 50 lines preferred)

Example:

```typescript
// Good
interface UserProgress {
  moduleId: string;
  percentage: number;
  lastUpdated: Date;
}

function calculateProgress(sections: Section[]): number {
  const completed = sections.filter((s) => s.completed).length;
  return (completed / sections.length) * 100;
}

// Bad
function calculate(data: any[]): any {
  return (data.filter((x) => x.done).length / data.length) * 100;
}
```

### React Components

- Use functional components with hooks
- Keep components focused (< 200 lines preferred)
- Extract complex logic to custom hooks
- Use meaningful prop names
- Document props with JSDoc or TypeScript

Example:

```typescript
interface QuizProps {
  moduleId: string;
  onComplete: (score: number) => void;
}

/**
 * Quiz component - Manages quiz interaction and scoring
 * @param moduleId - ID of the module for this quiz
 * @param onComplete - Callback when quiz is submitted
 */
export function Quiz({ moduleId, onComplete }: QuizProps) {
  // Implementation
}
```

### File Organization

```
src/
├── components/
│   ├── Quiz/
│   │   ├── index.tsx
│   │   ├── Quiz.tsx
│   │   ├── QuizQuestion.tsx
│   │   ├── QuizResults.tsx
│   │   └── styles.module.css
│   └── ...
├── hooks/
│   ├── useQuiz.ts
│   ├── useAuth.ts
│   └── ...
├── services/
│   ├── quiz-service.ts
│   ├── auth-service.ts
│   └── ...
└── ...
```

## Testing Requirements

### Coverage Targets

- **Overall**: 80%+ coverage
- **Services**: 90%+ coverage
- **Components**: 80%+ coverage
- **Hooks**: 85%+ coverage

### Writing Tests

```typescript
import { render, screen } from '@testing-library/react';
import { Quiz } from './Quiz';

describe('Quiz Component', () => {
  it('renders quiz title', () => {
    render(<Quiz moduleId="module-1" onComplete={jest.fn()} />);
    expect(screen.getByText(/quiz/i)).toBeInTheDocument();
  });

  it('submits quiz and calls onComplete', async () => {
    const onComplete = jest.fn();
    render(<Quiz moduleId="module-1" onComplete={onComplete} />);
    // Test interaction
  });
});
```

## Documentation

### Commit Messages

Use conventional commits:

```
feat: add quiz retake functionality
fix: correct progress calculation formula
docs: update README with installation steps
style: format code with prettier
refactor: extract quiz logic to custom hook
test: add tests for quiz scoring
chore: update dependencies
```

### Code Comments

Comment the "why", not the "what":

```typescript
// Good
// Fisher-Yates shuffle ensures random question order per attempt
function shuffleQuestions(questions: Question[], seed: number): Question[] {
  // Implementation
}

// Bad
// Shuffle the questions
function shuffleQuestions(questions: Question[]): Question[] {
  // Implementation
}
```

### TypeScript Documentation

```typescript
/**
 * Calculate quiz score with detailed breakdown
 * @param answers - Map of question IDs to selected option indices
 * @param questions - Array of question definitions with correct answers
 * @returns QuizResult with score, percentage, and per-question details
 * @throws Error if answers don't match question IDs
 *
 * @example
 * const result = scoreQuiz(answers, questions);
 * console.log(`Score: ${result.percentage}%`);
 */
function scoreQuiz(
  answers: Record<string, number>,
  questions: QuizQuestion[]
): QuizResult {
  // Implementation
}
```

## Pull Request Process

### Before Submitting

1. **Update main branch**
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Run full test suite**
   ```bash
   npm run test:coverage
   npm run lint
   npm run type-check
   npm run e2e
   ```

3. **Build verification**
   ```bash
   npm run build
   ```

### PR Description Template

```markdown
## Description
Brief description of changes

## Related Issues
Closes #123

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation

## Testing
- [ ] Unit tests added
- [ ] Integration tests added
- [ ] E2E tests added
- [ ] Manual testing done

## Screenshots (if applicable)
<!-- Add screenshots -->

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex logic
- [ ] Documentation updated
- [ ] Tests pass locally
- [ ] Build passes
- [ ] No console warnings/errors
```

### Review Process

1. **Automatic checks**: Lint, tests, build
2. **Code review**: At least one maintainer
3. **Approval**: Required before merge
4. **Merge**: Squash commits to main

## Adding Features

### Feature Checklist

- [ ] Specification written (if major feature)
- [ ] Architecture documented
- [ ] Component structure planned
- [ ] Tests written first (TDD)
- [ ] Implementation completed
- [ ] Tests passing (80%+ coverage)
- [ ] Code reviewed
- [ ] Documentation updated
- [ ] Performance verified
- [ ] Accessibility checked

### Feature Documentation

Update docs/ and README as needed. For new components:

```markdown
## QuizResults Component

Displays quiz results with score, breakdown, and review options.

### Props
- `result` (QuizResult) - Quiz result data
- `onRetake` (function) - Callback when user clicks retake
- `onBack` (function) - Callback to return to module

### Usage
\`\`\`tsx
<QuizResults
  result={result}
  onRetake={handleRetake}
  onBack={handleBack}
/>
\`\`\`
```

## Reporting Bugs

Include:

1. **Description**: What's the bug?
2. **Steps to reproduce**: How to trigger it?
3. **Expected behavior**: What should happen?
4. **Actual behavior**: What actually happens?
5. **Screenshots**: Visual evidence
6. **Environment**: Browser, OS, Node version

## Asking Questions

Use GitHub Discussions for:

- Design questions
- Architecture discussions
- Feature requests
- General guidance

## License

By contributing, you agree your code will be licensed under MIT.

---

Thank you for contributing! 🚀
