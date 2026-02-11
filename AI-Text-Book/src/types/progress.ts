export interface SectionProgress {
  section_id: string;
  status: 'not_started' | 'in_progress' | 'completed';
  scroll_percentage: number;
  time_spent: number;
  first_viewed: number;
  last_viewed: number;
}

export interface ModuleProgress {
  module_id: string;
  status: 'not_started' | 'in_progress' | 'completed';
  sections: SectionProgress[];
  overall_percentage: number;
  last_visited: number;
  quiz_attempts: string[]; // attempt IDs
  best_quiz_score?: number;
}

export interface UserProgress {
  user_id: string;
  modules: Record<string, ModuleProgress>;
  total_reading_time: number;
  total_quiz_attempts: number;
  overall_progress_percentage: number;
  last_updated: number;
}

export interface ReadingTimeData {
  content_id: string;
  estimated_minutes: number;
  word_count: number;
  calculated_at: number;
}

export interface ProgressState {
  modules: Record<string, ModuleProgress>;
  current_module?: string;
  current_section?: string;
  total_progress: number;
  is_loading: boolean;
}
