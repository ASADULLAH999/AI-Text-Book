import { useState, useCallback } from 'react';
import { QuizState, QuizResult } from '../types/quiz';

/**
 * useQuiz - Manage quiz state and logic
 */
export function useQuiz(module_id: string): {
  state: QuizState;
  currentQuestion: any | null;
  selectAnswer: (question_id: string, option_index: number) => void;
  nextQuestion: () => void;
  previousQuestion: () => void;
  submitQuiz: () => Promise<QuizResult | null>;
  resetQuiz: () => void;
} {
  const [state, setState] = useState<QuizState>({
    current_question_index: 0,
    answers: {},
    status: 'not_started',
  });

  // TODO: Load quiz data on mount

  const selectAnswer = useCallback((question_id: string, option_index: number) => {
    // TODO: Update answer state
  }, []);

  const nextQuestion = useCallback(() => {
    // TODO: Advance to next question
  }, []);

  const previousQuestion = useCallback(() => {
    // TODO: Go to previous question
  }, []);

  const submitQuiz = useCallback(async (): Promise<QuizResult | null> => {
    // TODO: Score and persist quiz attempt
    return null;
  }, []);

  const resetQuiz = useCallback(() => {
    // TODO: Reset quiz state
  }, []);

  return {
    state,
    currentQuestion: null,
    selectAnswer,
    nextQuestion,
    previousQuestion,
    submitQuiz,
    resetQuiz,
  };
}
