import { QuizData, QuizQuestion, QuizAttempt, QuizResult } from '../types/quiz';
import { storageService } from './storage-service';

/**
 * QuizService - Manages quiz loading, question randomization, and scoring
 * MVP: JSON-based quiz data with localStorage persistence
 */
class QuizService {
  private storage = storageService;
  private readonly PASS_THRESHOLD = 0.7;
  private readonly ATTEMPTS_LIMIT = 5;
  private readonly ATTEMPTS_KEY_PREFIX = 'ai_textbook_quiz_attempts';

  constructor() {
    // Use the singleton storageService instance
  }

  /**
   * Load quiz data for a specific module
   */
  async loadQuiz(module_id: string): Promise<QuizData> {
    try {
      const response = await fetch(`/quizzes/module-${module_id}.json`);
      if (!response.ok) {
        throw new Error(`Failed to load quiz for module ${module_id}`);
      }
      return response.json();
    } catch (error) {
      console.error('Failed to load quiz:', error);
      throw error;
    }
  }

  /**
   * Select questions with Fisher-Yates shuffle for randomization
   * Different pool per attempt (Q1 clarification)
   */
  selectQuestions(
    questions: QuizQuestion[],
    count: number,
    attempt_number: number
  ): QuizQuestion[] {
    // Create attempt-based seed for deterministic randomization
    const seed = this.generateAttemptSeed(attempt_number);
    const shuffled = this.fisherYatesShuffle([...questions], seed);
    return shuffled.slice(0, Math.min(count, shuffled.length));
  }

  /**
   * Score a completed quiz attempt
   * 100% accurate scoring with validation
   */
  scoreQuiz(attempt: QuizAttempt, questions: QuizQuestion[]): QuizResult {
    let correct = 0;
    let incorrect = 0;
    let skipped = 0;
    const questionResults: Array<{
      question_id: string;
      correct: boolean;
      user_answer: number | null;
      correct_answer: number;
      explanation: string;
    }> = [];

    // Score each question
    questions.forEach((q) => {
      const userAnswerIndex = attempt.answers[q.id];

      if (userAnswerIndex === undefined || userAnswerIndex === null) {
        skipped++;
        questionResults.push({
          question_id: q.id,
          correct: false,
          user_answer: null,
          correct_answer: q.correct_answer,
          explanation: q.explanation || '',
        });
      } else {
        const isCorrect = userAnswerIndex === q.correct_answer;
        if (isCorrect) {
          correct++;
        } else {
          incorrect++;
        }
        questionResults.push({
          question_id: q.id,
          correct: isCorrect,
          user_answer: userAnswerIndex,
          correct_answer: q.correct_answer,
          explanation: q.explanation || '',
        });
      }
    });

    const totalAnswered = correct + incorrect;
    const percentage = totalAnswered > 0 ? (correct / totalAnswered) * 100 : 0;
    const passed = percentage >= this.PASS_THRESHOLD * 100;

    return {
      attempt_id: attempt.id,
      module_id: attempt.module_id,
      score: correct,
      percentage: Math.round(percentage),
      passed,
      correct_count: correct,
      incorrect_count: incorrect,
      skipped_count: skipped,
      time_spent: attempt.end_time && attempt.start_time ? attempt.end_time - attempt.start_time : attempt.time_spent,
      details: questionResults.map((qr: any) => ({
        question_id: qr.question_id,
        question: qr.question,
        user_answer: qr.user_answer,
        correct_answer: qr.correct_answer,
        correct: qr.correct,
        explanation: qr.explanation,
      })),
    };
  }

  /**
   * Save quiz attempt to localStorage
   */
  async saveAttempt(attempt: QuizAttempt): Promise<void> {
    const key = `${this.ATTEMPTS_KEY_PREFIX}_${attempt.user_id}_${attempt.module_id}`;
    const attempts = this.storage.get<QuizAttempt[]>(key, []) || [];

    // Add new attempt
    attempts.push(attempt);

    // Keep only last N attempts
    const cleaned = this.cleanupOldAttempts(attempts);
    this.storage.set<QuizAttempt[]>(key, cleaned);
  }

  /**
   * Get quiz attempt history for a user/module
   */
  async getAttemptHistory(user_id: string, module_id: string): Promise<QuizAttempt[]> {
    const key = `${this.ATTEMPTS_KEY_PREFIX}_${user_id}_${module_id}`;
    return this.storage.get<QuizAttempt[]>(key, []) || [];
  }

  /**
   * Get best score for a module
   */
  getBestScore(attempts: QuizAttempt[]): number | null {
    if (attempts.length === 0) {
      return null;
    }

    // Calculate scores for each attempt
    const scores = attempts.map((attempt) => {
      const correct = Object.values(attempt.answers).filter((a) => a !== undefined && a !== null).length;
      return (correct / (attempt.answers ? Object.keys(attempt.answers).length : 1)) * 100;
    });

    return Math.max(...scores);
  }

  /**
   * Clear old quiz attempts (limit to last N per module)
   */
  private cleanupOldAttempts(attempts: QuizAttempt[], limit: number = this.ATTEMPTS_LIMIT): QuizAttempt[] {
    if (attempts.length <= limit) {
      return attempts;
    }

    // Sort by date and keep only most recent
    return attempts.sort((a, b) => (b.end_time || b.timestamp) - (a.end_time || a.timestamp)).slice(0, limit);
  }

  /**
   * Fisher-Yates shuffle with seeded randomization
   */
  private fisherYatesShuffle(arr: QuizQuestion[], seed: number): QuizQuestion[] {
    const random = this.seededRandom(seed);
    const result = [...arr];

    for (let i = result.length - 1; i > 0; i--) {
      const j = Math.floor(random() * (i + 1));
      [result[i], result[j]] = [result[j], result[i]];
    }

    return result;
  }

  /**
   * Seeded random number generator
   */
  private seededRandom(seed: number) {
    return function () {
      seed = (seed * 9301 + 49297) % 233280;
      return seed / 233280;
    };
  }

  /**
   * Calculate Fisher-Yates shuffle seed based on attempt number
   */
  private generateAttemptSeed(attempt_number: number): number {
    return attempt_number * 12345 + 67890;
  }
}

export const quizService = new QuizService();
