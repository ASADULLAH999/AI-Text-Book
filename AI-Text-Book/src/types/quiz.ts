export interface QuizQuestion {
  id: string;
  question: string;
  options: string[];
  correct_answer: number;
  explanation: string;
  difficulty: 'easy' | 'medium' | 'hard';
  category?: string;
}

export interface QuizData {
  module_id: string;
  module_name: string;
  questions: QuizQuestion[];
  passing_score: number;
  time_limit?: number;
}

export interface QuizAttempt {
  id: string;
  module_id: string;
  user_id: string;
  answers: Record<string, number>; // question_id -> selected_option_index
  score: number;
  percentage: number;
  passed: boolean;
  time_spent: number;
  start_time?: number;
  end_time?: number;
  timestamp: number;
  skipped: string[]; // question_ids that were skipped
}

export interface QuizResult {
  attempt_id: string;
  module_id?: string;
  score: number;
  percentage: number;
  passed: boolean;
  correct_count: number;
  incorrect_count: number;
  skipped_count: number;
  time_spent: number;
  correct?: number;
  details: {
    question_id: string;
    question: string;
    user_answer: number | null;
    correct_answer: number;
    correct: boolean;
    explanation: string;
  }[];
}

export interface QuizState {
  current_question_index: number;
  answers: Record<string, number>;
  status: 'not_started' | 'in_progress' | 'submitted' | 'completed';
  score?: number;
  percentage?: number;
  time_started?: number;
  time_spent?: number;
}
